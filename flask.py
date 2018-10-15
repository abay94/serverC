#!/home/user/anaconda3/bin/python
# import os
# import pandas as pd    #'0.22.0'
# from sklearn.externals import joblib             #The scikit-learn version is 0.19.1.
from flask import Flask, jsonify, request         #'0.12.2'
# from flask import render_template
# import requests
import json
# from datetime import datetime, timedelta
# import numpy as np

#our libraries
from InfluxLinkClass import *
from ChannelObjectClass import *
from Final_try_python_scripts.ChannelObjectClass import Channel_object

app = Flask(__name__)


arima_objects = []


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
            if (json_file[obj_name][ch_name]["input"]["source"] == "influxdb"):

                attr_of_node = read_node_config_file("influxdb")

                SRC_ip_addr = attr_of_node["host"]
                SRC_port = attr_of_node["port"]
                SRC_username = attr_of_node["username"]
                SRC_userpass = attr_of_node["userpass"]

                SRC_measurement = json_file[obj_name][ch_name]["input"]["measurement"]
                SRC_db_name = json_file[obj_name][ch_name]["input"]['database']

                model_name = json_file[obj_name][ch_name]["input"]['model_name']
                model_dir = json_file[obj_name][ch_name]["input"]["model_dir"]
                rate = json_file[obj_name][ch_name]["input"]["rate"]

                OUT_node = json_file[obj_name][ch_name]["output"]["node"]
                OUT_database = json_file[obj_name][ch_name]["output"]["database"]
                OUT_measurement = json_file[obj_name][ch_name]["output"]["measurement"]

                if (model_name == 'ARIMA'):

                    arima_objects.append(Channel_object(ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_db_name, SRC_measurement, model_name, model_dir, rate, OUT_node, OUT_database, OUT_measurement))



@app.route('/ARIMA', methods=['POST', 'GET'])

def apicall_two(responses2 = None):

    try:

       for i in range(len(arima_objects)):

           arima_objects[i].predict_arima()

    except Exception as e:

        raise e




if __name__ == '__main__':
    iniatialize()
    app.run(host="0.0.0.0")







