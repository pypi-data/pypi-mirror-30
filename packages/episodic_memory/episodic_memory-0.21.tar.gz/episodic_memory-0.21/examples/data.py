import numpy as np
from math import factorial
from itertools import permutations


def get_datas_ohv(n_params, n_branches, event_len, num_data):
    X_list = []
    Y_list = []
    for i in range(num_data):
        X, Y, _, _ = get_data(n_params, n_branches, event_len)
        X_list.append(X)
        Y_list.append(Y)
    X_list = np.array(X_list)
    Y_list = np.array(Y_list)
    return X_list, Y_list


def get_data(n_params, n_branches, event_len):
    # prepare for the training data
    event_info = event_gen(n_params, n_branches, event_len, True)
    obs_params, obs_branch_ids, obs_ohvs, _, pred_branch_ids, _ = event_info
    # combine the observations to list form
    obs = [[param, branch_id]
           for param, branch_id in zip(obs_params, obs_branch_ids)]
    pred = obs[::-1]
    # get X and Y matrices
    X = obs_ohvs
    Y = [val2ohv_y(pred_branch_ids[s], n_branches)
         for s in range(len(pred_branch_ids))]
    return X, Y, obs, pred


def event_gen(n_params, n_branches, event_len, repeat=False):
    """ generate a sequence of observation and a reversed seq
        with one hot vector form
        - e.g. a1, b2, c1, ... d2
    """
    # generate a sequence of observations
    obs_params = np.random.choice(
        np.arange(n_params), event_len, replace=False)
    # generate the branch index
    obs_branch_ids = 1 + np.random.choice(
        np.arange(n_branches), event_len)
    # convert to one hot vector representation
    obs_ohvs = [val2ohv(obs_params[s], obs_branch_ids[s], n_params, n_branches)
                for s in range(event_len)]
    # generate the prediciton values
    pred_params = obs_params[::-1]
    pred_branch_ids = obs_branch_ids[::-1]
    pred_ohvs = obs_ohvs[::-1]
    # repeat the event (movie 2nd half)
    if repeat:
        n_repeats = 2
        obs_params = np.tile(obs_params, n_repeats)
        obs_branch_ids = np.tile(obs_branch_ids, n_repeats)
        pred_params = np.tile(pred_params, n_repeats)
        pred_branch_ids = np.tile(pred_branch_ids, n_repeats)
        obs_ohvs = np.vstack([obs_ohvs, obs_ohvs])
        pred_ohvs = np.vstack([pred_ohvs, pred_ohvs])
    else:
        obs_ohvs = np.array(obs_ohvs)
        pred_ohvs = np.array(pred_ohvs)
    return obs_params, obs_branch_ids, obs_ohvs,\
        pred_params, pred_branch_ids, pred_ohvs


def val2ohv(param_val, branch_id, n_params, n_branches):
    """ conver a param val and a branch index (e.g. {2, 1})
        to a one hot vector
    """
    ohv = np.zeros((n_params * n_branches,))
    ohv[param_val * n_branches + branch_id-1] = 1
    return ohv


def val2ohv_y(branch_id, n_branches):
    """ convert pred_branch_ids to Y
    """
    ohv = np.zeros((n_branches,))
    ohv[branch_id-1] = 1
    return ohv


"""helper function """


def check_train_test_overlap(X_test, X_train):
    """ check how many test set example is in the training set
    """
    # check if any test set data is in the training set
    count = 0
    for i, j in product(range(len(X_train)), range(len(X_test))):
        if np.allclose(X_train[i], X_test[j]):
            count += 1
    return count
