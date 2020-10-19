import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import test_settings
import requests
import time
import getToken
from discoverDevice import discoverDevice
from cleanup import cleanup
from approveDevice import approveDevice
import importlib
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import logging
main_logger = logging.getLogger("testlogger")

def deviceMonitorTest(token, device_model,one_device):
    main_logger.info("Starting monitorTest")
    device_info = test_settings.DEVICE_INFO[device_model]
    agent_id = one_device['agent_id']
    device_type = device_info['device_type']
    token_dict = {"token": token}
    device_api = importlib.import_module("DeviceAPI." + device_info['api'])
    #check if you can read all the device data from the metadata
    device_list_url = test_settings.URL + "/api/get_better_list"
    time.sleep(10) #wait for the device to populate the data
    recheck_count = 3
    while recheck_count:
        result = requests.get(url=device_list_url, params=token_dict)
        try:
            result.raise_for_status()
        except:
            main_logger.error("API Call to the get_better_list endpoint failed. Shouldn't have failed. It is a webserver code issue")
            raise

        device_data = result.json()
        main_logger.debug("Got device list data")
        main_logger.debug(str(device_data))
        if not device_data or 'Building1' not in device_data or device_type not in device_data['Building1']['devices'] or \
            not device_data['Building1']['devices'][device_type]:
            time.sleep(5)
            recheck_count -=1
        else:
            device_data = device_data['Building1']['devices'][device_type][0]
            device_ontology = device_api.API().ontology()
            for val in device_ontology.values():
                if val.NAME not in device_data:
                    main_logger.error("One of the ontology variable doesn't exist in device data: "+val.NAME)
                    raise Exception("One of the ontology variable doesn't exist in device data: "+val.NAME)
            break
    if not recheck_count:
        main_logger.error("Device Was approved, but it could not save data from device in postgresdb")
        raise Exception("Device Was approved, but it could not save data from device in postgresdb")

    main_logger.info("Successfully read the device data")
    #check if you can read the historical data
    device_history_url = test_settings.URL + "/charts/get_historical_data"
    recheck_count = 2
    while recheck_count:
        query_dict = dict(token_dict)
        query_dict.update({"agent_id":agent_id})
        result = requests.get(url=device_history_url, params=query_dict)
        try:
            result.raise_for_status()
        except Exception as exp:
            main_logger.error("API Call to the get_historical_data endpoint failed. Shouldn't have failed. It is a webserver code issue")
            raise


        device_data = result.json()
        main_logger.debug("Historical data:" + str(device_data))
        device_ontology = device_api.API().ontology()
        for val in device_ontology.values():
            if val.NAME not in device_data:
                main_logger.error("One of the ontology variable doesn't exist in time series database: " + val.NAME)
                raise Exception("One of the ontology variable doesn't exist in time series database: " + val.NAME)
        break

    if not recheck_count:
        main_logger.error("Device Was approved, but it could not get data from device in postgresdb")
        raise Exception("Device Was approved, but it could not get data from device in postgresdb")


if __name__ == "__main__":
    cleanup()
    token = getToken.login(test_settings.testusername, test_settings.testuserpassword)
    device_model = "ICM100"
    device_info = test_settings.DEVICE_INFO[device_model]
    devices = discoverDevice(token, device_info)
    one_device = devices[0]
    approveDevice(token, one_device)
    print(deviceMonitorTest(token, device_model, one_device))
    #cleanup()