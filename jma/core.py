from requests_html import HTMLSession
import urllib
import re
import datetime

session = HTMLSession()


class Latitude:
    def __init__(self, degrees, minutes):
        self.degrees = degrees
        self.minutes = minutes


class Longitude:
    def __init__(self, degrees, minutes):
        self.degrees = degrees
        self.minutes = minutes


class Station:
    def __init__(self, prec_no, block_no, name, name_kana, latitude, longitude, altitude, station_type, f_pre, f_wsp, f_tem, f_sun, f_snc):
        self.prec_no = prec_no
        self.block_no = block_no

        self.name = name
        self.name_kana = name_kana
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.station_type = station_type
        self.f_pre = f_pre
        self.f_wsp = f_wsp
        self.f_tem = f_tem
        self.f_sun = f_sun
        self.f_snc = f_snc

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'<Station> name: {self.name} prec_no: {self.prec_no} block_no: {self.block_no}'

    def get_hourly_data(self, year, month, day):
        return Jma().get_hourly_data(self.prec_no, self.block_no, self.station_type, year, month, day)

    def get_ten_minutely_data(self, year, month, day):
        return Jma().get_ten_minutely_data(self.prec_no, self.block_no, self.station_type, year, month, day)


class WeatherDataRow:

    def __repr__(self):
        str = ', '.join("%s: %s" % item for item in vars(self).items())
        return str

    def _direction(self, value):

        return mapping(value)

    def _convert(self, value):
        '''値の処理'''
        # http://www.data.jma.go.jp/obd/stats/data/mdrr/man/remark.html

        direction_mapping = {
            '北': 'N',
            '東': 'E',
            '南': 'S',
            '西': 'W',
            '北東': 'NE',
            '南東': 'SE',
            '南西': 'SW',
            '北西': 'NW',
            '北北東': 'NNE',
            '東南東': 'ESE',
            '南南西': 'SSW',
            '西北西': 'WNW',
            '東北東': 'ENE',
            '南南東': 'SSE',
            '西南西': 'WSW',
            '北北西': 'NNW'
        }
        if value == '--':
            return None
        if value == '':
            return None
        if value in direction_mapping:
            return direction_mapping[value]
        if '×' in value:
            return None
        if '.' in value:
            return float(value)
        try:
            return int(value)
        except ValueError:
            return value

    def _parse_time_value(self, dt, value):
        if ":" in value:
            dt += datetime.timedelta(hours=int(value.split(":")[0]), minutes=int(value.split(":")[1]))
        else:
            dt += datetime.timedelta(hours=int(value))
        return dt


class HourlyWeatherDataRow(WeatherDataRow):

    def __init__(self, row, year, month, day):
        columns = row.find("td")
        dt = self._parse_time_value(datetime.datetime(year, month, day), columns[0].text)

        if len(columns) == 17:
            # station_type = "s"
            self.type = "s"
            # 時
            self.dt = dt
            # 気圧(hPa) 現地
            self.air_pressure_spot = self._convert(columns[1].text)
            # 気圧(hPa) 海面
            self.air_pressure_sea = self._convert(columns[2].text)
            # 降水量(mm)
            self.precipitation = self._convert(columns[3].text)
            # 気温(度)
            self.temperature = self._convert(columns[4].text)
            # 露点温度(度)
            self.dew_point_temperature = self._convert(columns[5].text)
            # 蒸気圧(hPa)
            self.vapor_pressure = self._convert(columns[6].text)
            # 湿度(%)
            self.humidity = self._convert(columns[7].text)
            # 風速
            self.wind_speed = self._convert(columns[8].text)
            # 風向
            self.wind_direction = self._convert(columns[9].text)
            # 日照時間(h)
            self.daylight_hours = self._convert(columns[10].text)
            # 全天日射量(MJ/m2)
            self.solar_irradiance = self._convert(columns[11].text)
            # 雪(降雪)
            self.snowfall = self._convert(columns[12].text)
            # 雪(積雪)
            self.snow_cover = self._convert(columns[13].text)
            # 天気
            # self.weather = self._convert(columns[14].text)
            # 雲量
            # self.cloud_cover = self._convert(columns[15].text)
            # 視程(km)
            # self.visibility = self._convert(columns[16].text)
        elif len(columns) == 8:
            # station_type = "a"
            self.type = "a"
            # 時
            self.dt = dt
            # 降水量(mm)
            self.precipitation = self._convert(columns[1].text)
            # 気温(度)
            self.temperature = self._convert(columns[2].text)
            # 風速
            self.wind_speed = self._convert(columns[3].text)
            # 風向
            self.wind_direction = self._convert(columns[4].text)
            # 日照時間(h)
            self.daylight_hours = self._convert(columns[5].text)
            # 雪(降雪)
            self.snowfall = self._convert(columns[6].text)
            # 雪(積雪)
            self.snow_cover = self._convert(columns[7].text)


