import numpy as np
from episodic_memory.utils import flatten_lists, attach_suffix, \
    remove_repeated_list, intersection_ll, compute_ll_overlap
from string import ascii_uppercase
import sys


class World():
    def __init__(self, param_vec_dim, num_ongoing_vecs, num_branches,
                 param_vecs=None):
        # TODO if param_vecs is provided, should check consistency
        # the dimension of the parameter vector
        self.param_vec_dim = param_vec_dim
        # the number of ongoing parameter vectors
        self.num_ongoing_vecs = num_ongoing_vecs
        # the number of possible realizations of any parameter (0=UNK)
        self.num_branches = num_branches
        # if no pre-defined param_vecs, take random samples
        if param_vecs == None:
            self.__initialize_param_vectors()
        else:
            # a list of parameter vectors
            self.param_vecs = param_vecs
        self.clear()

    def __initialize_param_vectors(self):
        max_shifts = 1
        _, param_vecs_with_shift_s = gen_param_vecs(self.param_vec_dim)
        vec_set = select_param_vecs_with_shift_s(
            param_vecs_with_shift_s, max_shifts)
        self.param_vecs = vec_set

    def initialize_situations(self, num_events, verbose=False):
        """ initialize the world with vector/value sources
        """
        if num_events < 0:
            raise ValueError('num_events and event_length are natural numbers')
        self.clear()
        self.num_events = num_events
        for i in range(num_events):
            situation = self.__sample_latent_causes(verbose)
            self.situations.append(situation)

    def clear(self):
        """ clear the situation depended stuff
        """
        self.num_events = 0
        self.situations = []
        self.val_sources = []
        self.vec_sources = []

    def make_event_seq(self, event_length, verbose=False):
        """ make a sequence of events
        """
        if len(self.situations) == 0:
            raise ValueError('You need to init the world 1st!')
        if verbose:
            print('--- EVENT SEQ ---')
        event_seq = []
        pred_seq = []
        # sample {observation, prediction} pair, sequentially
        for i in range(self.num_events):
            val_source = self.situations[i]
            events, preds = self.__sample_event(val_source, event_length)
            # collect the samples
            event_seq += events
            pred_seq += preds
        if verbose:
            print('\n')
        return event_seq, pred_seq

    def __sample_event(self, val_source, event_length, noise_p=0,
                       verbose=False):
        """ randomly sample an event
        """

        def sample_value_source(val_source):
            """ generate a sample from a set of values
            """
            temp_indices = np.random.choice(
                len(val_source), size=event_length, replace=True, p=None)
            value_seq = [val_source[i] for i in temp_indices]
            return value_seq

        event_seq = sample_value_source(val_source)
        pred_seq = sample_value_source(val_source)
        return event_seq, pred_seq

    def __sample_latent_causes(self, verbose=True):
        """ randomly sample some parameter vectors
            instantiate the vectors
        """
        # sample some vectors as the source
        num_param_vecs = len(self.param_vecs)
        selected_param_ids = np.random.choice(
            num_param_vecs, size=self.num_ongoing_vecs, replace=False, p=None)
        vec_source = [self.param_vecs[i] for i in selected_param_ids]
        # instantiate the parameter vector sets
        val_source_lists = self.__instantiate_vec_source(vec_source)
        # construct a situation by combining all value vectors
        situation = flatten_lists(val_source_lists)
        situation = remove_repeated_list(situation)

        # take a snapshot for display purpose
        self.vec_sources.append(vec_source)
        self.val_sources.append(val_source_lists)
        if verbose:
            print('%s:\n- %s' % (sorted(vec_source), val_source_lists))
        return situation

    def __instantiate_vec_source(self, vec_source):
        """ instantiate a set of parameter vectors, avoid conflicting values
        """
        num_vecs = len(vec_source)
        val_source = []
        value_suffix = []
        # process the 1st parameter vector
        value_suffix.append(self.__get_random_suffix())
        values = attach_suffix(vec_source[0], value_suffix[0])
        val_source.append(values)
        # process the rest
        for i in np.arange(1, num_vecs, 1):
            # look at all previous vectors
            has_shared_params = False
            for j in range(i):
                # if there is shared parameter...
                if len(set(vec_source[j]).intersection(vec_source[i])) > 0:
                    # then use the same suffix to avoid conflict
                    has_shared_params = True
                    value_suffix.append(value_suffix[j])
                    values = attach_suffix(vec_source[i], value_suffix[j])
                    val_source.append(values)
                    break
            if not has_shared_params:
                # otherwise, it is okay a random suffix
                value_suffix.append(self.__get_random_suffix())
                values = attach_suffix(vec_source[i], value_suffix[i])
                val_source.append(values)
        return val_source

    def __get_random_suffix(self):
        """Get a random index for the episodes (= the choice of branch)
        """
        # plus 1 to avoid zero
        suffix = np.random.choice(
            np.arange(self.num_branches), size=1, replace=True) + 1
        return suffix

    def __repr__(self):
        info = '--- WORLD INFO ---\n'
        info += 'Number of ongoing vectors: %s\n' % self.num_ongoing_vecs
        info += 'Parameter vector dimension: %s\n' % self.param_vec_dim
        info += 'All param vectors: %s\n' % self.param_vecs
        if self.num_events == 0:
            return info
        for i in range(self.num_events):
            info += '- Situation: %d\n' % (i)
            info += '-- Vecs: %s\n' % (self.vec_sources[i])
            info += '-- Vals: %s\n' % (self.val_sources[i])
        overlap_heatmap = compute_ll_overlap(self.situations)
        info += '-- situation overlapmap: \n%s' % (overlap_heatmap)
        return info


