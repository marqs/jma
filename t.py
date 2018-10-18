import unittest
import datetime
import time

from jma import Jma

j = Jma()

# for p in j.get_prefectures():
#     print(p)
#     time.sleep(1)
#     for s in p.get_stations():
#         print(s)

# for d in j.get_hourly_data('48','1392',2018,10,7):
#     print(d)

print(j.get_station('55','1415'))