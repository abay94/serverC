import json
def iniatialize():

    with open('model.conf') as f:
        json_file = json.load(f)

    object_ids = json_file.keys()
    print("all object names: ", object_ids)
    for obj_id in object_ids:

        ch_name = json_file[obj_id]["source_fields"]["raw_data"]

        SRC_ip_addr = json_file[obj_id]["source_fields"]["host"]
        SRC_port = json_file[obj_id]["source_fields"]["port"]
        SRC_username = json_file[obj_id]["source_fields"]["username"]
        SRC_userpass = json_file[obj_id]["source_fields"]["password"]

        SRC_node = json_file[obj_id]["source_fields"]["node"]
        SRC_measurement = json_file[obj_id]["source_fields"]["measurement"]
        SRC_database = json_file[obj_id]["source_fields"]["database"]

        OUT_ip_addr = json_file[obj_id]["destination_fields"]["host"]
        OUT_port = json_file[obj_id]["destination_fields"]["port"]
        OUT_username = json_file[obj_id]["destination_fields"]["username"]
        OUT_userpass = json_file[obj_id]["destination_fields"]["password"]

        OUT_node = json_file[obj_id]["destination_fields"]["node"]
        OUT_database = json_file[obj_id]["destination_fields"]["database"]
        OUT_measurement = json_file[obj_id]["destination_fields"]["measurement"]


        ML_core_type = json_file[obj_id]["model_fields"]["ml-core"]
        model_name = json_file[obj_id]["model_fields"]["name"]
        model_dir = json_file[obj_id]["model_fields"]["path"]
        ML_core_ip_addr = json_file[obj_id]["model_fields"]["host"]
        ML_core_port = json_file[obj_id]["model_fields"]["port"]


        print(ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, OUT_ip_addr, OUT_port, OUT_username, OUT_userpass, SRC_node, SRC_database, SRC_measurement, model_name, model_dir, OUT_node, OUT_database, OUT_measurement, ML_core_ip_addr, ML_core_port,ML_core_type)


        # all_copies_of_object.append(Channel_object(ch_name, SRC_ip_addr, SRC_port, SRC_username, SRC_userpass, OUT_ip_addr, OUT_port, OUT_username, OUT_userpass, SRC_node, SRC_database, SRC_measurement, model_name, model_dir, OUT_node, OUT_database, OUT_measurement, ML_core_ip_addr, ML_core_port,ML_core_type))


if __name__ == "__main__":

    iniatialize()