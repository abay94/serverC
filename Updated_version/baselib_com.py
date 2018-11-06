import argparse
import json, requests, time, datetime
import numpy as np
import pandas as pd

from influxdb import InfluxDBClient, DataFrameClient

class Config(object):
    def __init__(self, **kwargs):
        pass

    def _loadJson(self,file):
        with open(file, 'r') as fp:
            list = json.load(fp)
        return list

    def getInfo(self,**kwargs):
        file = kwargs['file']
        source_list = self._loadJson(file)
        return source_list

class Link(object):
    def __init__(self, host, port, user, password, id_name):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.id_name = id_name
        self.dt = self.influxdb_time()
        self.data = None
        self.query = None

    def influxdb_time(self):
        dt = time.time()
        dt = (datetime.datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S'))
        return dt

    def getData(self, query, node, database, **kwargs):
        self.query = query
        data_as_list_df = None
        try:
            if node == 'influxdb':
                data_as_list_df = self.influxdb_client(method='get', database = database)
        except Exception as e:
            print(e)
        finally:
            print('Complete Link.getData() with id {0}'.format(self.id_name))
            return (data_as_list_df)

    def putData(self, data, node, database, **kwargs):
        #self.data_to_put = data
        try:
            if node == 'influxdb':
                self.influxdb_client(data=data, method='put', database = database)
        except Exception as e:
            print(e)
        finally:
            print('Complete Link.putData() with id {0}'.format(self.id_name))

    def influxdb_client(self, data, database, method):
        data_as_list_df = None
        try:
            if method == 'get':
                client_get = DataFrameClient(self.host, self.port, database)
                data_as_list_df = client_get.query(self.query)
            if method == 'put':
                #data_as_list_df = kwargs['data']
                print("database: ", database)
                client_put = DataFrameClient(host=self.host, port=self.port, username='root', password='root', database=database)
                client_put.write_points(data, measurement=self.id_name)
        except Exception as e:
            print(e)
        finally:
            print('Comlete Link.influxdb_client() with id {0}'.format(self.id_name))
            return data_as_list_df

class Model(object):
    def __init__(self, host, port, node, core, id_name, **kwargs):

        self.host = host
        self.port = port
        self.node = node
        self.core = core
        self.id_name = id_name
        self.path = None
        self.name = None
        self.data = None
        self.tag = None
        self.calc = {}
        self.df_time = None

    def execModel(self, path, name, data, tag, **kwargs):
        self.path = path
        self.name = name
        self.data = data
        self.tag = tag
        data_as_json = None
        try:
            if self.core == 'tf-core':
                calculated = self._tf_core(self.data, self.tag)
            if self.core == 'flask-core':
                data_as_json = self.prep_data(self.data, tag, operation='to_json')
                calc = self._flask_core(data_as_json, self.tag)
                calculated = self.prep_data(calc, tag, operation='to_df')

        except Exception as e:
            print(e)
        finally:
            print('Comlete execModel() with id {0} for {1}, complete'.format(self.id_name, self.core))
            return (calculated)

    def _tf_core(self, data, tag):

        # Read an image
        test_X = data
        data = test_X[-14].astype(np.float32)
        #print(data)
        last=test_X[-1:]
        # Wrap bitstring in JSON
        #data = json.dumps({"inputs": float(last)})
        data1 = json.dumps({"inputs": float(1)})
        json_response = requests.post("http://{0}:{1}/{2}/{3}:predict".format(self.host, self.port, self.path, self.name), data=data1)
        print(json_response)
        response = json.loads(json_response.text)
        print(json_response.status_code)
        predicted_value = float(response['outputs'])
        print(predicted_value)
        return predicted_value

    def prep_data(self, data, tag, operation=''):
        data_as_df = None
        data_as_json = None

        if operation=='to_json':
            meta_data = {"model_name":self.name,
                         "maodel_path":self.path,
                         "id_name":self.id_name}
            try:
                df = pd.concat(data)
                self.df_time = df
                df = df.reset_index()
                df = df[tag]
                data_array = df.values
                df_as_json = pd.Series(data_array).to_json(orient='records')
                data_as_json = {"data_frame": df_as_json,
                                "meta_data": meta_data}
            except Exception as e:
                print(e)
            return data_as_json
        if operation=='to_df':
            df = self.df_time.reset_index()
            df = df.set_index('level_1')
            return pd.DataFrame([data], columns=[tag+".predicted", tag+".mse", tag+".actual"], index=df[-1:].index)





    def _flask_core(self, data_as_json, tag):

        response = None
        header = {'Content-Type': 'application/json', 'Accept': 'application/json' }
        try:
            response = requests.post(
                url='http://{0}:{1}/{2}'.format(self.host, self.port, self.name),
                data=json.dumps(data_as_json), headers=header)
            #print('http://{0}:{1}/{2}'.format(self.host, self.port, self.name), json.dumps(data_as_json), header)
            print(response.json())
        except Exception as e:
            print(e)
        finally:
            #print('Comlete Model._flask_core() with id {0} for {1}'.format(self.id_name, self.core))
            return response.json()




