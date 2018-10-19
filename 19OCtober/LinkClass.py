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



    #################################   Write  data    ###############################################


    def write_data_to_influx(self, json_influx):



        self.client.write_points(json_influx)






