import unittest

from seaborn_timestamp.timestamp import TIMESTAMP_FORMAT, \
    datetime_to_str, str_to_datetime
import datetime


class TestTimestamp(unittest.TestCase):
    def test_str_to_datetime(self):
        date = str_to_datetime("2018-03-31_18:22:47.012")
        self.assertEqual(date.month, 3)
        self.assertEqual(date.day, 31)
        self.assertEqual(date.weekday(), 5)
        self.assertEqual(date.year, 2018)

    def test_datetime_to_str(self):
        render = datetime_to_str(
            datetime.datetime(2018, 3, 31, 18, 22, 47, 12000))
        self.assertEqual(render, "2018-03-31_18:22:47.012")
