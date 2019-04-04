from requests_html import HTMLSession
import urllib
import re
import datetime

# 1時間毎の観測値のカラム数
NUMBER_OF_COLUMNS_HOURLY_DATA_S = 17
NUMBER_OF_COLUMNS_HOURLY_DATA_A = 8
NUMBER_OF_COLUMNS_TEN_MINUTELY_DATA_S = 11
NUMBER_OF_COLUMNS_TEN_MINUTELY_DATA_A = 8

STATION_TYPE_S = "s"
STATION_TYPE_A = "a"

DATA_TYPE_HOURLY = "hourly"
DATA_TYPE_TEN_MINUTELY = "ten_minutely"

session = HTMLSession()

class Prefecture:
    def __init__(self, prec_no, name):
        self.prec_no = prec_no
        self.name = name

    def __repr__(self):
        return '<Station>' + ', '.join("%s: %s" % item for item in vars(self).items())

    def __str__(self):
        return self.__repr__()

    def get_stations(self):
        return Jma().get_stations(self.prec_no)


class Station:
    def __init__(self, prec_no, block_no, **kwargs):
        self.prec_no = prec_no
        self.block_no = block_no

        #kwargs
        self.name = kwargs['name']
        self.name_kana = kwargs['name_kana']
        self.latitude_degrees = kwargs['latitude_degrees']
        self.latitude_minutes = kwargs['latitude_minutes']
        self.longitude_degrees = kwargs['longitude_degrees']
        self.longitude_minutes = kwargs['longitude_minutes']
        self.altitude = kwargs['altitude']
        self.station_type = kwargs['station_type']
        self.f_pre = kwargs['f_pre']
        self.f_wsp = kwargs['f_wsp']
        self.f_tem = kwargs['f_tem']
        self.f_sun = kwargs['f_sun']
        self.f_snc = kwargs['f_snc']
        self.observation_end_date = kwargs['observation_end_date']

    def __repr__(self):
        return '<Station>' + ', '.join("%s: %s" % item for item in vars(self).items())

    def __str__(self):
        return self.__repr__()

    def get_hourly_data(self, year, month, day):
        return Jma().get_hourly_data(self.prec_no, self.block_no, year, month, day)

    def get_ten_minutely_data(self, year, month, day):
        return Jma().get_ten_minutely_data(self.prec_no, self.block_no, year, month, day)


class WeatherDataRow:

    def __repr__(self):
        return '<WeatherDataRow>' + ', '.join("%s: %s" % item for item in vars(self).items())

    def __str__(self):
        return self.__repr__()

    def _sanitize(self, value):
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
            '北北西': 'NNW',
            '静穏': None
        }
        if value == '--':
            return None
        if value == '///':
            return None
        if value == '':
            return None
        if value == '#':
            return None
        if value in direction_mapping:
            return direction_mapping[value]
        if '×' in value:
            return None
        if '.' in value:
            if ']' in value:
                return float(value.replace(']',''))
            elif ')' in value:
                return float(value.replace(')',''))
            else:
                return float(value)
        try:
            return int(value)
        except ValueError:
            return value

    def _convert_weather_img(self, column):
        if len(column.find("img")) == 1:
            return column.find("img", first=True).attrs["alt"]
        if len(column.find("img")) == 0:
            return None
        raise WeatherImageConvertError

    def _parse_time_value(self, dt, value):
        if ":" in value:
            dt += datetime.timedelta(hours=int(value.split(":")[0]), minutes=int(value.split(":")[1]))
        else:
            dt += datetime.timedelta(hours=int(value))
        return dt


