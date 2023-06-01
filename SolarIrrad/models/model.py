from abc import ABC, abstractmethod


class SolarIrradModel(ABC):
    @abstractmethod
    def hour(self):
        pass

    @abstractmethod
    def day(self):
        pass

    @abstractmethod
    def five_days(self):
        pass

    @abstractmethod
    def month(self):
        pass

    @abstractmethod
    def year(self):
        pass


class SolarPanel(object):
    def __init__(self, eff: float, area: float, pr: float, cap: float):
        self.efficiency = float(eff) / 100 if float(eff) > 1 else float(eff)
        self.area = float(area)
        self.performance_ratio = float(pr)
        self.capacity = float(cap)

    @staticmethod
    def kilojoule_to_kilowatthour(kj):
        return kj / 3.6e3

