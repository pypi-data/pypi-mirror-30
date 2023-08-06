import pandas
import datetime
import MySQLdb


class Database:
    def __init__(self):
        self.connection = MySQLdb.connect(host='localhost', user=
        'root', passwd='quangbach1', db='moodle')

    def readDataset(self):
        sql = 'SELECT * FROM mdl_uet_dataset'
        data = pandas.read_sql(sql=sql, con=self.connection)
        return data

    def checkModelVersion(self, modelname):
        cur = self.connection.cursor()
        sql = 'SELECT * FROM mdl_uet_models WHERE model_name = %s AND status=1 '
        cur.execute(sql, (modelname,))
        version = cur.fetchone()
        cur.close()
        if version is None:
            return 0
        else:
            return version[3]

    def saveModelVersion(self, modelname, type, version):
        cur = self.connection.cursor()
        sql = 'SELECT * FROM mdl_uet_models WHERE model_name = %s AND status=1 '
        cur.execute(sql, (modelname,))
        for row in cur:
            if row is not None:
                sql = 'UPDATE mdl_uet_models SET status=0,modified_at=%s WHERE id=%s'
                cur.execute(sql, (datetime.datetime.now(), row[0],))
        sql = 'INSERT INTO mdl_uet_models (model_name,type,version,status,created_at) VALUES (%s,%s,%s,%s,%s)'
        values = (modelname, type, version, 1, datetime.datetime.now())
        success = cur.execute(sql, values)
        self.connection.commit()
        cur.close()
        return success
