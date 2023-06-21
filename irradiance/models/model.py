from abc import ABC, abstractmethod
from sklearn.metrics import (mean_squared_error, mean_absolute_error,
                             accuracy_score, precision_score,
                            recall_score, confusion_matrix)


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


class Results(object):
    def __init__(self, type):
        self.type = type

        self.train = dict()
        self.test = dict()

    def save_results(self, y_true, y_pred, training):
        results = dict()

        if self.type == 'classifier':
            results['acc'] = round(accuracy_score(y_true, y_pred), 3)
            results['prec'] = round(precision_score(y_true, y_pred), 3)
            results['rec'] = round(recall_score(y_true, y_pred), 3)
            results['conf_mat'] = confusion_matrix(y_true, y_pred)
        else:
            results['mse'] = round(mean_squared_error(y_true, y_pred, squared=True), 3)
            results['rmse'] = round(mean_squared_error(y_true, y_pred, squared=False), 3)
            results['mae'] = round(mean_absolute_error(y_true, y_pred), 3)

        if training:
            self.train = results
        else:
            self.test = results

    def report(self):
        if self.type == 'classifier':
            self._classification_report()
        else:
            self._regression_report()

    def _classification_report(self):
        if self.train is not None:
            print("Training")
            print("Accuracy: ", self.train['acc'])
            print("Precision: ", self.train['prec'])
            print("Recall: ", self.train['rec'])
            print("Confusion Matrix: \n", self.train['conf_mat'])
        if self.test is not None:
            print("Testing")
            print("Accuracy: ", self.test['acc'])
            print("Precision: ", self.test['prec'])
            print("Recall: ", self.test['rec'])
            print("Confusion Matrix: \n", self.test['conf_mat'])

    def _regression_report(self):
        if self.train is not None:
            print("Training")
            print("MSE: ", self.train['mse'])
            print("RMSE: ", self.train['rmse'])
            print("MAE: ", self.train['mae'])
        if self.test is not None:
            print("Testing")
            print("MSE: ", self.test['mse'])
            print("RMSE: ", self.test['rmse'])
            print("MAE: ", self.test['mae'])


class ModelPackage(object):
    def __init__(self, model):
        self.model = model
        self.utilities = dict()

    def add_utility(self, name, util):
        self.utilities[name] = util

    def package(self):
        pkg = dict()
        pkg['model'] = self.model
        pkg['utility'] = self.utilities
        return pkg
