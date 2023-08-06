import pickle
from abc import ABC
from abc import abstractmethod
from .Database import Database
from sklearn import preprocessing
import os


class UETMachineLearning(ABC):

    def __init__(self):
        self.model = None
        self.modelname = ""
        self.type = ""
        self.X = []
        self.y = []

    def filterData(self):
        pass

    def transformData(self):
        scaler = preprocessing.MinMaxScaler()
        self.X = scaler.fit_transform(self.X)
        # self.y = scaler.fit_transform(self.y)
        return self.X

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def predict(self, X):
        pass

    def saveModel(self):
        if self.model is None:
            self.fit()
        db = Database()
        version = int(db.checkModelVersion(self.modelname)) + 1
        filename = os.path.dirname(os.path.realpath(__file__)) +'/model/' + self.modelname + '_' + self.type + '_' + str(version)
        pickle.dump(self.model, open(filename, 'wb'),protocol=2)
        db.saveModelVersion(self.modelname, self.type, version)
        return self.model

    def loadModel(self):
        db = Database()
        version = db.checkModelVersion(self.modelname)
        if version == 0:
            self.saveModel()
            version = 1
        filename = os.path.dirname(os.path.realpath(__file__)) +'/model/' + self.modelname + '_' + self.type + '_' + str(version)
        self.model = pickle.load(open(filename, 'rb'))
        return self.model
