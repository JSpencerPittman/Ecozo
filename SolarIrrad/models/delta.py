import yaml

from DataManager.PSM3 import PSM3API
from SolarIrrad.models.model import SolarIrradModel, Results, ModelPackage
from SolarIrrad.preprocessing.bravo import DataPreprocessorPSM3, DataPreprocessorOpenWeather
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from SolarIrrad.models.model import SolarPanel
from scipy.integrate import quad
import pickle
import os
import pandas as pd
import numpy as np

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
        self.rf_clf = None
        self.rf_reg = None

        self.psm3_api = PSM3API()
        self.solar_panel = sp

        self.dp_psm3 = None
        self.dp_ow = None

        self.pkl_path = os.path.join(os.path.dirname(__file__), 'saved/delta.pkl')
        self.loc_path = os.path.join(os.path.dirname(__file__), '../locations.yaml')

        self.results_clf = Results("classifier")
        self.results_reg = Results("regressor")
        self.results_hyb = Results("regressor")

        self.pred = None

    def hour(self):
        exposure = self._calc_irrads(1)
        return self._calc_power(exposure)

    def day(self):
        exposure = self._calc_irrads(8)
        return self._calc_power(exposure)

    def five_days(self):
        exposure = self._calc_irrads(40)
        return self._calc_power(exposure)

    def month(self):
        return -1

    def year(self):
        return -1

    def train(self, verbose=False):
        if verbose:
            print("Downloading Location-based data from PSM3...")
        self._load_location_psm3()
        if verbose:
            print("Training Classifier")
        self._train_classifier()
        if verbose:
            print("Training Regressor")
        self._train_regressor()
        if verbose:
            print("Evaluating Hybrid Model")
        self._evaluate_hybrid()
        if verbose:
            print('Saving Data')
        self.save()

    def _train_classifier(self):
        X_train, X_test, y_train, y_test = self._train_test_split(self.psm3_data)
        X_train = self._transform_data(X_train, stage='classifier', training=True)
        X_test = self._transform_data(X_test, stage='classifier', training=False)

        # True - I > 0
        # False - I = 0
        y_train = y_train != 0
        y_test = y_test != 0

        self.rf_clf = RandomForestClassifier()
        self.rf_clf.fit(X_train, y_train)

        pred_train = self.rf_clf.predict(X_train)
        pred_test = self.rf_clf.predict(X_test)

        self.results_clf.save_results(y_train, pred_train, training=True)
        self.results_clf.save_results(y_test, pred_test, training=False)

    def _train_regressor(self):
        data = self.psm3_data.loc[self.psm3_data.DNI != 0].copy()
        X_train, X_test, y_train, y_test = self._train_test_split(data)
        X_train = self._transform_data(X_train, stage='regressor', training=True)
        X_test = self._transform_data(X_test, stage='regressor', training=False)

        self.rf_reg = RandomForestRegressor()
        self.rf_reg.fit(X_train, y_train)

        pred_train = self.rf_reg.predict(X_train)
        pred_test = self.rf_reg.predict(X_test)

        self.results_reg.save_results(y_train, pred_train, training=True)
        self.results_reg.save_results(y_test, pred_test, training=False)

    def _evaluate_hybrid(self):
        X = self.psm3_data.drop('DNI', axis=1)
        y = self.psm3_data.DNI

        pred = self._hybrid_predict(X)

        self.results_hyb.save_results(y, pred, training=False)

    def _hybrid_predict(self, data):
        data_clf = self._transform_data(data, stage='classifier', training=False)
        data_reg = self._transform_data(data, stage='regressor', training=False)

        pred_clf = self.rf_clf.predict(data_clf)
        pred_reg = self.rf_reg.predict(data_reg)

        pred = list()
        for clf_val, reg_val in zip(pred_clf, pred_reg):
            pred.append(reg_val if clf_val else 0)
        pred = np.array(pred).reshape(-1, 1)

        return pred

    @staticmethod
    def _train_test_split(data):
        X = data.drop('DNI', axis=1)
        y = data.DNI

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_SEED)
        return X_train, X_test, y_train, y_test

    def _load_location_psm3(self):
        locations = self._load_location_coordinates()
        loc_dfs = []

        for i, (city, coords) in enumerate(locations.items()):
            print(f"{i + 1}/{len(locations.keys())}")
            lat, lon = coords['latitude'], coords['longitude']

            # Prepare the data for the given location
            self.psm3_api.calibrate(lat, lon, DEFAULT_YEAR)

            self.psm3_api.download()
            self.psm3_api.tabelize()

            # Request the data at said location for the span of a year
            df = self.psm3_api.get_dataframe(t1=(1, 1), t2=(12, 31))

            loc_dfs.append(df)

        self.psm3_data = pd.concat(loc_dfs)

        # Preprocess the data
        self.dp_psm3 = DataPreprocessorPSM3(self.psm3_data)
        self.psm3_data = self.dp_psm3.format()

    def _load_location_coordinates(self):
        with open(self.loc_path, 'r') as locations_yaml:
            locations = yaml.safe_load(locations_yaml)
        return locations

    def save(self):
        clf_mpkg = ModelPackage(self.rf_clf)
        reg_mpkg = ModelPackage(self.rf_reg)

        clf_mpkg.add_utility('poly_feat', self.poly_feat_clf)
        reg_mpkg.add_utility('poly_feat', self.poly_feat_reg)

        clf_mpkg.add_utility('ss', self.ss_clf)
        reg_mpkg.add_utility('ss', self.ss_reg)

        clf_mpkg.add_utility('results', self.results_clf)
        reg_mpkg.add_utility('results', self.results_reg)

        clf_pkg = clf_mpkg.package()
        reg_pkg = reg_mpkg.package()

        data = {
            'hyb_results': self.results_hyb,
            'clf': clf_pkg,
            'reg': reg_pkg
        }

        with open(self.pkl_path, 'wb') as pkl_file:
            pickle.dump(data, pkl_file)

    def load(self):
        with open(self.pkl_path, 'rb') as pkl_file:
            data = pickle.load(pkl_file)

        self.results_hyb = data['hyb_results']

        self.rf_clf = data['clf']['model']
        self.poly_feat_clf = data['clf']['utility']['poly_feat']
        self.ss_clf = data['clf']['utility']['ss']
        self.results_clf = data['clf']['utility']['results']

        self.rf_reg = data['reg']['model']
        self.poly_feat_reg = data['reg']['utility']['poly_feat']
        self.ss_reg = data['reg']['utility']['ss']
        self.results_reg = data['reg']['utility']['results']

    def predict(self, data, lat, lon):
        if self.rf_clf is None or self.rf_reg is None:
            if os.path.exists(self.pkl_path):
                self.load()
            else:
                self.train()

        ow_dataformatter = DataPreprocessorOpenWeather(data, lat, lon)
        data = ow_dataformatter.format()

        self.pred = self._hybrid_predict(data)
        self.pred *= 3.6  # Convert from J/m^2/s to kJ/m^2/hr

        return self.pred

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

    def _calc_irrads(self, time):
        capacity = self.solar_panel.capacity  # Watts
        capacity *= 3.6  # kJ/hr

        def derive_line(pred_index):
            p1, p2 = self.pred[pred_index], self.pred[pred_index + 1]
            slope = (1 / 3) * (p2 - p1)
            y_intercept = p2 - (3 * slope)

            def line(x):
                return slope * x + y_intercept

            def limited_line(x):
                return min(line(x), capacity)

            return limited_line

        sum_irrads = 0
        i = 0

        while time >= 3:
            f = derive_line(i)

            results, _ = quad(f, 0, 3)
            sum_irrads += results

            i += 1
            time -= 3

        if time > 0:
            f = derive_line(i)

            results, _ = quad(f, 0, time)
            sum_irrads += results

        return sum_irrads

    def _calc_power(self, exposure):
        power_exposed = exposure * self.solar_panel.area
        power_useable = power_exposed * self.solar_panel.efficiency * self.solar_panel.performance_ratio
        generated_power = SolarPanel.kilojoule_to_kilowatthour(power_useable)
        return generated_power
