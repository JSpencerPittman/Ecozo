import yaml

from DataManager.PSM3 import PSM3API
from irradiance.models.model import SolarIrradModel, Results, ModelPackage
from irradiance.preprocessing.bravo import DataPreprocessorPSM3, DataPreprocessorOpenWeather
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBRegressor
from irradiance.models.model import SolarPanel
from util.piecewise import Piecewise
from scipy.integrate import quad
import pickle
import os
import pandas as pd
import numpy as np
import psutil

RANDOM_SEED = 42
DEFAULT_YEAR = 2014


class Delta(SolarIrradModel):
    def __init__(self, sp: SolarPanel):
        # Classifier
        self.ss_clf = StandardScaler()
        self.poly_feat_clf = PolynomialFeatures(2)

        # Regressor
        self.ss_reg = StandardScaler()
        self.poly_feat_reg = PolynomialFeatures(2)

        # Models
        self.clf = None
        self.reg = None

        self.psm3_api = PSM3API()
        self.solar_panel = sp

        self.dp_psm3 = None
        self.dp_ow = None

        self.pkl_path_clf = os.path.join(os.path.dirname(__file__), 'saved/delta_clf.pkl')
        self.pkl_path_reg = os.path.join(os.path.dirname(__file__), 'saved/delta_reg.pkl')
        self.loc_path = os.path.join(os.path.dirname(__file__), '../locations.yaml')

        self.pred = None
        self.pw = None

        if os.path.exists(self.pkl_path_clf) and \
           os.path.exists(self.pkl_path_reg):
            self._load_clf()
            self._load_reg()
        else:
            self._train()

    def hour(self):
        return self._calc_power(1)

    def day(self):
        return self._calc_power(8)

    def five_days(self):
        return self._calc_power(40)

    def month(self):
        return -1

    def year(self):
        return -1

    def _calc_power(self, time):
        """
        Calculate how much power was generated for a specific time interval
        :param time: how many hours in advance
        :return: total power generated in kWh
        """

        def estimate_power_at_instant(x):
            est_pow = self.pw.get_y(x)  # solar irradiance w/m^2
            est_pow *= 3.6  # Convert to kJ/m^2/hr

            # How much energy is the solar panel exposed to
            est_pow *= self.solar_panel.efficiency * self.solar_panel.area

            # factor in capacity
            capacity = self.solar_panel.capacity * 3.6  # In kJ/hr
            est_pow = min(capacity, est_pow)  # factor in capacity

            return est_pow

        generated_power, _ = quad(estimate_power_at_instant, 0, time)

        actual_power = generated_power * self.solar_panel.performance_ratio
        actual_power = SolarPanel.kilojoule_to_kilowatthour(actual_power)

        return actual_power

    def _load_clf(self):
        with open(self.pkl_path_clf, 'rb') as pkl_file_clf:
            data = pickle.load(pkl_file_clf)

        self.clf = data['model']
        self.poly_feat_clf = data['utility']['poly_feat']
        self.ss_clf = data['utility']['ss']

    def _load_reg(self):
        with open(self.pkl_path_reg, 'rb') as pkl_file_reg:
            data = pickle.load(pkl_file_reg)

        self.reg = data['model']
        self.poly_feat_reg = data['utility']['poly_feat']
        self.ss_reg = data['utility']['ss']

    # ---- Prediction ---- #
    def predict(self, data, lat, lon):
        ow_formatter = DataPreprocessorOpenWeather(data, lat, lon)
        data = ow_formatter.format()

        data_clf = self._transform_data(data, stage='classifier', training=False)
        pred_clf = self.clf.predict(data_clf)

        data_reg = self._transform_data(data, stage='regressor', training=False)
        pred_reg = self.reg.predict(data_reg)

        pred = list()
        for clf_val, reg_val in zip(pred_clf, pred_reg):
            pred.append(reg_val if clf_val else 0)

        self.pred = np.array(pred).reshape(-1, 1)
        self.pred *= 3.6  # Convert from J/m^2/s to kJ/m^2/hr

        self.pw = Piecewise(y=self.pred, x_int=3)
        return self.pred

    # ---- Training ---- #
    def _train(self, verbose=False):
        if verbose:
            print("Downloading Location-based data from PSM3...")
        data = self._load_location_psm3()

        if verbose:
            print("Training Classifier")
        self._train_classifier(data)

        if verbose:
            print("Training Regressor")
        self._train_regressor(data)

        if verbose:
            print('Saving Data')
        self._save()

    def _load_location_psm3(self):
        locations = self._load_location_coordinates()
        loc_dfs = []

        for i, (city, coords) in enumerate(locations.items()):
            print(f"{i + 1}/{len(locations.keys())}")
            lat, lon = coords['latitude'], coords['longitude']

            # Prepare the data for the given location
            self.psm3_api.download(lat, lon, DEFAULT_YEAR)
            self.psm3_api.tabelize()

            # Request the data at said location for the span of a year
            df = self.psm3_api.get_dataframe(t1=(1, 1), t2=(12, 31))

            loc_dfs.append(df)

        psm3_data = pd.concat(loc_dfs)

        # Preprocess the data
        dp_psm3 = DataPreprocessorPSM3(psm3_data)
        psm3_data_formatted = dp_psm3.format()
        return psm3_data_formatted

    def _train_classifier(self, data):
        X = data.drop('DNI', axis=1)
        y = data.DNI

        X = self._transform_data(X, stage='classifier', training=True)

        y = y != 0

        self.clf = DecisionTreeClassifier()
        self.clf.fit(X, y)

    def _train_regressor(self, data):
        data_trimmed = data.loc[data.DNI != 0].copy()
        X = data_trimmed.drop('DNI', axis=1)
        y = data_trimmed.DNI

        X = self._transform_data(X, stage='regressor', training=True)

        self.reg = XGBRegressor()
        self.reg.fit(X, y)

    def _save(self):
        clf_mpkg = ModelPackage(self.clf)
        reg_mpkg = ModelPackage(self.reg)

        clf_mpkg.add_utility('poly_feat', self.poly_feat_clf)
        reg_mpkg.add_utility('poly_feat', self.poly_feat_reg)

        clf_mpkg.add_utility('ss', self.ss_clf)
        reg_mpkg.add_utility('ss', self.ss_reg)

        clf_pkg = clf_mpkg.package()
        reg_pkg = reg_mpkg.package()

        with open(self.pkl_path_clf, 'wb') as pkl_file_clf:
            pickle.dump(clf_pkg, pkl_file_clf)

        with open(self.pkl_path_reg, 'wb') as pkl_file_reg:
            pickle.dump(reg_pkg, pkl_file_reg)

    def _transform_data(self, data, stage, training):
        if training:
            if stage == 'classifier':
                data = self.poly_feat_clf.fit_transform(data)
                data = self.ss_clf.fit_transform(data)
            else:
                data = self.poly_feat_reg.fit_transform(data)
                data = self.ss_reg.fit_transform(data)
        else:
            if stage == 'classifier':
                data = self.poly_feat_clf.transform(data)
                data = self.ss_clf.transform(data)
            else:
                data = self.poly_feat_reg.transform(data)
                data = self.ss_reg.transform(data)
        return data

    @staticmethod
    def _train_test_split(data):
        X = data.drop('DNI', axis=1)
        y = data.DNI

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_SEED)
        return X_train, X_test, y_train, y_test

    def _load_location_coordinates(self):
        with open(self.loc_path, 'r') as locations_yaml:
            locations = yaml.safe_load(locations_yaml)
        return locations
