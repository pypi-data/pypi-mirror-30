from episodic_memory.utils import flatten_lists
from collections import OrderedDict


class Buffer():
    """ the memory buffer for parameter values
        represents a "short-term" memory system
    """

    def __init__(self, size):
        # the sizez of the value buffer
        self.size = size
        # maintain the content by an ordered dictionary
        self.od = OrderedDict()

    def reset(self):
        """ reset the buffer
        """
        self.od = OrderedDict()

    def load_vals(self, params_vals):
        """ Add a list of parameter values to the value buffer
            if the params_vals is a single string, convert to list
        Parameters
        ----------
        params_vals: list
            a list of parameter vales. e.g: ['a1', 'b2']
        """
        # input checking
        if type(params_vals) is str:
            params_vals = [params_vals]
        else:
            # flatten the list just in case
            params_vals = flatten_lists(params_vals)
        # loop over all param values
        for param_val in params_vals:
            self.__load_val(param_val)

    def __load_val(self, param_val):
        """ Add one parameter value to the value buffer
        Parameters
        ----------
        params_val: string
            a parameter vales. e.g: 'a1'
        """
        param, val = param_val[0], param_val[1]
        # if need to add a new value and it will cause overflow
        if not (param in self.od) and (len(self.od) + 1) > self.size:
            # remove the earlist value
            self.od.popitem(0)
        # updated it
        self.od[param] = val

    def get_all_vals(self):
        """ Get all parameter values in the buffer as a list
        """
        param_vals = ['%s%s' % (param, value)
                      for param, value in self.od.items()]
        return param_vals

    def get_all_params(self):
        """ Get all parameters in the buffer
        """
        return list(self.od.keys())

    def has_param(self, param_val):
        """ Given a parameter value,
            check if its underlying parameter exists in the value buffer
        Parameters
        ----------
        params_val: string
            a parameter vales. e.g: 'a1'

        Returns
        -------
        true if the underlying parameter exists, false otherwise
        """
        if param_val[0] in self.od:
            return True
        return False

    def print_info(self):
        print('Param value Buffer:')
        print('- Size = %d' % (self.size))
        # get the content
        if len(self.od) > 0:
            content_str = '{'
            for key, val in self.od.items():
                content_str += '%s: %s, ' % (key, val)
            content_str = content_str[:-2] + '}'
        else:
            content_str = '{}'
        print('- Content: ', content_str)


""" testing
"""
# b = Buffer(3)
# b.load_vals(['a1', 'b2'])
# b.print_info()
