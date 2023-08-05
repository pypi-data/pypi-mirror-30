from __future__ import print_function

from helper import Helper


class Cleaner(object):
    def __init__(self, numerical_list, null_list=None):
        if null_list is None:
            null_list = ["", "null", "?"]
        self._raw_data_list = numerical_list
        self._invalid_list = null_list

    def clean(self):
        valid_list = self._get_valid_list()
        float_list = [Helper.convert_to_float(item) for item in valid_list]
        mean_value = sum(float_list) / len(float_list)
        return [Helper.convert_to_float(x) if self.is_valid_data(x) else mean_value for x in self._raw_data_list]

    def _get_valid_list(self):
        return [x for x in self._raw_data_list if self.is_valid_data(x) and Helper.is_numeric(x)]

    def is_valid_data(self, item):
        return item not in self._invalid_list


