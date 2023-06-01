from DataManager.PSM3 import PSM3API
from DataManager.OpenWeather import OpenWeatherAPI
from SolarIrrad.models.model import SolarIrradModel
#from SolarIrrad.DataFormatter import PSM3DataFormatter, OWDataFormatter
from SolarIrrad.preprocessing.bravo import DataPreprocessorPSM3, DataPreprocessorOpenWeather
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

RANDOMSEED = 42
DEFAULT_YEAR = 2014


class PSM3Alpha(SolarIrradModel):
    def __init__(self):
        self.ss = StandardScaler()
        self.poly_feat = PolynomialFeatures(2)
        self.psm3_api = PSM3API(defaults=True)

        self.y_test = None
        self.y_train = None
        self.y_pred_test = None
        self.y_pred_train = None
        self.model = None

        self.pred = None

    def hour(self):
        pass

    def day(self):
        return -1

    def five_days(self):
        return -1

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

    def predict(self, data, lat, lon):
        ow_dataformatter = DataPreprocessorOpenWeather(data, lat, lon)
        data = ow_dataformatter.format()
        data = self._transform_data(data)
        self.pred = self.model.predict(data)
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
