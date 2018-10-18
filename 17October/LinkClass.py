#!/home/user/anaconda3/bin/python
import json
import requests
import mysql.connector
import datetime

header = {'Content-Type': 'application/json', \
                  'Accept': 'application/json'}

import pandas as pd
from influxdb import InfluxDBClient, DataFrameClient



class Link():

    def __init__(self, host, port, user, password, db_name, type_of_link):

        self.host = host

        self.port = port

        self.user = user

        self.password = password

        self.db_name = db_name

        self.type_of_link = type_of_link



        if (type_of_link == "influxdb") :

            self.client = InfluxDBClient(self.host, self.port, self.user, self.password, self.db_name)

        if (type_of_link == "mysql") :

            self.client = mysql.connector.connect(user=self.user, password=self.password, host=self.host,
                                                  database=self.db_name)

    #################################   QUERY  ###############################################

    def query(self, query):


        if (self.type_of_link == "influxdb"):

            self.influx_get_data_as_list(query)

            return self.influx_get_data_as_df()

        if (self.type_of_link == "mysql"):

            self.mysql_get_data(query)

            return self.influx_get_data_as_df()      # <<<<<<<<<<<< CHANGE   CHANGE





################ MYSQL queries

    def mysql_get_data(self):

        cursor = self.client.cursor()



################ Influx queries
    def influx_get_data_as_list(self, query_body):

        self.rs_tag = self.client.query(query_body)

        self.data = list(self.rs_tag.get_points())



    def influx_convert_to_df_second(self, data):
        main_d = dict()
        for i in range(len(data)):
            main_d[list(data[i].values())[1]] = list(data[i].values())[0]
        data1 = pd.Series(main_d)
        #print(data1)
        df = data1.to_frame()
        df = df.reset_index()
        df.columns = ['date', 'value']
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        return df


    def influx_convert_to_df_first(self, data):
        main_d = dict()
        for i in range(len(data)):
            main_d[list(data[i].values())[0]] = list(data[i].values())[1]
        data1 = pd.Series(main_d)
       # print(data1)
        df = data1.to_frame()
        df = df.reset_index()
        df.columns = ['date', 'value']
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        return df


    def influx_get_data_as_df(self):

        data_to_df = self.data

        if list(data_to_df[0].keys())[1] == "time":
            df_tag = self.influx_convert_to_df_second(data_to_df)
        else:
            df_tag = self.influx_convert_to_df_first(data_to_df)

        self.current_time = pd.to_datetime(df_tag.index.values[-1])

        return df_tag

    def add_ten_seconds(self, needed_time):
        needed_time_1 = pd.to_datetime(needed_time)
        needed_time_2 = needed_time_1 + datetime.timedelta(0, 10)
        return pd.tslib.Timestamp(needed_time_2)

    #################################   Write  data    ###############################################


    def write_data_to_influx(self, putting_data_in_list, measurement, ch_name):

        time_calc = []

        time_calc[0] = self.current_time

        for i in range(len(putting_data_in_list) - 1):
            time_calc[i + 1] = self.add_ten_seconds(time_calc[i])



        for i in range(len(putting_data_in_list)):

            json_influx = [
                {
                    "measurement": measurement,
                    "time": time_calc[i],
                    "fields": {
                        str(ch_name + "_low_limit"): putting_data_in_list[i] * 0.95,
                        str(ch_name + "_high_limit"): putting_data_in_list[i] * 1.05,
                        str(ch_name + "_predicted"): putting_data_in_list[i]
                    }
                }
            ]

            self.client.write_points(json_influx)






