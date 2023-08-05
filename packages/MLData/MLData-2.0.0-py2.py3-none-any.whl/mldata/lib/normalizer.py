from __future__ import print_function

from numpy import sqrt, fabs

from mldata.lib.cleaner import Cleaner
from mldata.lib.helper import Helper


class Normalizer(object):
    def __init__(self, numerical_list, invalid_list):
        # start with parameter check
        self._parameter_check(numerical_list, invalid_list)
        self._raw_data_list = self.clean_list(numerical_list, invalid_list)
        self._length = len(self._raw_data_list)
        self._sum = sum(self._raw_data_list)
        self._mean = self._sum / self._length

    @staticmethod
    def clean_list(numerical_list, invalid_list):
        # return a list all elements are numerical
        return Cleaner(numerical_list, invalid_list).clean()

    @staticmethod
    def _parameter_check(numerical_list, invalid_list):
        for item in numerical_list:
            if item not in invalid_list and not Helper.is_numeric(item):
                raise ValueError("Item %s not numerical, all data in list should be numerical" % str(item))

    def normalize_numerical_value(self):
        norm_list = [(x - self._mean) / self.compute_std() for x in self._raw_data_list]
        return [x if -4 <= x <= 4 else 4 * x / abs(x) for x in norm_list]

    def compute_std(self):
        sum_x = self._sum
        sum_x_2 = sum([x * x for x in self._raw_data_list])
        return sqrt(fabs(sum_x_2 - sum_x * sum_x / self._length) / (self._length - 1))