class HourlyWeatherDataRow(WeatherDataRow):

    def __init__(self, row, year, month, day, url):
        columns = row.find("td")
        dt = self._parse_time_value(datetime.datetime(year, month, day), columns[0].text)

        if len(columns) == NUMBER_OF_COLUMNS_HOURLY_DATA_S:
            # station_type = "s"
            self.type = STATION_TYPE_S
            # url
            self.url = url

            ### data ###
            # 時
            self.dt = dt
            # 気圧(hPa) 現地
            self.air_pressure_spot = self._sanitize(columns[1].text)
            # 気圧(hPa) 海面
            self.air_pressure_sea = self._sanitize(columns[2].text)
            # 降水量(mm)
            self.precipitation = self._sanitize(columns[3].text)
            # 気温(度)
            self.temperature = self._sanitize(columns[4].text)
            # 露点温度(度)
            self.dew_point_temperature = self._sanitize(columns[5].text)
            # 蒸気圧(hPa)
            self.vapor_pressure = self._sanitize(columns[6].text)
            # 湿度(%)
            self.humidity = self._sanitize(columns[7].text)
            # 風速
            self.wind_speed = self._sanitize(columns[8].text)
            # 風向
            self.wind_direction = self._sanitize(columns[9].text)
            # 日照時間(h)
            self.daylight_hours = self._sanitize(columns[10].text)
            # 全天日射量(MJ/m2)
            self.solar_irradiance = self._sanitize(columns[11].text)
            # 雪(降雪)
            self.snowfall = self._sanitize(columns[12].text)
            # 雪(積雪)
            self.snow_cover = self._sanitize(columns[13].text)
            # 天気
            self.weather = self._convert_weather_img(columns[14])
            # 雲量
            self.cloud_cover = self._sanitize(columns[15].text)
            # 視程(km)
            self.visibility = self._sanitize(columns[16].text)
        elif len(columns) == NUMBER_OF_COLUMNS_HOURLY_DATA_A:
            # station_type = "a"
            self.type = STATION_TYPE_A
            # url
            self.url = url

            ### data ###
            # 時
            self.dt = dt
            # 降水量(mm)
            self.precipitation = self._sanitize(columns[1].text)
            # 気温(度)
            self.temperature = self._sanitize(columns[2].text)
            # 風速
            self.wind_speed = self._sanitize(columns[3].text)
            # 風向
            self.wind_direction = self._sanitize(columns[4].text)
            # 日照時間(h)
            self.daylight_hours = self._sanitize(columns[5].text)
            # 雪(降雪)
            self.snowfall = self._sanitize(columns[6].text)
            # 雪(積雪)
            self.snow_cover = self._sanitize(columns[7].text)


class TenMinutelyWeatherDataRow(WeatherDataRow):

    def __init__(self, row, year, month, day, url):
        columns = row.find("td")
        dt = self._parse_time_value(datetime.datetime(year, month, day), columns[0].text)

        if len(columns) == NUMBER_OF_COLUMNS_TEN_MINUTELY_DATA_S:
            # station_type = "s""
            self.type = STATION_TYPE_S
            # url
            self.url = url
            ### data ###
            # 時分
            self.dt = dt
            # 気圧(hPa) 現地
            self.air_pressure_spot = self._sanitize(columns[1].text)
            # 気圧(hPa) 海面
            self.air_pressure_sea = self._sanitize(columns[2].text)
            # 降水量(mm)
            self.precipitation = self._sanitize(columns[3].text)
            # 気温(度)
            self.temperature = self._sanitize(columns[4].text)
            # 相対湿度(%)
            self.relative_humidity = self._sanitize(columns[5].text)
            # 平均風速(m/s)
            self.mean_wind_speed = self._sanitize(columns[6].text)
            # 平均風速（風向）
            self.wind_direction = self._sanitize(columns[7].text)
            # 最大瞬間(m/s)
            self.max_wind_speed = self._sanitize(columns[8].text)
            # 最大瞬間（風向）
            self.max_wind_direction = self._sanitize(columns[9].text)
            # 日照時間（分）
            self.daylight_minute = self._sanitize(columns[10].text)
        elif len(columns) == NUMBER_OF_COLUMNS_TEN_MINUTELY_DATA_A:
            # station_type = "a"
            self.type = STATION_TYPE_A
            # url
            self.url = url

            ### data ###
            # 時分
            self.dt = dt
            # 降水量(mm)
            self.precipitation = self._sanitize(columns[1].text)
            # 気温(度)
            self.temperature = self._sanitize(columns[2].text)
            # 平均風速(m/s)
            self.mean_wind_speed = self._sanitize(columns[3].text)
            # 平均風速（風向）
            self.wind_direction = self._sanitize(columns[4].text)
            # 最大瞬間(m/s)
            self.max_wind_speed = self._sanitize(columns[5].text)
            # 最大瞬間（風向）
            self.max_wind_direction = self._sanitize(columns[6].text)
            # 日照時間（分）
            self.daylight_minute = self._sanitize(columns[7].text)


