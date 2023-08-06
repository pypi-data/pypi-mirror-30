import pandas as pd
import pickle
from .UETRegressor import UETRegressor
from .UETClustering import UETClustering
from .UETClassification import UETClassification
from .Database import Database
import os


class UETAnalytics:

    def __init__(self,filepath):
        self.dataset = []
        self.filepath = filepath

    # load data from db
    def loadData(self, nrow=10000):
        db = Database()
        self.dataset = db.readDataset()

    def loadModel(self, modelname, type):
        db = Database()
        version = db.checkModelVersion(modelname)
        filename = self.filepath + '/model/' + modelname + '_' + type + '_' + str(version)
        return pickle.load(open(filename, 'rb'))

    def createModel(self):
        self.loadData()
        columns = ['view', 'post', 'forumview', 'forumpost', 'successsubmission']
        weeks = ['3', '6', '10', '13']
        for week in weeks:
            for column in columns:
                modelname = week + 'w_15w_' + column
                self.regression(modelname, 'w' + week + '_' + column, 'w15_' + column)
                if int(week) < 7:
                    modelname = week + 'w_7w_' + column
                    self.regression(modelname, 'w' + week + '_' + column, 'w7_' + column)
        week7 = self.clustering('7w',
                                ['w7_view', 'w7_post', 'w7_forumview', 'w7_forumpost', 'w7_successsubmission',
                                 'w7_grade'])
        week15 = self.clustering('15w',
                                 ['w15_view', 'w15_post', 'w15_forumview', 'w15_forumpost', 'w15_successsubmission',
                                  'w15_grade'])
        self.classifcation('15w',
                           ['view', 'post', 'forumview', 'forumpost', 'successsubmission'], 'group',
                           week15)
        self.classifcation('7w',
                           ['view', 'post', 'forumview', 'forumpost', 'successsubmission'], 'group',
                           week7)

    def predict(self, week, data):
        columns = ['view', 'post', 'forumview', 'forumpost', 'successsubmission']
        predictdata = {}
        regressiondata = {}
        if week < 7:
            for column in columns:
                modelname = str(week) + 'w_7w_' + column
                model = self.loadModel(modelname=modelname, type='regressor')
                regressiondata[column] = model.predict(data[column])[0]
            model = self.loadModel('7w', 'classification')
            temp = [[regressiondata['view'], regressiondata['post'], regressiondata['forumview'],
                     regressiondata['forumpost'], regressiondata['successsubmission']]]
            predictdata['w7'] = model.predict(temp)[0]
        if week == 7:
            model = self.loadModel('7w', 'classification')
            temp = [[data['view'], data['post'], data['forumview'],
                     data['forumpost'], data['successsubmission']]]
            predictdata['w7'] = model.predict(temp)[0]
        if week < 15:
            for column in columns:
                modelname = str(week) + 'w_15w_' + column
                model = self.loadModel(modelname=modelname, type='regressor')
                regressiondata[column] = model.predict(data[column])[0]
            model = self.loadModel('15w', 'classification')
            temp = [[regressiondata['view'], regressiondata['post'], regressiondata['forumview'],
                     regressiondata['forumpost'], regressiondata['successsubmission']]]
            predictdata['w15'] = model.predict(temp)[0]
        if week == 15:
            model = self.loadModel('15w', 'classification')
            temp = [[data['view'], data['post'], data['forumview'],
                     data['forumpost'], data['successsubmission']]]
            predictdata['w15'] = model.predict(temp)[0]
        return predictdata

    def regression(self, modelname, columnX, columnY):
        X = self.dataset[columnX]
        y = self.dataset[columnY]
        uet = UETRegressor(modelname=modelname, X=X, y=y,filepath=self.filepath)
        uet.fit()
        uet.saveModel()

    def classifcation(self, modelname, columnX, columnY, traindata=[]):
        X = traindata[columnX]
        y = traindata[columnY]
        uet = UETClassification(modelname=modelname, X=X, y=y,filepath=self.filepath)
        uet.fit()
        uet.saveModel()

    def clustering(self, modelname, columnXs):
        X = self.dataset[columnXs]
        uet = UETClustering(n_cluster=5, X=X, modelname=modelname,filepath=self.filepath)
        uet.saveModel()
        best = uet.labelGrade()
        return best
