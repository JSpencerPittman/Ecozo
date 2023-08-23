from windpower.WindTurbine import WindTurbine
from windpower.AtmosphericData import AtmosphericData
from DataManager.WindTK import WindTKAPI
from windpower.Evaluator import PowerEvaluator
from datetime import datetime

AVG_DAYS_IN_MONTH = 30
DEFAULT_YEAR = 2013
DAYS_IN_YEAR = 365


class Aeolus(object):
    def __init__(self, lat, lon, turbine: WindTurbine):
        self.latitude = lat
        self.longitude = lon
        self.wind_turbine = turbine

        self.api = WindTKAPI()
        self.api.download(lat, lon, DEFAULT_YEAR)
        self.api.tabelize()

        data = self.api.get_dataframe(t1=(1, 1), t2=(12, 31))
        self.atm_data = AtmosphericData()
        self.atm_data.add_windtk_data(data)

        self.pow_eval = PowerEvaluator(self.wind_turbine, self.atm_data)

    def hour(self):
        return self._calc_power_day_basis(1) / 24

    def day(self):
        return self._calc_power_day_basis(1)

    def five_days(self):
        return self._calc_power_day_basis(5)

    def month(self):
        return self._calc_power_day_basis(AVG_DAYS_IN_MONTH)

    def year(self):
        return self._calc_power_day_basis(DAYS_IN_YEAR)

    def _calc_power_day_basis(self, days):
        doy_init = datetime.now().timetuple().tm_yday

        total_power = 0

        for d in range(days):
            doy = doy_init + d
            if doy > 365:
                doy -= 365
            total_power += self.pow_eval.eval(doy)

        return total_power
