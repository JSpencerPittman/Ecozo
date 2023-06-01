class SolarPanel(object):
    def __init__(self, eff: float, area: float, pr: float):
        self.efficiency = float(eff) / 100 if float(eff) > 1 else float(eff)
        self.area = float(area)
        self.performance_ratio = float(pr)

    def calc_generated_power(self, exposure):
        sol_pow = self.efficiency * self.area * self.performance_ratio
        kj_pow = sol_pow * exposure
        return self._kilojoule_to_kilowatthour(kj_pow)

    @staticmethod
    def _kilojoule_to_kilowatthour(kj):
        return kj / 3.6e3

