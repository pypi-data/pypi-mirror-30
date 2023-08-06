from functools import reduce
import operator
import numpy as np
from string import ascii_lowercase
from itertools import product


def extract_param(episode):
    """ Given a list of parameter values, get the underlying parameters
    Parameters
    ----------
    episode: list
        parameter values, such as ['a1', 'b2']

    Returns
    -------
    param: list
        parameter vector, e.g. ['A', 'B']
    """
    if type(episode) is not list:
        episode = [episode]
    if len(episode) == 0:
        return None
    # collect the parameters
    params_list = [episode[i][0] for i in range(len(episode))]
    params = ''.join(params_list).upper()
    # params = set(params_list)
    return params


def get_set_intersection(list_i, list_j):
    """ Get the intersection set
    Parameters
    ----------
    list_i, list_j: list
        two generic lists

    Returns
    -------
    intersection_set: set
        the intersection of list_i and list_j
    """
    set_i = set(list_i)
    set_j = set(list_j)
    intersection_set = set_i.intersection(set_j)
    return intersection_set


def flatten_lists(lists):
    """ Convert a list of lists to a list (reduce list-depth by 1)
    Parameters
    ----------
    lists: list
        a list of lists

    Returns
    -------
    lists: list
        a list of the "internal items"
    """
    if len(lists) == 0:
        return []
    if type(lists[0]) is list:
        return reduce(operator.add, lists)
    return lists


# def attach_suffix(item_list, suffix):
#     """ add a int suffix to a parameter vector
#         letter representation of the parameter
#     """
#     vals = []
#     # generate instantiation of the underlying parameter
#     for item in item_list:
#         vals.append(item.lower() + '%d' % (suffix))
#     return vals

def attach_suffix(item_list, suffix):
    """ add a int suffix to a parameter vector
        int representation of parameters
    """
    vals = []
    # generate instantiation of the underlying parameter
    for item in item_list:
        vals.append([int(item), int(suffix)])
    return vals


def val_to_one_hot_vec(value, k):
    """ convert a input value to a 1 hot vector
    Parameters
    ----------
    value: string
        a event value, such as 'a1'
    k: int
        the dimension of the one hot vector
    Returns
    -------
    one_hot_vector : 1d-array with size (k,)
    """
    index = int(value[1])
    one_hot_vector = np.zeros((k,))
    if index > k:
        raise ValueError('value index cannot be larger than K')
    if index == 0:
        return one_hot_vector
    # use one-based index
    one_hot_vector[index-1] = 1
    return one_hot_vector


def vals_to_one_hot_vecs(values, k, value_set=list(ascii_lowercase)):
    """ Make the implicit assumption that the domain of value is all letters
    Parameters
    ----------
    values: list of strings
        some event values, such as ['a1', 'b2', 'c0']
    k: int
        the dimension of "sub" one-hot vector
    Returns
    -------
    one_hot_vector : 1d-array with size (k * |value_set|,)
    """
    num_elements = len(ascii_lowercase)
    full_dim = num_elements * k
    full_one_hot_vec = np.zeros((full_dim, ))
    # fill in all values
    for val in values:
        # compute the support for the currenet value
        start_idx = value_set.index(val[0]) * k
        end_idx = start_idx + k
        # fill in the value with one hot representations
        sub_one_hot_vec = val_to_one_hot_vec(val, k)
        full_one_hot_vec[start_idx:end_idx] = sub_one_hot_vec
    return full_one_hot_vec


def remove_repeated_list(ll):
    set_of_list = list()
    for sublist in ll:
        if sublist not in set_of_list:
            set_of_list.append(sublist)
    return set_of_list


def intersection_ll(ll1, ll2):
    intersection_list = []
    for list_l1 in ll1:
        if list_l1 in ll2:
            intersection_list.append(list_l1)
    return intersection_list


def compute_ll_overlap(lll):
    """
    input: list of lists of lists
    """
    n_ll = len(lll)
    overlap_map = np.zeros((n_ll, n_ll))
    for i, j in product(range(n_ll), range(n_ll)):
        sit_intersection = intersection_ll(lll[i], lll[j])
        overlap_map[i, j] = len(sit_intersection)
    return overlap_map


""" simple helper functions
"""


def print_list(input_list):
    for item in input_list:
        print(item)


def print_dict(input_dict):
    for val, item in input_dict.items():
        print(val, item)


def letter2num(letter):
    """ map a-z to 0-25
    """
    letter = letter.lower()
    number = ord(letter) - ord('a')
    return number


def letters2nums(letters):
    return [letter2num(letters[i]) for i in range(len(letters))]