""" helper function """

DEFAULT_PARAMS_SET = np.arange(1, 27, 1)


def gen_param_vecs(param_dim, params_set=DEFAULT_PARAMS_SET, verbose=False):
    """ generate parameter vectors (consecutive letters)
    """
    max_overlap_num = param_dim - 1
    num_params = len(params_set)
    # preallocate
    all_param_vecs = []
    overlap_param_vecs = dict()
    # get all possble param vectors
    for i in range(len(params_set) - param_dim):
        param_vec = [params_set[j] for j in np.arange(i, i + param_dim)]
        all_param_vecs.append(param_vec)
    # loop over all shifts
    for s in range(max_overlap_num + 1):
        # get param vecs with shift s (these vecs over lap with the s0 set)
        K = int(num_params / param_dim) - s
        overlap_param_vecs[s] = [all_param_vecs[s + param_dim * k] for k in range(K)]
    if verbose:
        print_dict(overlap_param_vecs)
    return all_param_vecs, overlap_param_vecs


def select_param_vecs_with_shift_s(param_vecs_with_shift_s, max_shifts):
    # collect all vectors with different number of shifts
    vec_set = []
    for s in range(max_shifts):
        vec_set += param_vecs_with_shift_s[s]
    return vec_set


# """ demos """

# """ example 1: how to use
# """
# # world constants
# param_vec_dim = 4
# num_ongoing_vecs = 4
# num_branches = 2
# # event constants
# num_events = 2
# event_length = 10
#
# w0 = World(param_vec_dim, num_ongoing_vecs, num_branches)
# w0
#
# w0.initialize_situations(num_events, event_length)
# w0
# w0.make_event_seq(event_length)

#
# """ example 2: naive World
#     non-overlapping event structure
#     number of ongoing vector = 1
# """
# naive_param_vecs = [[(i+1) for i in range(10)], [(i+11) for i in range(10)]]
# # constants
# param_vec_dim = len(naive_param_vecs[0])
# num_branches = 2
# num_ongoing_vecs = 1
# num_events = 1
# event_length = 30
#
# # set up world 0
# w0 = World(param_vec_dim, num_ongoing_vecs, num_branches,
#            [naive_param_vecs[0]])
# w0.initialize_situations(num_events)
# w0
#
# # set up world 1
# w1 = World(param_vec_dim, num_ongoing_vecs, num_branches,
#            [naive_param_vecs[1]])
# w1.initialize_situations(num_events)
# w1
#
# # make events
# obs_seq0, pred_seq0 = w0.make_event_seq(event_length)
# obs_seq1, pred_seq1 = w1.make_event_seq(event_length)
# print(obs_seq0)
# print(obs_seq1)
