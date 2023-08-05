from mldata.lib.helper import Helper
from unittest import TestCase


class TestHelper(TestCase):
    def test_is_number(self):
        self.assertTrue(Helper.is_numeric(1))
        self.assertTrue(Helper.is_numeric(1.000000))
        self.assertFalse(Helper.is_numeric("12"))

    def test_read_csv_file(self):
        raw_data = Helper.read_csv_file("resource/raw_dataset.csv")
        print(raw_data.columns)
        print(raw_data['APPROVE/NOT'])
