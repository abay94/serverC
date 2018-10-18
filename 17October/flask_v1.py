
# import os
# import pandas as pd    #'0.22.0'
# from sklearn.externals import joblib             #The scikit-learn version is 0.19.1.
from flask import Flask, jsonify, request, Response
# from flask import render_template
import requests
import json
# from datetime import datetime, timedelta
# import numpy as np
from LinkClass import *
from serverClass import Channel_object
import pandas as pd
import statsmodels.api as sm
import statsmodels

app = Flask(__name__)



@app.route('/ARIMA', methods = ['POST'])

def apicall_two(responses2 = None):

    try:

        test_json = request.get_json()

        # print(type(test_json))
        #
        # print(json.loads(test_json))

        # token_data = json.loads(test_json)
        # print("all data as df :", token_data["data"])
        #
        # print("type of data  :", type(token_data["data"]))
        #
        # print ("model dir: ", token_data["model_dir"])

        gotten_data_as_df_with_model_dir = pd.read_json(test_json, orient='columns')

        model_dir = str(gotten_data_as_df_with_model_dir.model_dir.unique()[0])

        gotten_data_df = gotten_data_as_df_with_model_dir.drop(['model_dir'], axis=1)

        #gotten_data_df = gotten_data_series.to_frame()




        print("all data as df :", type(gotten_data_df))
        print("all data as df :", gotten_data_df)

        print(gotten_data_df.index)







    except Exception as e:

        raise e

    #pd.read_pickle(model_dir)

    results_of_model = statsmodels.tsa.statespace.sarimax.SARIMAXResults.load(model_dir)

    my_mod_tag = sm.tsa.SARIMAX(gotten_data_df.astype(float), order=(1, 1, 1),
                                enforce_stationarity=False,
                                enforce_invertibility=False)

    res_tag = my_mod_tag.filter(results_of_model.params)

    insample_tag = res_tag.predict(start=len(gotten_data_df.index), end=len(gotten_data_df.index) + 6)
    print(type(insample_tag.values.tolist()))

    return str(insample_tag.values.tolist())




if __name__ == '__main__':
    #iniatialize()
    app.run(host="0.0.0.0")







