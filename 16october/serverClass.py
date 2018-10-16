import pandas as pd
from influxdb import InfluxDBClient, DataFrameClient
import json
import time
import datetime
import statsmodels.api as sm
import statsmodels
from LinkClass import Link
import requests


time_calc = []


class Channel_object():
    def __init__(self, ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_source_type, SRC_db_name, SRC_measurement,
                 model_name, model_dir, rate, OUT_node, OUT_database, OUT_measurement):

        self.SRC_ip_addr = SRC_ip_addr
        self.SRC_port = SRC_port
        self.SRC_username = SRC_username
        self.SRC_userpass = SRC_userpass
        self.SRC_measurement = SRC_measurement
        self.SRC_source_type = SRC_source_type

        self.ch_name = ch_name
        self.model_name = model_name
        self.model_dir = model_dir
        self.rate = rate

        self.OUT_node = OUT_node
        self.OUT_database = OUT_database
        self.OUT_measurement = OUT_measurement

        self.LinkAgent = Link(SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_db_name, SRC_source_type)


    def get_raw_data_from_source(self):


        if (self.model_name == "ARIMA"):

            query_body = "SELECT " + self.ch_name + " from " + self.SRC_measurement + " WHERE time > now() - 30m;"

            self.send_data_as_df = self.LinkAgent.query(query_body)




    def send_raw_data_to_ml(self):


        if (self.model_name != "tf-serving"):

            header = {'Content-Type': 'application/json',

                      'Accept': 'application/json'}

            data_sending_for_flask = {}

            data_sending_for_flask[self.ch_name] = self.send_data_as_df

            data_sending_for_flask_2 = json.dumps(data_sending_for_flask)

            try:
                self.response_from_ml = requests.post(
                    url='http://localhost:5000/{0}'.format(self.model_name),
                    data=json.dumps(data_sending_for_flask_2), headers=header)
                print("Send raw data to ml for model {0}. Request is done correctly for {1} ".format(self.model_name, self.ch_name))

            except Exception as e:
                print(e)


    def put_preprocessed_data_to_db(self):

        if (self.OUT_node == "influxdb") and (self.model_name == "ARIMA"):


            json_body_to_influx_in_list = self.response_from_ml

            for i in range(len(json_body_to_influx_in_list)):

                self.LinkAgent.write_data_to_influx(json_body_to_influx_in_list[i])



