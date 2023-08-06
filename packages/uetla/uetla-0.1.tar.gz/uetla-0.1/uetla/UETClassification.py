from .MachineLearning import UETMachineLearning
from sklearn.naive_bayes import GaussianNB


class UETClassification(UETMachineLearning):
    def __init__(self, modelname='', X=[], y=[]):
        super().__init__()
        self.modelname = modelname
        self.X = X
        self.y = y
        self.type = 'classification'

    def fit(self):
        self.model = GaussianNB()
        self.model.fit(self.X, self.y)
        return self.model

    def predict(self, X):
        if self.model is None:
            self.loadModel()
        result = self.model.predict([X])
        return result
