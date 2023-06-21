import math
from abc import ABC, abstractmethod
from windpower.WindTurbine import WindTurbine
from windpower.AtmosphericData import AtmosphericData

SECONDS_IN_DAY = 60 * 60 * 24  # s

AIR_DENSITY_SURFACE = 1.2250  # kg m^-3
RELATIVE_DENSITY_0m = 1
RELATIVE_DENSITY_500m = 0.9529
CHANGE_RD_PER_METER = (RELATIVE_DENSITY_0m - RELATIVE_DENSITY_500m) / 500


class PowerEvaluator(object):
    def __init__(self, turbine: WindTurbine, atm_data: AtmosphericData):
        super().__init__()
        self.turbine = turbine
        self.atm_data = atm_data

        self.air_dense_eval = AirDensityEvaluator(self.turbine.hub_height)

    def eval(self, doy: int):
        hub_height = self.turbine.hub_height
        efficiency = self.turbine.efficiency
        blade_radius = self.turbine.blade_radius

        wind_speed = self.atm_data.estimate_wind_speed(hub_height, doy)
        air_density = self.air_dense_eval.eval()

        cross_section = math.pi * (blade_radius ** 2)  # m^2
        volume = (SECONDS_IN_DAY * wind_speed) * cross_section  # m^3
        mass = volume * air_density  # kg
        energy = 0.5 * mass * (wind_speed ** 2)  # J

        power = efficiency * energy  # J
        power /= 3.6 * (10**6)  # kWh

        return power


class AirDensityEvaluator(object):
    def __init__(self, altitude: float):
        self.altitude = altitude

    def eval(self):
        result = RELATIVE_DENSITY_0m - CHANGE_RD_PER_METER * self.altitude
        result *= AIR_DENSITY_SURFACE
        return result
