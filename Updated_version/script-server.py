#!/user/bin/python3

from socket import *
import json, os
import time
from datetime import tzinfo, timedelta, datetime
import argparse

from baselib_com import Config, Link, Model

import _thread

def workflow(*kwargs):

    source_info = kwargs[0]
    model_info = kwargs[1]
    store_info = kwargs[2]
    delay = kwargs[3]
    id = kwargs[4]

    source_host = str(source_info['host'])
    source_port = source_info['port']
    source_node = source_info['node']
    source_user = source_info['user']
    source_password = source_info['password']
    source_query = '{0}'.format(source_info['query'])
    source_database = source_info['database']
    source_tag = source_info['tag']

    model_host = str(model_info['host'])
    model_port = model_info['port']
    model_node = model_info['node']
    model_core = model_info['ml-core']
    model_path = model_info['path']
    model_name = model_info['model']

    store_host = store_info['host']
    store_port = store_info['port']
    store_node = store_info['node']
    store_database = store_info['database']
    store_query = '{0}'.format(store_info['query'])
    store_user = store_info['user']
    store_password = store_info['password']
    inlink = Link(source_host, source_port, source_user, source_password, id)
    model = Model(model_host, model_port, model_node, model_core, id)
    outLink = Link(store_host, store_port, store_user, store_password, id)

    count =0

    while 1:
        time.sleep(delay)
        try:
            print('Query data from {0}.{1}'.format(source_node, source_database))
            source_data = inlink.getData(source_query, source_node, source_database)
            print('Output as source data', source_data)
            model_data = model.execModel(model_path, model_name, source_data, source_tag)
            print('Output as model_data', model_data)
            outLink.putData(model_data, store_node, store_database)
            print("complete flow!!!")
            count += 1
        except Exception as e:
            print("%s Error in flow: %s" % (id,str(e)))
        finally:
            print(count)
def main():
    print("start")
    print('read config file')
    source_list = Config().getInfo(file='./config.conf')
    try:
        print('start thread in: ', time.time())

        _thread.start_new_thread(workflow, (source_list['1']['source'], source_list['1']['model'], source_list['1']['destination'], source_list['1']['model']['delay'], source_list['1']['id_name']))
        #_thread.start_new_thread(workflow, (source_list['2']['source'], source_list['2']['model'], source_list['2']['destination'], source_list['2']['model']['delay'], source_list['2']['id_name']))

    except Exception as e:
        print("Error: unable to start thread" + str(e))
    while 1:
        time.sleep(80)
        print('pass')
        pass

if __name__ == '__main__':
    main()


















