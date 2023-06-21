from abc import ABC, abstractmethod


class DataPreprocessor(ABC):
    def __init__(self, data):
        self.data = data

    @abstractmethod
    def format(self):
        pass
