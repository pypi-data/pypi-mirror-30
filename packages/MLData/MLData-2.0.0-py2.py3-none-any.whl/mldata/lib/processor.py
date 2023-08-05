from __future__ import print_function
from helper import Helper
import pandas as pd

from mldata.lib.category_converter import CategoryConverter
from mldata.lib.normalizer import Normalizer


class Processor(object):
    def __init__(self, csv_file_path, target_column, exclude_column_list=None, category_list=None, positive_tag=1,
                 csv_header=0, invalid_values=None):
        if exclude_column_list is None:
            exclude_column_list = []
        self._exclude_column_list = exclude_column_list
        if category_list is None:
            category_list = []
        if invalid_values is None:
            invalid_values = []
        self._csv_file_path = csv_file_path
        self._target_column = target_column
        self._category_column_list = category_list
        self._positive_tag = positive_tag
        self._csv_header = csv_header
        self._raw_data = pd.read_csv(self._csv_file_path, header=self._csv_header)
        self._header = self._raw_data.columns.values.tolist()
        self._invalid_values = invalid_values
        print("headers: %s" % str(self._header))
        # check parameters, if failed will throw illegal parameter exception
        self._check_parameters()

    def _check_parameters(self):
        if not Helper.is_file_exist(self._csv_file_path):
            raise ValueError("CSV file %s not exist!" % self._csv_file_path)
        if self._target_column not in self._header:
            raise ValueError("target column %s not exist in excel header" % self._target_column)

    def _get_numerical_column_list(self):
        return set(self._header) - {self._target_column} - set(self._exclude_column_list) \
                   - set(self._category_column_list)

    def normalize(self):
        for category_column in self._category_column_list:
            print("starting normalize %s" % category_column)
            self._raw_data[category_column] = self._normalize_category_column(category_column)
        for numerical_column in self._get_numerical_column_list():
            print("starting normalize %s" % numerical_column)
            self._raw_data[numerical_column] = self._normalize_numerical_column(numerical_column)

    def _normalize_numerical_column(self, numerical_column):
        column_value_list = self._raw_data[numerical_column].values.tolist()
        return Normalizer(column_value_list, self._invalid_values).normalize_numerical_value()

    def _normalize_category_column(self, category_column):
        column_value_list = self._raw_data[category_column].values.tolist()
        target_list = self._raw_data[self._target_column].values.tolist()
        numerical_list = CategoryConverter(column_value_list, target_list, self._positive_tag).convert()
        return Normalizer(numerical_list, self._invalid_values).normalize_numerical_value()

    def save_to_file(self, new_file_name):
        self._raw_data.to_csv(new_file_name, index=False)