class TenMinutelyWeatherDataRow(WeatherDataRow):

    def __init__(self, row, year, month, day):
        columns = row.find("td")
        dt = self._parse_time_value(datetime.datetime(year, month, day), columns[0].text)

        if len(columns) == 11:
            # station_type = "s""
            self.type = "s"
            # 時分
            self.dt = dt
            # 気圧(hPa) 現地
            self.air_pressure_spot = self._convert(columns[1].text)
            # 気圧(hPa) 海面
            self.air_pressure_sea = self._convert(columns[2].text)
            # 降水量(mm)
            self.precipitation = self._convert(columns[3].text)
            # 気温(度)
            self.temperature = self._convert(columns[4].text)
            # 相対湿度(%)
            self.relative_humidity = self._convert(columns[5].text)
            # 平均風速(m/s)
            self.mean_wind_speed = self._convert(columns[6].text)
            # 平均風速（風向）
            self.wind_direction = self._convert(columns[7].text)
            # 最大瞬間(m/s)
            self.max_wind_speed = self._convert(columns[8].text)
            # 最大瞬間（風向）
            self.max_wind_direction = self._convert(columns[9].text)
            # 日照時間（分）
            self.daylight_minute = self._convert(columns[10].text)
        elif len(columns) == 8:
            # station_type = "a"
            self.type = "a"
            # 時分
            self.dt = dt
            # 降水量(mm)
            self.precipitation = self._convert(columns[1].text)
            # 気温(度)
            self.temperature = self._convert(columns[2].text)
            # 平均風速(m/s)
            self.mean_wind_speed = self._convert(columns[3].text)
            # 平均風速（風向）
            self.wind_direction = self._convert(columns[4].text)
            # 最大瞬間(m/s)
            self.max_wind_speed = self._convert(columns[5].text)
            # 最大瞬間（風向）
            self.max_wind_direction = self._convert(columns[6].text)
            # 日照時間（分）
            self.daylight_minute = self._convert(columns[7].text)


