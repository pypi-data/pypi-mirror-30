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
        if not value_vector in self.episodes:
            self.episodes.append(value_vector)

    def get_candidate_episodes(self, buffer_od, verbose=False):
        """ get all episodes that are consistent with the input cue
            the cue is a vector of parameter values
        """
        # preallocate measures for all episodes
        num_episodes = len(self.episodes)
        consistency = np.zeros((num_episodes,))
        mismatches = np.zeros((num_episodes,))
        # calculate the consistency and mismatch for all episodes
        for i in range(num_episodes):
            episode = self.episodes[i]
            consistency[i] = self._num_matches(episode, buffer_od)
            mismatches[i] = self._num_mismatches(episode, buffer_od)
            print('-- episode: %s has cons %d and mis %d' % (
                episode, consistency[i], mismatches[i]))
        candidates = [self.episodes[i] for i in range(num_episodes)
                      if (consistency[i] >= self.min_matches
                          and mismatches[i] <= self.max_mismatch)]
        # "best" episodic maximize {consistency - mismatches}
        best_episode = None
        if len(candidates) > 0:
            best_episode = candidates[np.argmax(consistency - mismatches)]
        return candidates, best_episode

    def _num_matches(self, episode, buffer_od):
        """ Compute the number of matches of an input episode w.r.t
            exisiting values (belief)
        """
        param_vals = [[param, val] for param, val in list(buffer_od.items())]
        n_matches = intersection_ll(episode, param_vals)
        return n_matches

    def _num_mismatches(self, episode, buffer_od):
        """ Compute the number values in the episode differ from the buffer
        """
        n_mismatch = 0
        for param, val in episode:
            if param in buffer_od and buffer_od[param] != val:
                n_mismatch += 1
        return n_mismatch

    # def _num_missing(self, episode, buffer_od):
    #     """ Compute the number values in the episode missing from the buffer
    #     """
    #     n_missing = 0
    #     for param, val in episode:
    #         if not param in buffer_od:
    #             n_missing += 1
    #     return n_missing

    def __repr__(self):
        info = 'Episodic Memory:\n'
        info += '- Min_matches = %d\n' % (self.min_matches)
        info += '- Max_mismatches = %d\n' % (self.max_mismatch)
        info += '- Param vectors:\n%s' % (self.episodes)
        return info


""" helper functions
"""


def intersection_ll(ll1, ll2):
    """ compute the intersection between two list of lists
    """
    assert type(ll1) == list
    assert type(ll2) == list
    counts = 0
    for list_i in ll1:
        if list_i in ll2:
            counts += 1
    return counts


# """ testing
# """
# event = [[6, 2],
#          [2, 1],
#          [1, 1],
#          [7, 2],
#          [3, 1],
#          [0, 1],
#          [5, 1],
#          [4, 1],
#          [6, 2],
#          [2, 1],
#          [1, 1],
#          [7, 2],
#          [3, 1],
#          [0, 1],
#          [5, 1],
#          [4, 1]]
# from episodic_memory.buffer import Buffer
# b = Buffer(3)
# b.load_vals(event)
# b
#
# episode1 = [
#     [3, 1],
#     [0, 1],
#     [5, 1]
# ]
# episode2 = [
#     [1, 1],
#     [7, 2],
#     [3, 1]
# ]
# em = EpisodicMemory(min_matches=2, max_mismatch=2)
# em.empty_episodes()
# em.add_episode(episode1)
# em.add_episode(episode2)
# em.get_candidate_episodes(b.od)
