import unittest
import datetime

import jma

class JmaTestCase(unittest.TestCase):
    """Jma test cases."""

    def setUp(self):
        """Setup."""
        self.jma = jma.Jma()
        self.prec_no = "51"
        self.block_no = "47636"
        self.year = 2018
        self.month = 9
        self.day = 28
        self.sation_type = "s"

    def tearDown(self):
        """Teardown."""
        pass

    def test_get_prefectures(self):
        self.assertEqual(len(self.jma.get_prefectures()), 61)

    def test_get_stations(self):
        self.assertEqual(len(self.jma.get_stations(self.prec_no)), 24)

    def test_get_ten_minutely_data(self):
        i = 1
        for data in self.jma.get_ten_minutely_data(self.prec_no, self.block_no, self.sation_type, self.year, self.month, self.day):
            self.assertEqual(datetime.datetime(self.year, self.month, self.day) + datetime.timedelta(minutes=10 * i), data.dt)
            i += 1

    def test_get_hourly_data(self):
        i = 1
        for data in self.jma.get_hourly_data(self.prec_no, self.block_no, self.sation_type, self.year, self.month, self.day):
            self.assertEqual(datetime.datetime(self.year, self.month, self.day) + datetime.timedelta(hours = i), data.dt)
            i += 1

if __name__ == '__main__':
    unittest.main()
