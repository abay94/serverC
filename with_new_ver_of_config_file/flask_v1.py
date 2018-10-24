# from sklearn.externals import joblib             #The scikit-learn version is 0.19.1.
from flask import Flask, jsonify, request, Response
# from flask import render_template
#import requests
import json
# from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt
from sklearn.metrics import mean_squared_error as mse
import pickle

app = Flask(__name__)



@app.route('/ARIMA', methods = ['POST'])

def apicall_two(responses2 = None):

    try:

        test_json = request.get_json()


        gotten_data_as_df_with_model_dir = pd.read_json(test_json, orient='columns')

        model_dir = str(gotten_data_as_df_with_model_dir.model_dir.unique()[0])

        gotten_data_df = gotten_data_as_df_with_model_dir.drop(['model_dir'], axis=1)

        print(model_dir[0])
        print(model_dir[-1])


        print("all data as df :", type(gotten_data_df))
        print("all data as df :", gotten_data_df)

        print(gotten_data_df.index)

    except Exception as e:

        raise e


    results_of_model = statsmodels.tsa.statespace.sarimax.SARIMAXResults.load(model_dir)

    my_mod_tag = sm.tsa.SARIMAX(gotten_data_df.astype(float), order=(1, 1, 1),
                                enforce_stationarity=False,
                                enforce_invertibility=False)

    res_tag = my_mod_tag.filter(results_of_model.params)

    insample_tag = res_tag.predict(start=len(gotten_data_df.index), end=len(gotten_data_df.index))


    live = np.round(gotten_data_df[-1:].values, 5)

    my_list = map(lambda x: x[0], live)

    live_series = list(pd.Series(my_list))

    mse = live_series[0] - insample_tag.values[0]

    mse = pow(mse, 2)

    returning_data = list()

    returning_data.append(insample_tag.values.tolist()[0])
    returning_data.append(mse)
    returning_data.append(float(live))

    print(returning_data)

    return str(returning_data)


@app.route('/HOLTWINTER', methods = ['POST'])

def apicall_t(responses2 = None):

    try:

        test_json = request.get_json()

        gotten_data_as_df_with_model_dir = pd.read_json(test_json, orient='columns')

        model_dir = str(gotten_data_as_df_with_model_dir.model_dir.unique()[0])

        gotten_data_df = gotten_data_as_df_with_model_dir.drop(['model_dir'], axis=1)



    except Exception as e:

        raise e

    print(model_dir)

    with open('%s' % model_dir, 'rb') as handle:
        model1 = pickle.load(handle)
        live_data = np.round(gotten_data_df[-1:].values, 5)
        pred = model1.predict(start=len(gotten_data_df.index), end=len(gotten_data_df.index))  # param_data.index[-1])
        mse_goi = mse(pred, gotten_data_df.iloc[-1:])

        returning_data = list()

        returning_data.append(pred.tolist()[0])
        returning_data.append(mse_goi)
        returning_data.append(float(live_data))


    return str(returning_data)




if __name__ == '__main__':
    #iniatialize()
    app.run(host="0.0.0.0")







