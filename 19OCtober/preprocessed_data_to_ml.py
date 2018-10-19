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
from serverClass import Channel_object


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

            attr_of_node_src = read_node_config_file(json_file[obj_name][ch_name]["input"]["node"])
            attr_of_node_out = read_node_config_file(json_file[obj_name][ch_name]["output"]["node"])



            SRC_ip_addr = attr_of_node_src["host"]
            SRC_port = attr_of_node_src["port"]
            SRC_username = attr_of_node_src["username"]
            SRC_userpass = attr_of_node_src["userpass"]

            OUT_ip_addr = attr_of_node_out["host"]
            OUT_port = attr_of_node_out["port"]
            OUT_username = attr_of_node_out["username"]
            OUT_userpass = attr_of_node_out["userpass"]


            SRC_node = json_file[obj_name][ch_name]["input"]["node"]
            SRC_measurement = json_file[obj_name][ch_name]["input"]["measurement"]
            SRC_database = json_file[obj_name][ch_name]["input"]['database']

            model_name = json_file[obj_name][ch_name]["input"]['model_name']
            model_dir = json_file[obj_name][ch_name]["input"]["model_dir"]
            rate = json_file[obj_name][ch_name]["input"]["rate"][:-1]


            OUT_node = json_file[obj_name][ch_name]["output"]["node"]
            OUT_database = json_file[obj_name][ch_name]["output"]["database"]
            OUT_measurement = json_file[obj_name][ch_name]["output"]["measurement"]
            ML_core_type = json_file[obj_name][ch_name]["input"]["ml-core"]

            attr_of_ml_core = read_node_config_file(json_file[obj_name][ch_name]["input"]["ml-core"])

            ML_core_ip_addr = attr_of_ml_core["host"]
            ML_core_port = attr_of_ml_core["port"]




            all_copies_of_object.append(Channel_object(ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, OUT_ip_addr, OUT_port, OUT_username, OUT_userpass, SRC_node, SRC_database, SRC_measurement, model_name, model_dir, rate, OUT_node, OUT_database, OUT_measurement, ML_core_ip_addr, ML_core_port,ML_core_type))


if __name__ == "__main__":

    iniatialize()

    while True:

        for object in all_copies_of_object:

            object.get_raw_data_from_source()

            object.send_raw_data_to_ml()

            object.put_preprocessed_data_to_db()




        time.sleep(5)


















