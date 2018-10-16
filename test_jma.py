import unittest
import datetime

import jma

class JmaTestCase(unittest.TestCase):
    """Jma test cases."""


    def setUp(self):
        """Setup."""
        self.jma = jma.Jma()
        self.prec_no = "51" #愛知県
        self.block_no_nagoya = "47636" #名古屋
        self.block_no_okazaki = "0467" #岡崎
        self.year = 2018
        self.month = 9
        self.day = 28

    def tearDown(self):
        """Teardown."""
        pass

    # 都道府県を取得してその数をテスト
    def test_get_prefectures(self):
        NUMBER_OF_PREFECTURES = 61
        num_of_prefectures = 0
        for prefecture in self.jma.get_prefectures():
            num_of_prefectures += 1
        self.assertEqual(num_of_prefectures, NUMBER_OF_PREFECTURES)

    # 愛知県のstations数を取得してその数をテスト
    def test_get_stations(self):
        NUMBER_OF_STATIONS_IN_AICHI = 24
        num_of_stations = 0
        for station in self.jma.get_stations(self.prec_no):
            num_of_stations += 1
        self.assertEqual(num_of_stations, NUMBER_OF_STATIONS_IN_AICHI)

    # 10分計測値
    def test_nagoya_get_ten_minutely_data(self):
        i = 1
        for data in self.jma.get_ten_minutely_data(self.prec_no, self.block_no_nagoya, self.year, self.month, self.day):
            self.assertEqual(datetime.datetime(self.year, self.month, self.day) + datetime.timedelta(minutes=10 * i), data.dt)
            i += 1

    # 1時間計測値
    def test_nagoya_get_hourly_data(self):
        i = 1
        for data in self.jma.get_hourly_data(self.prec_no, self.block_no_nagoya, self.year, self.month, self.day):
            self.assertEqual(datetime.datetime(self.year, self.month, self.day) + datetime.timedelta(hours=i), data.dt)
            i += 1

    #不正なprec_no
    def test_get_hourly_data_with_invalid_prec_no(self):
        INVALID_PREC_NO = '999'
        with self.assertRaises(jma.InvalidPrecNo):
            for data in self.jma.get_hourly_data(INVALID_PREC_NO, self.block_no_nagoya, self.year, self.month, self.day):
                # do something
                pass

    # 不正なblock_no
    def test_get_hourly_data_with_invalid_block_no(self):
        INVALID_BLOCK_NO = '99999'
        with self.assertRaises(jma.InvalidBlockNo):
            for data in self.jma.get_hourly_data(self.prec_no, INVALID_BLOCK_NO, self.year, self.month, self.day):
                # do something
                pass

    # 未来の日付
    def test_get_hourly_data_with_future_date(self):
        # 2100年1月1日のデータをget
        with self.assertRaises(jma.FutureDateError):
            for data in self.jma.get_hourly_data(self.prec_no, self.block_no_nagoya, 2100, 1, 1):
                pass

    # 不正な日付
    def test_get_hourly_data_with_invalid_date(self):
        # 2018年13月33日のデータをget
        with self.assertRaises(ValueError):
            for data in self.jma.get_hourly_data(self.prec_no, self.block_no_nagoya, 2018, 13, 33):
                pass

    # station.get_hourly_dataのテスト
    def test_nagoya_station_get_hourly_data(self):
        station = self.jma.get_station(self.prec_no, self.block_no_nagoya)
        i = 1
        for data in station.get_hourly_data(self.year, self.month, self.day):
            self.assertEqual(datetime.datetime(self.year, self.month, self.day) + datetime.timedelta(hours=i), data.dt)
            i += 1

if __name__ == '__main__':
    unittest.main()
