import pandas as pd
from influxdb import InfluxDBClient, DataFrameClient
import json
import time
import datetime
import statsmodels.api as sm
import statsmodels
from LinkClass import Link
import requests
import ast

from grpc.beta import implementations
import tensorflow as tf
import numpy

from tensorflow.core.framework import types_pb2
from tensorflow.python.platform import flags
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2


time_calc = []


class Channel_object():
    def __init__(self, ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, OUT_ip_addr, OUT_port, OUT_username, OUT_userpass, SRC_node, SRC_database, SRC_measurement, model_name, model_dir, OUT_node, OUT_database, OUT_measurement, ML_core_ip_addr, ML_core_port,ML_core_type, query, ch_name_dest_1, ch_name_dest_2, ch_name_dest_3):

        self.SRC_ip_addr = SRC_ip_addr
        self.SRC_port = SRC_port
        self.SRC_username = SRC_username
        self.SRC_userpass = SRC_userpass
        self.SRC_measurement = SRC_measurement
        self.SRC_node = SRC_node
        self.SRC_database = SRC_database

        self.ch_name = ch_name
        self.model_name = model_name
        self.model_dir = model_dir
        #self.rate = rate

        self.OUT_ip_addr = OUT_ip_addr
        self.OUT_port = OUT_port
        self.OUT_username = OUT_username
        self.OUT_userpass = OUT_userpass
        self.OUT_node = OUT_node
        self.OUT_database = OUT_database
        self.OUT_measurement = OUT_measurement

        self.LinkAgentIN = Link(SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_database, SRC_node)
        self.LinkAgentOUT = Link(OUT_ip_addr, OUT_port, OUT_username, OUT_userpass, OUT_database, OUT_node)

        self.ML_core_ip_addr = ML_core_ip_addr
        self.ML_core_port = ML_core_port
        self.ML_core_type = ML_core_type

        self.query = query
        self.ch_name_dest_1 = ch_name_dest_1
        self.ch_name_dest_2 = ch_name_dest_2
        self.ch_name_dest_3 = ch_name_dest_3


    def get_raw_data_from_source(self):


        self.send_data_as_df = self.LinkAgentIN.query(self.query)

        self.current_time = pd.to_datetime(self.send_data_as_df.index.values[-1])           #<<<<<<<<<<<<<<<<<<   memorizee the time of the last query




    def send_raw_data_to_ml(self):


        if (self.ML_core_type != "tf-core"):           #<<<<<<<<<<<<<<<<<<< this part for models in flask

            header = {'Content-Type': 'application/json',

                      'Accept': 'application/json'}

            self.send_data_as_df['model_dir'] = self.model_dir



            raw_data_in_json = self.send_data_as_df.to_json(orient='columns')         ########<<<<<<<<<<<<<<<<<<<<<<<<<<


            try:
                self.response_from_ml = requests.post(
                    url='http://{0}:{1}/{2}'.format(self.ML_core_ip_addr, self.ML_core_port, self.model_name),
                    data=json.dumps(raw_data_in_json), headers=header)
                print("Send raw data to ml for model {0}. Request is done correctly for {1} ".format(self.model_name, self.ch_name))
                #print(self.response_from_ml.json())
            except Exception as e:
                print(e)
        else:            #<<<<<<<<<<<<<<<<<<< this part for models in tf-seving


            tf.app.flags.DEFINE_string('server', '192.168.1.77:8501',
                                       'inception_inference service host:port')
            FLAGS = tf.app.flags.FLAGS

            data_pred = self.send_data_as_df["value"].values.tolist()

            print("dataaaa_preeeed:: ",data_pred)

            data_for_pred = numpy.float32(data_pred[-2:])
            # Prepare request
            request = predict_pb2.PredictRequest()
            request.model_spec.name = self.model_name
            request.inputs['inputs'].dtype = types_pb2.DT_FLOAT
            request.inputs['inputs'].CopyFrom(
                tf.contrib.util.make_tensor_proto(data_for_pred))
            request.output_filter.append('outputs')
            # Send request
            host, port = FLAGS.server.split(':')
            channel = implementations.insecure_channel(host, int(port))

            print("host and port : ", host, port)
            print(channel)
            stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
            prediction = stub.Predict(request, 5.0)  # 5 secs timeout              # <<<<<<<<<<<<<<< ERRRRROOOORRRRRR
            print("predictiiiioooon: ",prediction)
            floats = prediction.outputs['outputs'].int64_val
            predicted_array = numpy.asarray(floats)
            print("prediction FROM TFFFF: ", predicted_array)

            self.response_from_ml = predicted_array[-1]



    def add_seconds(self, needed_time):
        needed_time_1 = pd.to_datetime(needed_time)
        needed_time_2 = needed_time_1 + datetime.timedelta(0, 10)
        return pd.tslib.Timestamp(needed_time_2)


    def put_preprocessed_data_to_db(self):

        if (self.OUT_node == "influxdb") and (self.model_name == "ARIMA"):


            json_body_to_influx_in_list = self.response_from_ml


            putting_data_in_list = json_body_to_influx_in_list.json()

            time_calc = dict()

            time_calc[0] = self.current_time

            for i in range(len(putting_data_in_list) - 1):
                time_calc[i + 1] = self.add_seconds(time_calc[i])

            print("Current time", self.current_time)
            json_influx = [
                {
                    "measurement": self.OUT_measurement,
                    "time": self.current_time,
                    "fields": {
                        str(self.ch_name + "_predicted"): putting_data_in_list[0],
                        str(self.ch_name + "_mse"): putting_data_in_list[1],
                        str(self.ch_name + "_live"): putting_data_in_list[2]
                    }
                }
            ]

            self.LinkAgentOUT.write_data_to_influx(json_influx)

        if (self.OUT_node == "influxdb") and (self.ML_core_type == "tf-core"):


            json_influx = [
                {
                    "measurement": self.OUT_measurement,
                    "time": self.current_time,
                    "fields": {
                        str(self.ch_name + "_predicted_tf"): putting_data_in_list[0],
                        str(self.ch_name + "_mse_tf"): putting_data_in_list[1],
                        str(self.ch_name + "_live"): putting_data_in_list[2]
                    }
                }
            ]

            self.LinkAgentOUT.write_data_to_influx(json_influx)

        if (self.OUT_node == "influxdb") and (self.ML_core_type == "flask-core"):

            json_body_to_influx_in_list = self.response_from_ml

            putting_data_in_list = json_body_to_influx_in_list.json()


            json_influx = [
                {
                    "measurement": self.OUT_measurement,
                    "time": self.current_time,
                    "fields": {
                        str(self.ch_name + "_predicted_hwtr"): putting_data_in_list[0],
                        str(self.ch_name + "_mse_hwtr"): putting_data_in_list[1],
                        str(self.ch_name + "_live"): putting_data_in_list[2]
                    }
                }
            ]

            self.LinkAgentOUT.write_data_to_influx(json_influx)




