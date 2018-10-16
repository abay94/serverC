#!/home/user/anaconda3/bin/python
import warnings
import itertools
import pandas as pd
# import numpy as np
# import statsmodels.api as sm
# import statsmodels
from influxdb import InfluxDBClient, DataFrameClient
import json
import requests
import time
from ServerClass import Channel_object


all_copies_of_object = []


def read_node_config_file(node_name):

    with open('node.cnfg.json') as f:
        json_file = json.load(f)

    return json_file[node_name]


def iniatialize():

    with open('ch-ad.cnfg.json') as f:
        json_file = json.load(f)

    object_names = json_file.keys()
    print("all object names: ", object_names)
    for obj_name in object_names:
        channel_names = json_file[obj_name].keys()
        for ch_name in channel_names:

            attr_of_node = read_node_config_file("influxdb")

            SRC_ip_addr = attr_of_node["host"]
            SRC_port = attr_of_node["port"]
            SRC_username = attr_of_node["username"]
            SRC_userpass = attr_of_node["userpass"]

            SRC_source_type = json_file[obj_name][ch_name]["input"]["source"]
            SRC_measurement = json_file[obj_name][ch_name]["input"]["measurement"]
            SRC_db_name = json_file[obj_name][ch_name]["input"]['database']

            model_name = json_file[obj_name][ch_name]["input"]['model_name']
            model_dir = json_file[obj_name][ch_name]["input"]["model_dir"]
            rate = json_file[obj_name][ch_name]["input"]["rate"]

            OUT_node = json_file[obj_name][ch_name]["output"]["node"]
            OUT_database = json_file[obj_name][ch_name]["output"]["database"]
            OUT_measurement = json_file[obj_name][ch_name]["output"]["measurement"]



            all_copies_of_object.append(Channel_object(ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_source_type, SRC_db_name, SRC_measurement, model_name, model_dir, rate, OUT_node, OUT_database, OUT_measurement))


if __name__ == "__main__":

    iniatialize()

    while True:

        for object in all_copies_of_object:

            object.get_raw_data_from_source()

            object.send_raw_data_to_ml()

            object.put_preprocessed_data_to_db()


        time.sleep(20)








# from InfluxLinkClass import *
#
#
#
# class Channel_object():
#
#     def __init__(self, ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_db_name, SRC_measurement, model_name, model_dir, rate, OUT_node, OUT_database, OUT_measurement):
#
#         self.SRC_ip_addr = SRC_ip_addr
#         self.SRC_port = SRC_port
#         self.SRC_username = SRC_username
#         self.SRC_userpass = SRC_userpass
#         self.SRC_measurement = SRC_measurement
#
#         self.ch_name = ch_name
#         self.model_name = model_name
#         self.model_dir = model_dir
#         self.rate = rate
#
#         self.OUT_node = OUT_node
#         self.OUT_database = OUT_database
#         self.OUT_measurement = OUT_measurement
#
#         if (model_name == "ARIMA") :
#             self.Influx_query = "SELECT " + ch_name + " from " + SRC_measurement + " WHERE time > now() - 30m;"
#
#         else:
#             self.Influx_query = "SELECT {0} from {1} GROUP BY * ORDER BY DESC LIMIT 1;".format(ch_name, SRC_measurement)
#
#
#         self.Influx_query = "SELECT " + ch_name + " from " + SRC_measurement + " WHERE time > now() - 30m;"
#         self.Influx_json_to_write = ""
#
#         self.InfluxAgent = Influx_our(SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_db_name, self.Influx_query, self.Influx_json_to_write)
#
#     def get_data_from_influx_as_df(self):
#
#         self.data_as_df = self.InfluxAgent.get_data_as_df()
#
#     def get_data_from_influx_as_list(self):
#
#         self.data_as_list = self.InfluxAgent.get_data_as_list()
#
#
#
#
#
#
#
#
# ################
# list_of_tags_as_object = []
# ################
#
# def read_channel_config_file():
#
#     with open('ch-ad.cnfg.json') as f:
#         json_file = json.load(f)
#
#     object_names = json_file.keys()
#     print("all object names: ", object_names)
#     for obj_name in object_names:
#         channel_names = json_file[obj_name].keys()
#         for ch_name in channel_names:
#             if (json_file[obj_name][ch_name]["input"]["source"] == "influxdb"):
#
#                 attr_of_node = read_node_config_file("influxdb")
#
#                 SRC_ip_addr = attr_of_node["host"]
#                 SRC_port = attr_of_node["port"]
#                 SRC_username = attr_of_node["username"]
#                 SRC_userpass = attr_of_node["userpass"]
#
#                 SRC_measurement = json_file[obj_name][ch_name]["input"]["measurement"]
#                 SRC_db_name = json_file[obj_name][ch_name]["input"]['database']
#
#                 model_name = json_file[obj_name][ch_name]["input"]['model_name']
#                 model_dir = json_file[obj_name][ch_name]["input"]["model_dir"]
#                 rate = json_file[obj_name][ch_name]["input"]["rate"]
#
#                 OUT_node = json_file[obj_name][ch_name]["output"]["node"]
#                 OUT_database = json_file[obj_name][ch_name]["output"]["database"]
#                 OUT_measurement = json_file[obj_name][ch_name]["output"]["measurement"]
#
#
#                 list_of_tags_as_object.append(Channel_object(ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_db_name, SRC_measurement, model_name, model_dir, rate, OUT_node, OUT_database, OUT_measurement))
#
#
#
#
# def read_node_config_file(node_name):
#
#     with open('node.cnfg.json') as f:
#         json_file = json.load(f)
#
#     return json_file[node_name]
#
# ################