class Jma:

    def _extract_station_info(self, str):
        s = re.search(r"^javascript:viewPoint\((.+)\);$", str)
        infos = s.group(1).replace("'", "").split(",")
        #print(infos)
        # 区分
        station_type = infos[0]
        # 名前
        name = infos[2]
        # カナ名
        name_kana = infos[3]
        # 緯度
        latitude_degrees = infos[4]
        latitude_minutes = infos[5]
        # 軽度
        longitude_degrees = infos[6]
        longitude_minutes = infos[7]
        # 高度
        altitude = infos[8]
        # 測定項目
        # 降水量
        f_pre = infos[9]
        # 風向,風速
        f_wsp = infos[10]
        # 気温
        f_tem = infos[11]
        # 日照時間
        f_sun = infos[12]
        # 積雪の深さ
        f_snc = infos[13]

        info = {
            "station_type": station_type,
            "name": name,
            "name_kana": name_kana,
            "altitude": altitude,
            "latitude": Latitude(latitude_degrees, latitude_minutes),
            "longitude": Longitude(longitude_degrees, longitude_minutes),
            "f_pre": f_pre,
            "f_wsp": f_wsp,
            "f_tem": f_tem,
            "f_sun": f_sun,
            "f_snc": f_snc
        }
        return info

    def _extract_prec_no(self, url):
        query = urllib.parse.urlparse(url).query
        parsed_query = urllib.parse.parse_qs(query)
        prec_no = parsed_query["prec_no"][0]
        return prec_no

    def _extract_block_no(self, url):
        query = urllib.parse.urlparse(url).query
        parsed_query = urllib.parse.parse_qs(query)
        block_no = parsed_query["block_no"][0]
        return block_no

    def _construct_url(self, prec_no, block_no, station_type, year, month, day, url_type=None):
        if url_type == "get_hourly_data":
            params = {
                "prec_no": prec_no,
                "block_no": block_no,
                "year": year,
                "month": month,
                "day": day
            }
            query = urllib.parse.urlencode(params)
            url = "http://www.data.jma.go.jp/obd/stats/etrn/view/hourly_{}1.php?".format(station_type) + query
        elif url_type == "get_ten_minutely_data":
            params = {
                "prec_no": prec_no,
                "block_no": block_no,
                "year": year,
                "month": month,
                "day": day
            }
            query = urllib.parse.urlencode(params)
            url = "http://www.data.jma.go.jp/obd/stats/etrn/view/10min_{}1.php?".format(station_type) + query
        return url

    def get_prefectures(self):
        url = "http://www.data.jma.go.jp/obd/stats/etrn/select/prefecture00.php"
        list = []
        r = session.get(url)
        for area in r.html.find("area"):
            prec_no = self._extract_prec_no(area.attrs["href"])
            list.append(prec_no)
        return list

    def get_stations(self, prec_no):
        block_no_array = []
        stations = {}
        url = "http://www.data.jma.go.jp/obd/stats/etrn/select/prefecture.php?prec_no={}".format(prec_no)
        #print(url)
        r = session.get(url)

        # 存在しないprec_noの場合はエラー
        if len(r.html.find("area")) == 0:
            raise InvalidPrecNo

        for area in r.html.find("area"):
            #print(area)
            prec_no_in_url = self._extract_prec_no(area.attrs["href"])
            if prec_no != prec_no_in_url:
                continue
            block_no = self._extract_block_no(area.attrs["href"])
            # 全地点は省く
            if block_no == "00":
                continue
            name = area.attrs["alt"]

            onmouseover = area.attrs["onmouseover"]
            station_params = self._extract_station_info(onmouseover)

            # 同じ情報が2個づつ入っているので1個にする
            if block_no not in block_no_array:
                block_no_array.append(block_no)
                stations[block_no] = Station(prec_no, block_no, **station_params)
        #print(stations)
        return stations

    def get_station(self, prec_no, block_no):
        try:
            stations = self.get_stations(prec_no)
            return stations[block_no]
        except KeyError:
            print("Invalid block_no")

    def get_hourly_data(self, prec_no, block_no, station_type, year, month, day):
        url = self._construct_url(prec_no, block_no, station_type, year, month, day, url_type="get_hourly_data")
        #print(url)
        r = session.get(url)

        # ヘッダを削除してテーブルを読み込む
        rows = r.html.find("#tablefix1 > tr")[2:]
        for row in rows:
            yield HourlyWeatherDataRow(row, year, month, day)

    def get_ten_minutely_data(self, prec_no, block_no, station_type, year, month, day):
        url = self._construct_url(prec_no, block_no, station_type, year, month, day, url_type="get_ten_minutely_data")
        #print(url)
        r = session.get(url)

        # ヘッダを削除してテーブルを読み込む
        rows = r.html.find("#tablefix1 > tr")[2:]
        for row in rows:
            yield TenMinutelyWeatherDataRow(row, year, month, day)


class InvalidPrecNo(Exception):
    "PrecNo is invalid"


class InvalidBlockNo(Exception):
    "BlockNo is invalid"
