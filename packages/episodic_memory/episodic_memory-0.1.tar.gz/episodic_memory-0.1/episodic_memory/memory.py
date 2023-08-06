# from utils import *
# from string import ascii_uppercase, ascii_lowercase
import numpy as np


class EpisodicMemory():
    """ the memory buffer for instantiated parameter vectors
        represents a "longer-term" episodic memory system
    """

    def __init__(self, min_matches, max_mismatch):
        # the number of matches required during value-based retrieval
        self.min_matches = min_matches
        self.max_mismatch = max_mismatch
        self.empty_episodes()

    def empty_episodes(self):
        self.episodes = []

    def add_episode(self, value_vector):
        # take a snapshot of the input value vector (e.g. buffer)
        self.episodes.append(value_vector)

    def organize(self):
        # e.g. consolidate the whole event at event boundary
        # remove subsets
        self.episodes = remove_subsets(self.episodes)

    def get_candidate_episodes(self, buffer_od, verbose=False):
        """ get all episodes that are consistent with the input cue
            the cue is a vector of parameter values
        """

        def num_matches(episode, buffer_od):
            """ Compute the number of matches of an input episode w.r.t
                exisiting values (belief)
            """
            # get all parameter values in the buffer
            param_vals = ['%s%s' % (param, value)
                          for param, value in buffer_od.items()]
            # compute the cardinality of their interesection
            n_match = len(set(param_vals).intersection(episode))
            return n_match

        def num_mismatches(episode, buffer_od):
            """ Compute the number values in the episode but not in the buffer
            """
            n_mismatch = 0
            # for all parameter value in the episode
            for param_val in episode:
                # # if the underlying parameter is in the buffer
                if param_val[0] in buffer_od:
                    # AND has a different value ...
                    if buffer_od[param_val[0]] != param_val[1]:
                        # increment the mismatch count
                        n_mismatch += 1
                else:
                    n_mismatch += 1
            return n_mismatch

        # # get all episodes ...
        # candidates = self.episodes
        # # satisfy minimal consistency criterion
        # candidates = [episode for episode in self.episodes
        #               if num_matches(episode, buffer_od) > self.min_matches]
        # candidates = [episode for episode in self.episodes
        #               if num_mismatches(episode, buffer_od) < self.max_mismatch]

        num_episodes = len(self.episodes)
        consistency = np.zeros((num_episodes,))
        mismatches = np.zeros((num_episodes,))
        # calculate the consistency and mismatch for all episodes
        for i in range(num_episodes):
            episode = self.episodes[i]
            consistency[i] = num_matches(episode, buffer_od)
            mismatches[i] = num_mismatches(episode, buffer_od)
            print('-- episode: %s has cons %d and mis %d' % (
                episode, consistency[i], mismatches[i]))
        candidates = [self.episodes[i] for i in range(num_episodes)
                      if (consistency[i] >= self.min_matches
                          and mismatches <= self.max_mismatch)]

        return candidates

    def print_info(self):
        print('Episodic Memory:')
        print('- Min_matches = %d' % (self.min_matches))
        print('- Max_mismatches = %d' % (self.max_mismatch))
        print('- Param vectors:')
        print(self.episodes)


""" helper functions
"""


def remove_subsets(list_of_list):
    # remove all subsets
    sets = {frozenset(e) for e in list_of_list}
    reduced_set = set()
    while sets:
        e = sets.pop()
        if any(e.issubset(s) for s in sets) \
                or any(e.issubset(s) for s in reduced_set):
            continue
        else:
            reduced_set.add(e)
    # conver to a list
    reduced_set_list = [list(item) for item in list(reduced_set)]
    return reduced_set_list


""" test
"""

# em = EpisodicMemory(min_matches=2, max_mismatch=2)
# em.add_episode(['a1', 'b1', 'c2'])
# em.organize()
# em.print_info()
