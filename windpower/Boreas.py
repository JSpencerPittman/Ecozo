from windpower.WindTurbine import WindTurbine
from DataManager.WindTK import WindTKAPI
from DataManager.OpenWeather import OpenWeatherAPI
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
import pandas as pd
from scipy.integrate import quad
import math
from util.piecewise import Piecewise
import numpy as np
import os
import pickle

AIR_DENSITY_SURFACE = 1.2250  # kg m^-3
RELATIVE_DENSITY_0m = 1
RELATIVE_DENSITY_500m = 0.9529
CHANGE_RD_PER_METER = (RELATIVE_DENSITY_0m - RELATIVE_DENSITY_500m) / 500
NON_SURF_ALTITUDES = [40, 60, 80, 100, 120, 140, 160, 200]
XGB_N_ESTIMATORS = 90
XGB_MAX_DEPTH = 5
WIND_ENERGY_DIVISIONS = 10
WIND_ENERGY_EPSABS = 1e10
DIVISIONS_PER_HOUR = 1
SECONDS_IN_HOUR = 3600


class Boreas(object):
    def __init__(self, wt: WindTurbine = None, lat=None, lon=None):
        self.wind_api = WindTKAPI()
        self.ow_api = OpenWeatherAPI()

        self.wt = wt
        self.lat, self.lon = lat, lon

        self.ws_reg = None
        self.ss = None

        self.pkl_path = os.path.join(os.path.dirname(__file__), 'saved/boreas.pkl')

        if os.path.exists(self.pkl_path):
            self.load()

    def hour(self):
        return self._estimate_captured_power(1, 0.1)

    def day(self):
        return self._estimate_captured_power(24, 0.5)

    def five_days(self):
        return self._estimate_captured_power(120, 3)

    @staticmethod
    def month():
        return -1

    @staticmethod
    def year():
        return -1

    def set_location(self, lat, lon):
        self.lat, self.lon = lat, lon

    def set_wind_turbine(self, wt: WindTurbine):
        self.wt = wt

    def _estimate_captured_power(self, duration, increments):
        if self.lat is None or self.lon is None:
            raise Exception('Location hasn\'t been set for Boreas model!')
        if self.wt is None:
            raise Exception('Wind turbine hasn\t been set for Boreas model!')

        # Create a piecewise function of future surface wind speeds
        self.ow_api.download(lat=self.lat, lon=self.lon)
        future_wind_speeds = list(self.ow_api.get_dataframe().speed.values)
        ws_piecewise = Piecewise(y=future_wind_speeds, x_int=3)

        inc_dur = SECONDS_IN_HOUR * increments

        wind_energies = list()
        for i in np.arange(0, duration + increments, increments):
            surf_ws = ws_piecewise.get_y(i)
            wind_energy = self._estimate_total_wind_energy(inc_dur, surf_ws)
            wind_energies.append(wind_energy)

        total_energy = 0
        for i in range(len(wind_energies) - 1):
            first_point = (0, wind_energies[i])
            second_point = (increments, wind_energies[i+1])
            total_energy += self._area_under_line(first_point, second_point)

        total_energy *= self.wt.efficiency
        total_energy /= 3.6e6

        return total_energy

    def _estimate_total_wind_energy(self, duration, surf_ws):
        if self.wt is None:
            raise Exception('Wind Turbine hasn\'t been set for Boreas model!')

        def g(y):
            width = self._horizontal_chord_width(self.wt.blade_radius, self.wt.hub_height, y)
            return self._estimate_wind_layer_energy(width, duration, surf_ws, y)

        bottom = self.wt.hub_height - self.wt.blade_radius
        top = self.wt.hub_height + self.wt.blade_radius
        return quad(g, bottom, top, limit=WIND_ENERGY_DIVISIONS, epsabs=WIND_ENERGY_EPSABS)[0]

    def _estimate_wind_layer_energy(self, width, duration, surf_ws, alt):
        wind_speed = self._estimate_wind_speed(surf_ws, alt)
        air_density = self._air_density_at_altitude(alt)
        layer_area = width * duration * wind_speed
        mass = layer_area * air_density
        return 0.5 * mass * wind_speed**2

    def _estimate_wind_speed(self, surf_ws, alt):
        if self.ws_reg is None:
            print('Training Boreas model for first time use')
            self._train_ws_regressor()

        input_data = pd.DataFrame([[surf_ws, alt]], columns=['surface_speed', 'altitude'])
        input_data = self.ss.transform(input_data)
        return self.ws_reg.predict(input_data)

    def _train_ws_regressor(self):
        # Load the training data
        windtk_df = self.wind_api.get_dataframe(t1=(1, 1), t2=(12, 31))

        # Format it into a list of wind speeds and their corresponding altitudes
        #   and surface wind speeds
        ws_df = list()
        for i, row in windtk_df.iterrows():
            surf_speed = row['wind_speed_10m']
            for alt in NON_SURF_ALTITUDES:
                col = f"wind_speed_{alt}m"
                speed = row[col]
                ws_df.append([surf_speed, alt, speed])
        speed_df = pd.DataFrame(ws_df, columns=['surface_speed', 'altitude', 'wind_speed'])

        # Split into features and labels
        X = speed_df[['surface_speed', 'altitude']].copy()
        y = speed_df['wind_speed']

        # Establish and fit the scaler
        self.ss = StandardScaler()
        X = self.ss.fit_transform(X)

        # Establish and train this model's regressor
        self.ws_reg = XGBRegressor(n_estimators=XGB_N_ESTIMATORS, max_depth=XGB_MAX_DEPTH)
        self.ws_reg.fit(X, y)

        self.save()

    def save(self):
        data = {
            'regression_model': self.ws_reg,
            'standard_scaler': self.ss
        }

        with open(self.pkl_path, 'wb') as pkl_file:
            pickle.dump(data, pkl_file)

    def load(self):
        with open(self.pkl_path, 'rb') as pkl_file:
            data = pickle.load(pkl_file)

        self.ws_reg = data['regression_model']
        self.ss = data['standard_scaler']

    @staticmethod
    def _horizontal_chord_width(radius, y_center, y_chord):
        return 2 * math.sqrt(radius ** 2 - (y_center - y_chord) ** 2)

    @staticmethod
    def _area_under_line(p1, p2):
        x_diff = p2[0] - p1[0]
        y_diff = abs(p2[1] - p1[1])
        sq_area = min(p1[1], p2[1]) * x_diff
        tri_area = x_diff * y_diff * 0.5
        return sq_area + tri_area

    @staticmethod
    def _air_density_at_altitude(alt):
        air_density = RELATIVE_DENSITY_0m - CHANGE_RD_PER_METER * alt
        air_density *= AIR_DENSITY_SURFACE
        return air_density