
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


def deviceControlTest(token, device_model,agent_id, controlCommandList):
    main_logger.info("Starting control test")
    device_info = test_settings.DEVICE_INFO[device_model]
    device_type = device_info['device_type']
    token_dict = {"token": token}

    device_api = importlib.import_module("DeviceAPI." + device_info['api'])
    device_ontology = device_api.API().ontology()
    #check if you can read all the device data from the metadata
    device_list_url = test_settings.URL + "/api/get_better_list"
    device_control_url = test_settings.URL +"/device/api_update_device"
    query_dict = dict(token_dict)
    query_dict.update({"agent_id": agent_id})

    for controlCommand in controlCommandList:
        d = {"agent_id":agent_id,'user':"testingScript"}
        controlCommand.update(d)

        main_logger.debug("Sending control command:" + str(controlCommand))
        response = requests.post(device_control_url,params=query_dict,json={'data':controlCommand})
        response.raise_for_status()
        time.sleep(5) #wait for the control command to be processed
        main_logger.info("Control command sent successfully")
        recheck_count = 3

        while recheck_count:
            result = requests.get(url=device_list_url, params=token_dict)
            unchanged_vars = []
            try:
                result.raise_for_status()
            except:
                main_logger.error("Get better list api call failed. Webserver issue")
                raise

            device_data = result.json()
            main_logger.debug("Got device data:" + str(device_data))
            if not device_data or 'Building1' not in device_data or device_type not in device_data['Building1']['devices'] or \
                not device_data['Building1']['devices'][device_type]:
                time.sleep(5)
                recheck_count -=1
            else:
                device_data = device_data['Building1']['devices'][device_type][0]
                for val in device_ontology.values():
                    if val.NAME not in device_data:
                        main_logger.error("One of the ontology variable doesn't exist in device data: "+val.NAME)
                        raise Exception("One of the ontology variable doesn't exist in device data: "+val.NAME)
                    if val.NAME in controlCommand and device_data[val.NAME] != controlCommand[val.NAME]:
                        unchanged_vars.append(val.NAME)
                        recheck_count -= 1
                        time.sleep(5) #There is a mismatch, lets wait 5 more seconds and see if it will match next time
                        main_logger.debug("Some variables did not change; waiting 5 sec: " + str(unchanged_vars))
                        break
                else:
                    break
        if not recheck_count:
            main_logger.error("Device Was approved, but the control was not successfull. The following vars didn't change:" + str(unchanged_vars))
            raise Exception("Device Was approved, but the control was not successfull. The following vars didn't change:" + str(unchanged_vars))

        main_logger.info("Control successfully verified in postgresdb.")
        time.sleep(2)
        #check if you can read the historical data
        device_history_url = test_settings.URL + "/charts/get_historical_data"
        recheck_count = 3
        while recheck_count:
            unchanged_vars = list()
            result = requests.get(url=device_history_url, params=query_dict)
            try:
                result.raise_for_status()
            except Exception as exp:
                main_logger.error("get_historical_data end point failed. Webserver issue")
                raise


            device_data = result.json()
            main_logger.debug("Historical data:"+str(device_data))
            device_ontology = device_api.API().ontology()
            for val in device_ontology.values():
                if val.NAME in controlCommand and device_data[val.NAME][-1][1] != controlCommand[val.NAME]:
                    unchanged_vars.append(val.NAME)
                    recheck_count -= 1
                    time.sleep(5)  # There is a mismatch, lets wait 5 more seconds and see if it will match next time
                    main_logger.debug("Some variables did not change; waiting 5 sec: " + str(unchanged_vars))
                    break
            break

        if not recheck_count:
            main_logger.error("Device Was approved, but it could not get data from device in cassandra")
            raise Exception("Device Was approved, but it could not get data from device in cassandra")

        main_logger.info("Control successfully verified in cassandradb.")


if __name__ == "__main__":
    device_model = "RTH8580WF"
    # agent_id = "ICM1_BGQKEKRXBGFV_contract1"
    agent_id = u'RTH8_3994424_contract1'
    #cleanup()
    token = getToken.login(test_settings.testusername, test_settings.testuserpassword)
    # device_info = test_settings.DEVICE_INFO[device_model]
    # devices = discoverDevice(token, device_info)
    # one_device = devices[0]
    # approveDevice(token, one_device)
    # agent_id = one_device['agent_id']
    controlCommandList = test_settings.test_control_commands['RTH8580WF']

    print(deviceControlTest(token, device_model, agent_id, controlCommandList))
    # cleanup()