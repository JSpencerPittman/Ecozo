from DataManager.WorldClim import WorldClimAPI
from irradiance.models.model import SolarIrradModel, SolarPanel
from datetime import datetime, timedelta
from irradiance.preprocessing.charlie import DataPreprocessorCharlie

MONTHS_IN_YEAR = 12
DAYS_IN_YEAR = 365
AVG_DAYS_IN_MONTH = 30
HOURS_IN_DAY = 24


class Charlie(SolarIrradModel):
    def __init__(self, lat, lon, sp: SolarPanel):
        self.lat, self.lon = lat, lon
        self.solar_panel = sp
        self.api = WorldClimAPI()

        data = self.api.get_dataframe(lat, lon)

        dp = DataPreprocessorCharlie(data, lat, lon, self.solar_panel)
        self.wc_df = dp.format()

    def hour(self):
        return self._calc_srad_day_basis(1) / 24

    def day(self):
        return self._calc_srad_day_basis(1)

    def five_days(self):
        return self._calc_srad_day_basis(5)

    def month(self):
        return self._calc_srad_day_basis(AVG_DAYS_IN_MONTH)

    def year(self):
        return self._calc_srad_day_basis(DAYS_IN_YEAR)

    def _calc_srad_day_basis(self, days):
        now = datetime.now()
        month_count = [0] * MONTHS_IN_YEAR
        sum_srad = 0

        # Count days of each month
        for i in range(days):
            month_index = (now + timedelta(days=i)).month - 1
            month_count[month_index] += 1

        for i in range(MONTHS_IN_YEAR):
            days_in_month = month_count[i]
            monthly_adjusted_srad = self.wc_df.loc[i, 'adjusted_srad']
            sum_srad += monthly_adjusted_srad * days_in_month

        return sum_srad