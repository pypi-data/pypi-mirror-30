import msmbuilder
import logging
import numpy

logger = logging.getLogger(__name__)


def retrieve_MSM(model):
    """
    Retrieve a MarkovStateModel object from a model
    :param model: sklearn.pipeline.Pipeline, the model to retrieve the MSM from
    :return msm: the MarkovStateModel inside the model
    :raises ValueError: if last step of model is not from the msmbuilder.msm module
    """
    logger.info('Retrieving MSM from model')
    if 'msm' in model.named_steps.keys():
        msm = model.named_steps['msm']
    elif 'MSM' in model.named_steps.keys():
        msm = model.named_steps['MSM']
    else:
        msm = model.steps[-1]
        if not getattr(msm, '__module__').startswith(msmbuilder.msm.__name__):
            raise ValueError('Last step in the model does not belong to the msmbuilder.msm module')
    return msm


def retrieve_clusterer(model):
    """
    Retrieve a clusterer object from a model
    :param model: sklearn.pipeline.Pipeline, the model to retrieve the clusterer from
    :return clusterer: the clusterer object inside the model
    :raises ValueError: if last step of model is not from the msmbuilder.cluster module
    """
    logger.info('Retrieving clusterer from model')
    if 'clusterer' in model.named_steps.keys():
        clusterer = model.named_steps['clusterer']
    else:
        clusterer = model.steps[-2]
    if not getattr(clusterer, '__module__').startswith(msmbuilder.cluster.__name__):
        raise ValueError('Penultimate step in the model does not belong to the msmbuilder.cluster module')
    return clusterer


def retrieve_feat(model):
    """
    Retrieve a featurizer object from a model
    :param model: sklearn.pipeline.Pipeline, the model to retrieve the featurizer from
    :return feat: the featurizer object inside the model
    :raises ValueError: if last step of model is not from the msmbuilder.featurizer module
    """
    logger.info('Retrieving featurizer from model')
    if 'feat' in model.named_steps.keys():
        feat = model.named_steps['feat']
    else:
        feat = model.steps[0]
    if not getattr(feat, '__module__').startswith(msmbuilder.featurizer.featurizer.__name__):
        raise ValueError('First step in the model does not belong to the msmbuilder.featurizer module')
    return feat


def retrieve_scaler(model):
    """
    Retrieve a scaler object from a model
    :param model: sklearn.pipeline.Pipeline, the model to retrieve the scaler from
    :return scaler: the scaler object inside the model
    :raises ValueError: if last step of model is not from the msmbuilder.preprocessing module
    """
    if 'scaler' in model.named_steps.keys():
        scaler = model.named_steps['scaler']
    else:
        scaler = model.steps[1]

    if not getattr(scaler, '__module__').startswith(msmbuilder.preprocessing.__name__):
        raise ValueError('Second step in the model does not belong to the msmbuilder.preprocessing module')

    elif getattr(scaler, '__module__').startswith(msmbuilder.decomposition.__name__):
        logger.warning('Second step in model is a decomposer and not a scaler.')

    return scaler


def retrieve_decomposer(model):
    """
    Retrieve a decomposer object (tICA, PCA...) from a model
    :param model: sklearn.pipeline.Pipeline, the model to retrieve the decomposer from
    :return decomposer: the decomposer object inside the model
    :raises ValueError: if last step of model is not from the msmbuilder.decomposition module
    """
    logger.info('Retrieving decomposer from model')
    if 'tICA' in model.named_steps.keys():
        decomposer = model.named_steps['tICA']
    elif 'PCA' in model.named_steps.keys():
        decomposer = model.named_steps['PCA']
    else:
        decomposer = model.steps[2]
    if not getattr(decomposer, '__module__').startswith(msmbuilder.decomposition.__name__):
        raise ValueError('Third step in the model does not belong to the msmbuilder.decomposition module')
    return decomposer


def apply_percentile_search(count_array, percentile, desired_length, search_type='clusterer',
                            msm=None, max_iter=500, step=0.5):
    """
    Search for entries in an array whose population is below a given percentile.
    Iteratively increase or decrease the percentile until a `desired_length`
    number of entries are found.

    Parameters
    ----------
    count_array: np.array of counts in microstates.
        Shape should be equal to (n_microstates, )
    percentile: float, initial percentile to look below from
    desired_length: int, length of final list of pairs
    search_type: str, has to be 'clusterer' or 'msm'
    msm: MarkovStateModel, needed if search_type='msm'
    max_iter: int, maximum number of iterations for the search
    step: float, amount by which to increase or decrease the percentile

    Returns
    -------
    low_count_ids: list, list of indices of microstates that have low counts below the percentile
        that matches the length of desired_length
    """

    if search_type not in ['clusterer', 'msm']:
        raise ValueError('search_type is not clusterer or msm.')
    if search_type == 'msm' and msm is None:
        raise ValueError('provide a MarkovStateModel object if using msm search_type.')

    # Initiate the search for candidate frames amongst the trajectories
    logger.info('Looking for low populated microstates')
    low_count_ids = []
    iterations = 0
    while not len(low_count_ids) == desired_length:
        low_count_ids = numpy.where(
            count_array < numpy.percentile(count_array, percentile)
        )[0]  # numpy.where gives back a tuple with empty second element

        if type(low_count_ids) != list:
            low_count_ids = list(low_count_ids)

        if search_type == 'msm':
            low_cluster_ids = []
            for state_id in low_count_ids:
                # The MSM object might be built with ergodic trimming, in that case the subspace that is found
                # does not necessarily recover all the clusters in the clusterer object.
                # Therefore, the msm.mapping_ directory stores the correspondence between the cluster labels
                # in the clusterer object and the MSM object. Keys are clusterer indices, values are MSM indices.
                # If no ergodic trimming is used, the msm.mapping_ dictionary is symmetric
                for c_id, msm_id in msm.mapping_.items():
                    if msm_id == state_id:
                        low_cluster_ids.append(c_id)  # Store the cluster ID in clusterer naming
            low_count_ids = low_cluster_ids

        # Change percentile threshold to reach desired number of frames
        if len(low_count_ids) < desired_length:
            percentile += step
        if len(low_count_ids) > desired_length:
            low_count_ids = list(low_count_ids)[:desired_length]

        iterations += 1
        # Logic to stop search if we get stuck
        # This can happen if there are repeated entries all with the same minimal value
        # And the percentile keeps being shifted back and forth oscillating around the
        # value were this minimal counts are
        if (percentile > 100) or (iterations > max_iter):
            if len(low_count_ids) < desired_length:
                # This can happen if we are going to break the while loop with the percentile being lower than
                # the minimal value. In such a case, just give the entries whose values are minimal
                low_count_ids = numpy.where(
                    count_array == count_array.min()
                )[0]
            break



    # There could be a larger amount of entries in the array whose counts are all equal
    # and lower than the minimal percentile possible. In that case, the length of the low_count_ids
    # list is larger than the chosen `desired_length`. If so,  we drop elements from it
    # from the end to reduce it to be the required length
    low_count_ids = list(low_count_ids)
    if len(low_count_ids) > desired_length:
        logger.warning("""Could not find {} entries in the count array.
        Dropping {} entries from it to enforce desired length.""".format(desired_length,
                                                                  len(low_count_ids) - desired_length))
        low_count_ids = low_count_ids[:desired_length]

    return low_count_ids
