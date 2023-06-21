from DataManager.WorldClim import WorldClimAPI
from irradiance.models.model import SolarIrradModel, SolarPanel
from datetime import datetime, timedelta

MONTHS_IN_YEAR = 12
DAYS_IN_YEAR = 365
AVG_DAYS_IN_MONTH = 30
HOURS_IN_DAY = 24


class Alpha(SolarIrradModel):
    def __init__(self, lat, lon, sp: SolarPanel):
        self.lat, self.lon = lat, lon
        self.solar_panel = sp
        self.api = WorldClimAPI()
        self.wc_df = self.api.get_dataframe(lat, lon)

    def hour(self):
        exposure = self._calc_srad_day_basis(1) / HOURS_IN_DAY
        return self._calc_power(exposure)

    def day(self):
        exposure = self._calc_srad_day_basis(1)
        return self._calc_power(exposure)

    def five_days(self):
        exposure = self._calc_srad_day_basis(5)
        return self._calc_power(exposure)

    def month(self):
        exposure = self._calc_srad_day_basis(AVG_DAYS_IN_MONTH)
        return self._calc_power(exposure)

    def year(self):
        exposure = self._calc_srad_day_basis(DAYS_IN_YEAR)
        return self._calc_power(exposure)

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
            monthly_srad = self.wc_df.loc[i, 'srad']
            sum_srad += monthly_srad * days_in_month

        return sum_srad

    def _calc_power(self, exposure):
        power_exposed = exposure * self.solar_panel.area
        power_useable = power_exposed * self.solar_panel.efficiency * self.solar_panel.performance_ratio
        generated_power = SolarPanel.kilojoule_to_kilowatthour(power_useable)
        return generated_power

