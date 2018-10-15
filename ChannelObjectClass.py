import pandas as pd
from influxdb import InfluxDBClient, DataFrameClient
import json
import time
import datetime
import statsmodels.api as sm
import statsmodels
from InfluxLinkClass import *


time_calc = []


class Channel_object():
    def __init__(self, ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_db_name, SRC_measurement,
                 model_name, model_dir, rate, OUT_node, OUT_database, OUT_measurement):

        self.SRC_ip_addr = SRC_ip_addr
        self.SRC_port = SRC_port
        self.SRC_username = SRC_username
        self.SRC_userpass = SRC_userpass
        self.SRC_measurement = SRC_measurement

        self.ch_name = ch_name
        self.model_name = model_name
        self.model_dir = model_dir
        self.rate = rate

        self.OUT_node = OUT_node
        self.OUT_database = OUT_database
        self.OUT_measurement = OUT_measurement

        if (model_name == "ARIMA"):
            self.Influx_query = "SELECT " + ch_name + " from " + SRC_measurement + " WHERE time > now() - 30m;"

        else:
            self.Influx_query = "SELECT {0} from {1} GROUP BY * ORDER BY DESC LIMIT 1;".format(ch_name, SRC_measurement)

        self.Influx_query = "SELECT " + ch_name + " from " + SRC_measurement + " WHERE time > now() - 30m;"
        self.Influx_json_to_write = ""

        self.InfluxAgent = Influx_our(SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, SRC_db_name, self.Influx_query,
                                      self.Influx_json_to_write)

    def get_data_from_influx_as_df(self):

        self.data_as_df = self.InfluxAgent.get_data_as_df()

    def get_data_from_influx_as_list(self):

        self.data_as_list = self.InfluxAgent.get_data_as_list()

    def add_ten_seconds(self, needed_time):
        needed_time_1 =  pd.to_datetime(needed_time)
        needed_time_2 = needed_time_1 + datetime.timedelta(0,10)
        return pd.tslib.Timestamp(needed_time_2)


    def predict_arima(self):

        df_tag = self.get_data_from_influx_as_df()
        sarimax_model = statsmodels.tsa.statespace.sarimax.SARIMAXResults.load(self.model_dir)
        current_time = pd.to_datetime(df_tag.index.values[-1])
        my_mod_tag = sm.tsa.SARIMAX(df_tag.astype(float), order=(1, 1, 1),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)

        res_tag = my_mod_tag.filter(sarimax_model.params)

        insample_tag = res_tag.predict(start=len(df_tag.index), end=len(df_tag.index) + 6)

        time_calc[0] = current_time

        for i in range(5):
            time_calc[i + 1] = self.add_ten_seconds(time_calc[i])




        for i in range(6):
            json_influx = [
                {
                    "measurement": self.OUT_measurement,
                    "time": time_calc[i],
                    "fields": {
                        str(self.ch_name + "_low_limit"): insample_tag.values[i] * 0.95,
                        str(self.ch_name + "_high_limit"): insample_tag.values[i] * 1.05,
                        str(self.ch_name + "_predicted"): insample_tag.values[i]
                    }
                }
            ]

            self.Influx_json_to_write = json_influx

            self.InfluxAgent.write_data_to_influx()



