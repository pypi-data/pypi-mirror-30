from .MachineLearning import UETMachineLearning
import pandas
from sklearn.cluster import AgglomerativeClustering
import operator


class UETClustering(UETMachineLearning):

    def __init__(self, n_cluster=5, modelname='', X=pandas.DataFrame()):
        super().__init__()
        self.n_cluster = n_cluster
        self.modelname = modelname
        self.dataset = X
        self.X = X
        self.type = 'clustering'

    def fit(self):
        self.model = AgglomerativeClustering(n_clusters=self.n_cluster)
        self.transformData()
        self.model.fit(self.X)
        return self.model

    def predict(self, X):
        if self.model is None:
            self.loadModel()
        result = self.model.predict(X)
        return result

    def getLabels(self):
        if self.model is None:
            self.fit()
        labels = self.model.labels_
        return labels

    def bestResult(self):
        if self.model is None:
            self.fit()
        data = pandas.DataFrame(data=self.X, columns=['view', 'post', 'forumview', 'forumpost', 'successsubmission'])
        data['group'] = self.getLabels()
        return data

    def labelGrade(self):
        data = pandas.DataFrame(data=self.dataset)
        column = {
            'w7_view': 'view',
            'w7_post': 'post',
            'w7_forumview': 'forumview',
            'w7_forumpost': 'forumpost',
            'w7_successsubmission': 'successsubmission',
            'w7_grade': 'grade',
            'w15_view': 'view',
            'w15_post': 'post',
            'w15_forumview': 'forumview',
            'w15_forumpost': 'forumpost',
            'w15_successsubmission': 'successsubmission',
            'w15_grade': 'grade'
        }
        data = data.rename(index=str, columns=column)
        data['group'] = self.getLabels()
        tb = {}
        i = 0
        while (i < self.n_cluster):
            temp = data[data.group == i]
            tb[i] = temp.grade.mean()
            i += 1
        sorted_x = sorted(tb.items(), key=operator.itemgetter(1))
        tb[sorted_x[0][0]] = 'F'
        tb[sorted_x[1][0]] = 'D'
        tb[sorted_x[2][0]] = 'C'
        tb[sorted_x[3][0]] = 'B'
        tb[sorted_x[4][0]] = 'A'
        data['group'] = data['group'].map(tb)
        return data
