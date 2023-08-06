from sklearn.linear_model import LinearRegression
import pandas
import operator
import pickle
from matplotlib import pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.mixture import BayesianGaussianMixture
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import MeanShift,estimate_bandwidth,SpectralClustering
from UETClustering import UETClustering
from sklearn import metrics
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans
from sklearn.cluster import Birch
from Database import Database
from MoodleBackend import mysql
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import MinMaxScaler
# data = pandas.read_csv('830/export3w(1).csv')
# train = data[list(data.columns[4:9])]
# d2 = pandas.read_csv('830/export7w(1).csv')
# plt.scatter(data['view'], d2['view'],  color='black')
# # plt.plot(diabetes_X_test, diabetes_y_pred, color='blue', linewidth=3)
#
#
# plt.show()
# y = data['letter']
# scaler = MinMaxScaler()
# train = scaler.fit_transform(train)
# classification = DecisionTreeClassifier()
# classification.fit(train,y)
# test = pandas.read_csv('830/test.csv');
# print(list(test['letter']))
# test = test[list(test.columns[4:9])]
# test = scaler.fit_transform(test)
# print(classification.predict(test))
# scores = cross_val_score(classification, train, y)
# print(scores.mean())
# from sklearn.neighbors import KNeighborsClassifier
#
# knn = KNeighborsClassifier(n_neighbors=10)
# knn.fit(train,y)
# print('knn')
# print(knn.predict(test))
#
# scores = cross_val_score(knn, train, y)
# print(scores.mean())
# from sklearn.naive_bayes import GaussianNB,MultinomialNB
#
# gauss = GaussianNB()
# gauss.fit(train,y)
# print('naive')
# print(gauss.predict(test))
#
# scores = cross_val_score(gauss, train, y)
# print(scores.mean())
# multi = MultinomialNB()
# multi.fit(train,y)
# print('multi')
# print(multi.predict(test))
#
# scores = cross_val_score(multi, train, y)
# print(scores.mean())
# from sklearn.svm import SVC,NuSVC,LinearSVC
# svc  = SVC()
# svc.fit(train,y)
# li = LinearSVC()
# li.fit(train,y)
# print('svc')
# print(svc.predict(test))
#
# scores = cross_val_score(svc, train, y)
# print(scores.mean())
# print(li.predict(test))
#
# scores = cross_val_score(li, train, y)
# print(scores.mean())
# from sklearn.linear_model import SGDClassifier
# # clf = SGDClassifier(loss="hinge")
# # clf.fit(train, y)
# # print('sgd')
# # print(clf.predict(test))
#
# from sklearn.ensemble import RandomForestClassifier
# random = RandomForestClassifier(n_estimators=100)
# random.fit(train,y)
# print('random')
# print(random.predict(test))
#
# scores = cross_val_score(random, train, y)
# print(scores.mean())
# from sklearn.ensemble import ExtraTreesClassifier,AdaBoostClassifier
# extra = ExtraTreesClassifier(n_estimators=10, max_depth=None,min_samples_split=2, random_state=0)
# extra.fit(train,y)
# print('extra')
# print(extra.predict(test))
#
#
#
# scores = cross_val_score(extra, train, y)
# print(scores.mean())

# kmean = KMeans(n_clusters=5)
# kmean.fit(train)
# print(train)
# df = pandas.DataFrame(train)
# data['group'] = kmean.labels_
# data.to_csv('/home/bachnguyen/Desktop/test.csv')

# hie = AgglomerativeClustering(n_clusters=5)
# hie.fit(train)
# kmean = KMeans(n_clusters=5,algorithm='elkan')
# kmean.fit(train)
# birch = Birch(n_clusters=5)
# birch.fit(train)
#
#
# gauss = GaussianMixture(n_components=5)
# gauss.fit(train)
# # data['group'] = gauss.predict(train)
# # data.to_csv('/home/bachnguyen/Desktop/resultexportgauss3w.csv',',')
#
# bg = BayesianGaussianMixture(n_components=5)
# bg.fit(train)
#
# print('Silhouette Coefficient')
# print(metrics.silhouette_score(train, kmean.labels_, metric='euclidean'))
# print(metrics.silhouette_score(train, hie.labels_, metric='euclidean'))
# print(metrics.silhouette_score(train, birch.labels_, metric='euclidean'))
# print(metrics.silhouette_score(train, gauss.predict(train), metric='euclidean'))
# print(metrics.silhouette_score(train, bg.predict(train), metric='euclidean'))
#
#
#
#
# print('Calinski-Harabaz Index')
# print(metrics.calinski_harabaz_score(train, kmean.labels_) )
# print(metrics.calinski_harabaz_score(train, hie.labels_) )
# print(metrics.calinski_harabaz_score(train, birch.labels_) )
# print(metrics.calinski_harabaz_score(train, gauss.predict(train)) )
# print(metrics.calinski_harabaz_score(train, bg.predict(train)) )