class Jma:

    def _observation_end_date(self, year, month, day):
        if year == '9999' or month == '99' or day == '99':
            return None
        else:
            return datetime.date(year=int(year),month=int(month),day=int(day))

    def _extract_station_info(self, str):
        s = re.search(r"^javascript:viewPoint\((.+)\);$", str)
        info = s.group(1).replace("'", "").split(",")
        #print(info)
        # 区分
        station_type = info[0]
        # 名前
        name = info[2]
        # カナ名
        name_kana = info[3]
        # 緯度
        latitude_degrees = info[4]
        latitude_minutes = info[5]
        # 軽度
        longitude_degrees = info[6]
        longitude_minutes = info[7]
        # 高度
        altitude = info[8]
        # 測定項目
        # 降水量
        f_pre = bool(int(info[9]))
        # 風向,風速
        f_wsp = bool(int(info[10]))
        # 気温
        f_tem = bool(int(info[11]))
        # 日照時間
        f_sun = bool(int(info[12]))
        # 積雪の深さ
        f_snc = bool(int(info[13]))

        observation_end_date = self._observation_end_date(year=info[14], month=info[15], day=info[16])

        info = {
            "station_type": station_type,
            "name": name,
            "name_kana": name_kana,
            "altitude": altitude,
            "latitude_degrees": latitude_degrees,
            "latitude_minutes": latitude_minutes,
            "longitude_degrees": longitude_degrees,
            "longitude_minutes": longitude_minutes,
            "f_pre": f_pre,
            "f_wsp": f_wsp,
            "f_tem": f_tem,
            "f_sun": f_sun,
            "f_snc": f_snc,
            "observation_end_date": observation_end_date
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

    def _construct_url(self, prec_no, block_no, station_type, year, month, day, data_frequenry=None):
        if data_frequenry == "hourly":
            params = {
                "prec_no": prec_no,
                "block_no": block_no,
                "year": year,
                "month": month,
                "day": day
            }
            query = urllib.parse.urlencode(params)
            url = "http://www.data.jma.go.jp/obd/stats/etrn/view/hourly_{}1.php?".format(station_type) + query
            return url
        if data_frequenry == "ten_minutely":
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
        raise InvalidDataFrequency

    def _validate_date(self, year, month, day):
        datetime.datetime(year=year,month=month,day=day)

    def get_prefectures(self):
        url = "http://www.data.jma.go.jp/obd/stats/etrn/select/prefecture00.php"
        r = session.get(url)

        for area in r.html.find("area"):
            prec_no = self._extract_prec_no(area.attrs["href"])
            prec_name = area.attrs["alt"]
            yield Prefecture(prec_no, prec_name)

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
                yield Station(prec_no, block_no, **station_params)

    def get_station(self, prec_no, block_no):
        for station in self.get_stations(prec_no):
            if station.block_no == block_no:
                return station
        raise InvalidBlockNo     

    def get_hourly_data(self, prec_no, block_no, year, month, day):
        self._validate_date(year, month, day)
        station = self.get_station(prec_no, block_no)
        url = self._construct_url(prec_no, block_no, station.station_type, year, month, day, data_frequenry=DATA_TYPE_HOURLY)
        #print(url)
        r = session.get(url)

        # ヘッダを削除してテーブルを読み込む
        if len(r.html.find("#tablefix1")) > 0:
            rows = r.html.find("#tablefix1 > tr")[2:]
            #print(rows)
            for row in rows:
                yield HourlyWeatherDataRow(row, year, month, day, url)
        else:
            div_main_text = r.html.find("#main",first=True).text
            if div_main_text.count("閲覧可能な日まで戻るか、「メニューに戻る」ボタンをクリックして下さい。") > 0:
                raise FutureDateError
            else:
                raise Exception


    def get_ten_minutely_data(self, prec_no, block_no, year, month, day):
        self._validate_date(year, month, day)
        station = self.get_station(prec_no, block_no)
        url = self._construct_url(prec_no, block_no, station.station_type, year, month, day, data_frequenry=DATA_TYPE_TEN_MINUTELY)
        #print(url)
        r = session.get(url)

        # ヘッダを削除してテーブルを読み込む
        rows = r.html.find("#tablefix1 > tr")[2:]
        for row in rows:
            yield TenMinutelyWeatherDataRow(row, year, month, day, url)


class InvalidPrecNo(Exception):
    "PrecNo is invalid"


class InvalidBlockNo(Exception):
    "BlockNo is invalid"


class InvalidDataFrequency(Exception):
    "Data frequency is invalid"


class WeatherImageConvertError(Exception):
    "WeatherImageConversion was failed"


class FutureDateError(Exception):
    "Specified date is future date"