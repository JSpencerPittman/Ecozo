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
