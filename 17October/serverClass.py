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
    def __init__(self, ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, OUT_ip_addr, OUT_port, OUT_username, OUT_userpass, SRC_node, SRC_database, SRC_measurement, model_name, model_dir, rate, OUT_node, OUT_database, OUT_measurement):

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
        self.rate = rate

        self.OUT_ip_addr = OUT_ip_addr
        self.OUT_port = OUT_port
        self.OUT_username = OUT_username
        self.OUT_userpass = OUT_userpass
        self.OUT_node = OUT_node
        self.OUT_database = OUT_database
        self.OUT_measurement = OUT_measurement

        self.LinkAgentIN = Link(SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_database, SRC_node)
        self.LinkAgentOUT = Link(OUT_ip_addr, OUT_port, OUT_username, OUT_userpass, OUT_database, OUT_node)


    def get_raw_data_from_source(self):


        if (self.model_name == "ARIMA"):

            query_body = "SELECT " + self.ch_name + " from " + self.SRC_measurement + " WHERE time > now() - 30m;"

            self.send_data_as_df = self.LinkAgentIN.query(query_body)




    def send_raw_data_to_ml(self):


        if (self.model_name != "tf-serving"):

            header = {'Content-Type': 'application/json',

                      'Accept': 'application/json'}

            data_sending_for_flask = {}

            self.send_data_as_df['model_dir'] = self.model_dir

            print(self.send_data_as_df)

            raw_data_in_json = self.send_data_as_df.to_json(orient='columns')         ########<<<<<<<<<<<<<<<<<<<<<<<<<<


            try:
                self.response_from_ml = requests.post(
                    url='http://localhost:5000/{0}'.format(self.model_name),
                    data=json.dumps(raw_data_in_json), headers=header)
                print("Send raw data to ml for model {0}. Request is done correctly for {1} ".format(self.model_name, self.ch_name))
                print(self.response_from_ml.json())
            except Exception as e:
                print(e)


    def put_preprocessed_data_to_db(self):

        if (self.OUT_node == "influxdb") and (self.model_name == "ARIMA"):


            json_body_to_influx_in_list = self.response_from_ml


            print (json_body_to_influx_in_list.json())                                  ########<<<<<<<<<<<<<<<<<<<<<<<<<<

            putting_data_in_list = json_body_to_influx_in_list.json()

            self.LinkAgentOUT.write_data_to_influx(putting_data_in_list, self.OUT_measurement,  self.ch_name)


