from unittest import TestCase

from mldata.lib.helper import Helper
from mldata.lib.processor import Processor


class TestProcessor(TestCase):
    def test_normalize(self):
        print("start test normalize")
        new_file_path = "outputs/new.csv"
        processor = Processor("resource/raw_dataset.csv", target_column="APPROVE/NOT", exclude_column_list=["id"],
                              category_list=["Work Class", "FnlWgt", "Education", "Maried Status", "Occupation",
                                             "Relationship", "Race", "Gender", "Native Country", "Flag"],
                              invalid_values=["?", "", "null", None],
                              positive_tag=1)
        processor.normalize()
        processor.save_to_file(new_file_path)
        self.assertTrue(Helper.is_file_exist(new_file_path))



