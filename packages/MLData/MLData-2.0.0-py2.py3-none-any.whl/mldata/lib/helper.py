import os.path as path
import pandas


class Helper(object):
    @staticmethod
    def is_file_exist(file_path):
        return path.exists(file_path)

    @staticmethod
    def read_csv_file(file_path):
        return pandas.read_csv(file_path)

    @staticmethod
    def is_numeric(item):
        try:
            float(item)
            return True
        except ValueError:
            return False

    @staticmethod
    def convert_to_float(item):
        return float(item)
