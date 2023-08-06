import numpy as np
from episodic_memory.utils import flatten_lists, attach_suffix, \
    get_set_intersection
from string import ascii_uppercase


class World():
    def __init__(self, param_vec_dim, num_ongoing_vecs, max_realization_idx,
                 param_vecs=None):
        # TODO if param_vecs is provided, should check consistency
        # the dimension of the parameter vector
        self.param_vec_dim = param_vec_dim
        # the number of ongoing parameter vectors
        self.num_ongoing_vecs = num_ongoing_vecs
        # the number of possible realizations of any parameter (0=UNK)
        self.max_realization_idx = max_realization_idx
        # if no pre-defined param_vecs, take random samples
        if param_vecs == None:
            self.__initialize_param_vectors()
        else:
            # a list of parameter vectors
            self.param_vecs = param_vecs
        self.clear()

    def __initialize_param_vectors(self):
        max_shifts = 1
        _, param_vecs_with_shift_s = gen_param_vecs(self.param_vec_dim, False)
        vec_set = select_param_vecs_with_shift_s(
            param_vecs_with_shift_s, max_shifts)
        self.param_vecs = vec_set

    def initialize_situations(self, num_events, verbose=False):
        """ initialize the world with vector/value sources
        """
        if num_events < 0:
            raise ValueError('num_events and event_length are natural numbers')
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

    def __sample_latent_causes(self, verbose=False):
        """ randomly sample some parameter vectors
            instantiate the vectors
        """
        # sample some vectors as the source
        num_param_vecs = len(self.param_vecs)
        params_indices = np.random.choice(
            num_param_vecs, size=self.num_ongoing_vecs, replace=False, p=None)
        vec_source = [self.param_vecs[i] for i in params_indices]
        # instantiate the parameter vector sets
        val_source_lists = self.__instantiate_vec_source(vec_source)
        # construct a situation
        situation = flatten_lists(val_source_lists)
        situation = sorted(list(set(situation)))

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
        """ get a random index for the episodes, avoid zero
        """
        suffix = np.random.choice(
            np.arange(self.max_realization_idx), size=1, replace=True) + 1
        return suffix

    def print_info(self):

        def compute_source_overlap():
            n_sources = len(self.situations)
            overlap_heatmap = np.zeros((n_sources, n_sources))
            for i in range(n_sources):
                for j in range(n_sources):
                    overlap_heatmap[i, j] = len(get_set_intersection(
                        self.situations[i], self.situations[j]))
            return overlap_heatmap

        print('--- WORLD INFO ---')
        print('Number of ongoing vectors: %s' % self.num_ongoing_vecs)
        print('Parameter vector dimension: %s' % self.param_vec_dim)
        print('All param vectors: ', self.param_vecs)
        if self.num_events == 0:
            return
        print('Event parameters:')
        for i in range(self.num_events):
            print('- Situation %d:' % i)
            print('-- Vecs:', self.vec_sources[i])
            print('-- Vals:', self.val_sources[i])

        overlap_heatmap = compute_source_overlap()
        print('-- situation overlapmap: \n', overlap_heatmap)
        print('\n')


def gen_param_vecs(param_dim, verbose=False):
    """ generate parameter vectors (consecutive letters)
    """
    max_overlap_num = param_dim - 1
    params_set = ascii_uppercase
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


# def instantiate_param_vecs(vec_set, max_realization_idx):
#     """ instantiate a set of parameter vectors with shifts
#     """
#     # instantiate all vectors with all possible realization indices
#     instantiated_vec_set = []
#     for param_vector in vec_set:
#         instantiated_vec = [attach_suffix(param_vector, idx + 1)
#                             for idx in range(max_realization_idx)]
#         instantiated_vec_set.append(instantiated_vec)
#     return instantiated_vec_set


""" demos """


def get_naive_param_vec_set():
    mid_pt = 13
    param_vecs = [[ascii_uppercase[i] for i in range(mid_pt)],
                  [ascii_uppercase[i+mid_pt]
                   for i in range(len(ascii_uppercase) - mid_pt)]
                  ]
    return param_vecs


""" example 1: how to use
"""
# # world constants
# param_vec_dim = 4
# num_ongoing_vecs = 4
# max_realization_idx = 2
# # event constants
# num_events = 2
# event_length = 10
#
# w0 = World(param_vec_dim, num_ongoing_vecs, max_realization_idx)
# w0.print_info()
# w0.initialize_situations(num_events, event_length)
# w0.print_info()


""" example 2: naive World
    non-overlapping event structure
    number of ongoing vector = 1
"""
# naive_param_vecs = get_naive_param_vec_set()
# # constants
# param_vec_dim = len(naive_param_vecs[0])
# max_realization_idx = 1
# num_ongoing_vecs = 1
# num_events = 1
# event_length = 30
#
# # set up world 0
# w0 = World(param_vec_dim, num_ongoing_vecs, max_realization_idx,
#            [naive_param_vecs[0]])
# # w0.print_info()
# w0.initialize_situations(num_events)
# w0.print_info()
#
# # set up world 1
# w1 = World(param_vec_dim, num_ongoing_vecs, max_realization_idx,
#            [naive_param_vecs[1]])
# # w1.print_info()
# w1.initialize_situations(num_events)
# w1.print_info()
#
# # make events
# obs_seq0, pred_seq0 = w0.make_event_seq(event_length)
# obs_seq1, pred_seq1 = w1.make_event_seq(event_length)
# print(obs_seq0)
# print(obs_seq1)
