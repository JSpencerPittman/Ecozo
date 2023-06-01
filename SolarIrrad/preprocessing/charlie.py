from SolarIrrad.preprocessing.DataPreprocessor import DataPreprocessor
import pytz
import ephem
from datetime import datetime, timedelta
import numpy as np

NOON = 12
YEAR = datetime.now().year


class DataPreprocessorCharlie(DataPreprocessor):
    def __init__(self, data, lat, lon):
        super().__init__(data)

        # location
        self.latitude = lat
        self.longitude = lon

        # observer
        self.obs = ephem.Observer()
        self.obs.lat = str(self.latitude)
        self.obs.lon = str(self.longitude)

        # sun
        self.sun = ephem.Sun()

    def format(self):
        self._add_daytimes()
        return self.data

    def _add_daytimes(self):
        daytimes = [self._month_daytime(m) for m in range(1, 13)]
        daytimes = np.array(daytimes).reshape(-1, 1)
        self.data['daytime'] = daytimes

    def _month_daytime(self, month):
        day = datetime(YEAR, month, 1, NOON)

        days_in_month = 0
        total_seconds = 0

        while day.month == month:

            days_in_month += 1
            total_seconds += self._daytime(day)
            day += timedelta(days=1)

        avg_daytime = total_seconds // days_in_month
        return avg_daytime

    def _daytime(self, date):
        utc_dt = date.astimezone(pytz.utc)
        self.obs.date = utc_dt

        self.sun.compute(self.obs)

        sun_rise = self.obs.previous_rising(self.sun).datetime()
        sun_set = self.obs.next_setting(self.sun).datetime()

        diff_sec = (sun_set - sun_rise).seconds

        return diff_sec