# db = Database(mysql)
# data = db.readDataset()
# dataset = pandas.DataFrame(data[['15w_view', '15w_post', '15w_forumview', '15w_forumpost', '15w_successsubmission','15w_grade']])

#
# hie = AgglomerativeClustering(n_clusters=5)
# hie.fit(dataset)
# kmean = KMeans(n_clusters=5)
# kmean.fit(dataset)
# birch = Birch(n_clusters=5)
# birch.fit(dataset)
# print('Silhouette Coefficient')
# print(metrics.silhouette_score(dataset, kmean.labels_, metric='euclidean'))
# print(metrics.silhouette_score(dataset, hie.labels_, metric='euclidean'))
# print(metrics.silhouette_score(dataset, birch.labels_, metric='euclidean'))
#
# print('Calinski-Harabaz Index')
# print(metrics.calinski_harabaz_score(dataset, kmean.labels_) )
# print(metrics.calinski_harabaz_score(dataset, hie.labels_) )
# print(metrics.calinski_harabaz_score(dataset, birch.labels_) )


# dataset['group'] = kmean.labels_
# dataset.to_csv('/home/bachnguyen/Desktop/a.csv')
#








# bg = BayesianGaussianMixture(n_components=3)
# bg.fit(train)
# data['group'] = bg.predict(train)
# data.to_csv('model/cluster/15wgauss.csv',',')
#
# kmean = KMeans(n_clusters=3)
# kmean.fit(train)
#
#
# data['group'] = kmean.labels_
# distances = kmean.transform(train)
# i = 0
# d = []
# for group in kmean.labels_:
#     d.append(distances[i][group])
#     i+=1
#
# data['distance'] = d
# data.to_csv('model/cluster/15w.csv')

# ag = AgglomerativeClustering(n_clusters=3)
# ag.fit(train)
# data['group'] = ag.labels_
# data.to_csv('model/cluster/15whi.csv')

# bandwidth = estimate_bandwidth(train, quantile=0.2, n_samples=500)
# ms = MeanShift(bandwidth=bandwidth,bin_seeding=True)
# ms.fit(train)
# data['group'] = ms.labels_
# data.to_csv('model/cluster/15wmeanshift.csv')

# spectral = SpectralClustering(n_clusters=3)
# spectral.fit(train)
# data['group'] = spectral.labels_
# data.to_csv('model/cluster/85915wspectral.csv')

#
connection = mysql.connect()
cursor = connection.cursor()
w3 = pandas.read_csv('830/export3w(1).csv')
w3 = w3.drop('grade', 1)
w6 = pandas.read_csv('830/export6w(1).csv')
w6 = w6.drop('grade', 1)
w7 = pandas.read_csv('830/export7w(1).csv')
w7 = w7.drop('grade', 1)
w10 = pandas.read_csv('830/export10w(1).csv')
w10 = w10.drop('grade', 1)
w13 = pandas.read_csv('830/export13w(1).csv')
w13 = w13.drop('grade', 1)
w15 = pandas.read_csv('830/export15w(1).csv')
w15 = w15.drop('grade', 1)
dataframe = pandas.DataFrame()
r = {}
test = w3.merge(w6, on=['stt', 'courseid', 'userid', 'studentName'], suffixes=('_3w', '_6w'))
test = test.merge(w7, on=['stt', 'courseid', 'userid', 'studentName'], suffixes=('_7w', '_7w'))
test = test.merge(w10, on=['stt', 'courseid', 'userid', 'studentName'], suffixes=('', '_10w'))
test = test.merge(w13, on=['stt', 'courseid', 'userid', 'studentName'], suffixes=('', '_13w'))
test = test.merge(w15, on=['stt', 'courseid', 'userid', 'studentName'], suffixes=('', '_15w'))
wg = pandas.read_csv('830/export7w.csv')
wg = wg[['stt', 'courseid', 'userid', 'studentName','grade']]
test = test.merge(wg,on=['stt', 'courseid', 'userid', 'studentName'],suffixes=('', '_7w'))
# cursor.execute('select count(*) from uet_dataset')
wg = pandas.read_csv('830/export15w.csv')
wg = wg[['stt', 'courseid', 'userid', 'studentName','grade']]
test = test.merge(wg,on=['stt', 'courseid', 'userid', 'studentName'],suffixes=('', '_15w'))
# rc = cursor.fetchone()
test = test.drop(['stt', 'studentName'],1)
for index, row in test.iterrows():
    num =  index
    sql = 'INSERT INTO mdl_uet_dataset VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    values = [num]
    values += row.tolist()
    print(sql)
    cursor.execute(sql,tuple(values))
connection.commit()
