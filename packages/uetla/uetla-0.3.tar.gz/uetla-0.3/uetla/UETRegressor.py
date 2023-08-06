from .MachineLearning import UETMachineLearning
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
import numpy as np


class UETRegressor(UETMachineLearning):

    def __init__(self, modelname='', X=[], y=[],filepath=''):
        super().__init__()
        self.modelname = modelname
        self.X = X
        self.y = y
        self.type = 'regressor'
        self.filepath = filepath

    def fit(self):
        self.model = LinearRegression()
        if len(self.X.shape) == 1:
            self.X = np.reshape(self.X,(-1,1))
        self.transformData()
        self.model.fit(self.X, self.y)
        return self.model

    def predict(self, X):
        if self.model is None:
            self.loadModel()
        if not X.shape[1]:
            X = np.reshape(X, (-1, 1))
        result = self.model.predict(X)
        return result



