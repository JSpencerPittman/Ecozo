from DataManager.PSM3 import PSM3API
from SolarIrrad.models.model import SolarIrradModel
from SolarIrrad.preprocessing.bravo import DataPreprocessorPSM3, DataPreprocessorOpenWeather
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from SolarIrrad.models.model import SolarPanel
from scipy.integrate import quad
import pickle
import os

RANDOMSEED = 42
DEFAULT_YEAR = 2014


class Bravo(SolarIrradModel):
    def __init__(self, sp: SolarPanel):
        self.ss = StandardScaler()
        self.poly_feat = PolynomialFeatures(2)
        self.psm3_api = PSM3API(defaults=True)
        self.solar_panel = sp

        self.pkl_path = os.path.join(os.path.dirname(__file__), 'saved/bravo.pkl')

        self.y_test = None
        self.y_train = None
        self.y_pred_test = None
        self.y_pred_train = None
        self.model = None

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

    def train(self):
        psm3_api = PSM3API(defaults=True)
        data = psm3_api.get_dataframe(t1=(1, 1), t2=(12, 31))
        psm3_dataformatter = DataPreprocessorPSM3(data)
        data = psm3_dataformatter.format()

        # Split to input features and labels
        X = data.drop('DNI', axis=1)
        y = data['DNI']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOMSEED)

        X_train_prep = self._transform_data(X_train, True)
        X_test_prep = self._transform_data(X_test)

        rf_reg = RandomForestRegressor(n_estimators=150)
        rf_reg.fit(X_train_prep, y_train)

        y_pred_test = rf_reg.predict(X_test_prep)
        y_pred_train = rf_reg.predict(X_train_prep)

        self.y_test = y_test
        self.y_train = y_train
        self.y_pred_test = y_pred_test
        self.y_pred_train = y_pred_train
        self.model = rf_reg

        self.save()

    def save(self):
        with open(self.pkl_path, 'wb') as pkl_file:
            model_data = {
                'model': self.model,
                'pf': self.poly_feat,
                'ss': self.ss
            }

            pickle.dump(model_data, pkl_file)

    def load(self):
        with open(self.pkl_path, 'rb') as pkl_file:
            model_data = pickle.load(pkl_file)
            self.model = model_data['model']
            self.poly_feat = model_data['pf']
            self.ss = model_data['ss']

    def predict(self, data, lat, lon):
        if self.model is None:
            if os.path.exists(self.pkl_path):
                self.load()
            else:
                self.train()

        ow_dataformatter = DataPreprocessorOpenWeather(data, lat, lon)
        data = ow_dataformatter.format()
        data = self._transform_data(data)
        self.pred = self.model.predict(data)
        self.pred *= 3.6  # Convert from J/m^2/s to kJ/m^2/hr
        return self.pred

    def model_analysis(self):
        def error_report(y_true, y_pred):
            print("MSE:  ", round(mean_squared_error(y_true, y_pred), 3))
            print("RMSE: ", round(mean_squared_error(y_true, y_pred, squared=False), 3))
            print("MAE: ", round(mean_absolute_error(y_true, y_pred), 3))

        print("Testing Error")
        error_report(self.y_test, self.y_pred_test)
        print("Training Error")
        error_report(self.y_train, self.y_pred_train)

    def _transform_data(self, data, training=False):
        if training:
            data = self.poly_feat.fit_transform(data)
            data = self.ss.fit_transform(data)
        else:
            data = self.poly_feat.transform(data)
            data = self.ss.transform(data)
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
