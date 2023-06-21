from irradiance.preprocessing.DataPreprocessor import DataPreprocessor
from irradiance.models.model import SolarPanel
import pytz
import ephem
from datetime import datetime, timedelta
import numpy as np
from scipy.integrate import quad

NOON = 12
YEAR = datetime.now().year


class DataPreprocessorCharlie(DataPreprocessor):
    def __init__(self, data, lat, lon, sp: SolarPanel):
        super().__init__(data)

        # solar panel
        self.solar_panel = sp

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
        self._add_adjusted_srad()
        return self.data

    def _add_daytimes(self):
        daytimes = [self._month_daytime(m) for m in range(1, 13)]
        daytimes = np.array(daytimes).reshape(-1, 1)
        self.data['daytime'] = daytimes

    def _add_adjusted_srad(self):
        adjusted_srads = list()
        for m in range(1, 13):
            adjusted_srads.append(self._month_adjusted_srad(m))
        adjusted_srads = np.array(adjusted_srads).reshape(-1, 1)
        self.data['adjusted_srad'] = adjusted_srads

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

    def _month_adjusted_srad(self, month):
        srad = self.data.iloc[month - 1]['srad']
        daytime = self.data.iloc[month - 1]['daytime']

        p_exposed = srad * self.solar_panel.area  # Kilojoules

        p_useable = p_exposed * self.solar_panel.efficiency # Kilojoules
        p_useable *= 1000  # Joules

        def wattage_no_capacity(x):
            res = x ** 2 - (x * daytime)
            res = res * -6 * p_useable / (daytime ** 3)
            return res

        def wattage_capacity(x):
            w_nc = wattage_no_capacity(x)
            return min(self.solar_panel.capacity, w_nc)

        result, _ = quad(wattage_capacity, 0, daytime)
        result *= self.solar_panel.performance_ratio
        result /= 3.6e6

        return result

