import math
from abc import ABC, abstractmethod
from WindPower.WindTurbine import WindTurbine
from WindPower.AtmosphericData import AtmosphericData

SECONDS_IN_DAY = 60 * 60 * 24

DRY_SPECIFIC_GAS_CONSTANT = 287.058
VAPOR_SPECIFIC_GAS_CONSTANT = 461.495

UNIVERSAL_GAS_CONSTANT = 8.3144598
GRAVITATIONAL_ACCELERATION = 9.80665
MOLAR_MASS_EARTHS_AIR = 0.0289644

BUCKS_COEFF = 0.621121
BUCKS_NUM_A = 18.678
BUCKS_NUM_B = 234.5
BUCKS_NUM_C = 257.14

MAGNUS_TETENS_CONST = 6.11

MAGNUS_BETA = 17.625
MAGNUS_LAMBDA = 243.04


class Evaluator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def eval(self, doy: int):
        pass


class PowerEvaluator(Evaluator):
    def __init__(self, turbine: WindTurbine, atm_data: AtmosphericData):
        super().__init__()
        self.turbine = turbine
        self.atm_data = atm_data

        self.air_dense_eval = AirDensityEvaluator(self.atm_data, self.turbine.hub_height)

    def eval(self, doy: int):
        hub_height = self.turbine.hub_height
        efficiency = self.turbine.efficiency
        blade_radius = self.turbine.blade_radius

        wind_speed = self.atm_data.estimate_wind_speed(hub_height, doy)
        air_density = self.air_dense_eval.eval(doy)

        cross_section = math.pi * (blade_radius ** 2)
        volume = (SECONDS_IN_DAY * wind_speed) * cross_section
        mass = volume * air_density
        energy = 0.5 * mass * (wind_speed ** 2)

        power = efficiency * energy

        return power


class AirDensityEvaluator(Evaluator):
    def __init__(self, atm_data: AtmosphericData, altitude):
        super().__init__()
        self.atm_data = atm_data
        self.altitude = altitude

    def eval(self, doy: int):
        dry_air_press = self._eval_dry_air_pressure(doy)
        vap_air_press = self._eval_vapor_pressure(doy)
        temp = self.atm_data.estimate_temp(self.altitude, doy)

        dry_term = dry_air_press / (DRY_SPECIFIC_GAS_CONSTANT * temp)
        vapor_term = vap_air_press / (VAPOR_SPECIFIC_GAS_CONSTANT * temp)
        result = dry_term + vapor_term

        return result

    def _eval_dewpoint(self, doy: int):
        sat_vap_press = self._eval_saturated_vapor_pressure(doy)

        t_inv = self.atm_data.estimate_temp(self.altitude, doy)
        term1 = MAGNUS_TETENS_CONST * t_inv
        term2 = t_inv - math.log10(sat_vap_press)
        result = term1 / term2

        return result

    def _eval_dry_air_pressure(self, doy: int):
        total_pressure = self._eval_total_pressure(doy)
        vap_air_press = self._eval_vapor_pressure(doy)

        return total_pressure - vap_air_press

    def _eval_lapse_rate(self, doy: int):
        alt_range = self.atm_data.get_alt_range(self.altitude)
        temp_high = self.atm_data.estimate_temp(alt_range.low_alt, doy)
        temp_low = self.atm_data.estimate_temp(alt_range.high_alt, doy)

        return (temp_high - temp_low) / alt_range.diff()

    def _eval_relative_humidity(self, doy: int):
        dew_point = self._eval_dewpoint(doy)
        temp = self.atm_data.estimate_temp(self.altitude, doy)

        term1 = (MAGNUS_BETA * dew_point) / (MAGNUS_LAMBDA + dew_point)
        term2 = (MAGNUS_BETA * temp) / (MAGNUS_LAMBDA + temp)
        result = math.exp(term1) / math.exp(term2)
        result *= 100

        return result

    def _eval_total_pressure(self, doy: int):
        height_ref = 100  # meters

        lapse_rate = self._eval_lapse_rate(doy)
        temp_ref = self.atm_data.estimate_temp(height_ref, doy)
        press_ref = self.atm_data.get_specific_air_pressure(height_ref, doy)

        term1 = temp_ref - (self.altitude - height_ref) * lapse_rate

        term2 = GRAVITATIONAL_ACCELERATION * MOLAR_MASS_EARTHS_AIR
        term2 = term2 / (UNIVERSAL_GAS_CONSTANT * lapse_rate)

        result = press_ref * ((term1 / temp_ref) ** term2)
        return result

    def _eval_saturated_vapor_pressure(self, doy: int):
        temp = self.atm_data.estimate_temp(self.altitude, doy)

        term1 = BUCKS_NUM_A - (temp / BUCKS_NUM_B)
        term2 = temp / (BUCKS_NUM_C + temp)
        results = BUCKS_COEFF * math.exp(term1 * term2)

        return results

    def _eval_vapor_pressure(self, doy: int):
        rel_humid = self._eval_relative_humidity(doy)
        sat_vap_press = self._eval_saturated_vapor_pressure(doy)

        return rel_humid * sat_vap_press
