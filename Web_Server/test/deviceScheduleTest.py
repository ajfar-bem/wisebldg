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



def compareSchedule(deviceSchedule,submittedSchedule):
    #periods = ['Wake', 'Leave', 'Return', 'Sleep']
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for day, dailySchedule in deviceSchedule.items():
        if day not in days:
            continue
        for id, entry in enumerate(dailySchedule):
            compareVars = ['cool_setpoint','heat_setpoint','at']
            for var, val in entry.items():
                if var.lower() in compareVars:
                    if float(val) != float(submittedSchedule[day][id][var]):
                        return False
    return True

def deviceScheduleTest(token, device_model, agent_id, scheduleList):
    main_logger.info("Starting scheduleTest")
    device_info = test_settings.DEVICE_INFO[device_model]
    device_type = device_info['device_type']
    token_dict = {"token": token}
    built_in_schedule = device_info['built_in_schedule']
    device_api = importlib.import_module("DeviceAPI." + device_info['api'])
    device_ontology = device_api.API().ontology()
    #check if you can read all the device data from the metadata
    device_list_url = test_settings.URL + "/api/get_better_list"
    device_schedule_update_url = test_settings.URL +"/api/schedule_update"
    device_schedule_retrieve_url = test_settings.URL + "/api/get_schedule"
    query_dict = dict(token_dict)
    query_dict.update({"agent_id": agent_id})

    for scheduleData in scheduleList:
        d = {"agent_id":agent_id,'user':"testingScript"}
        scheduleData.update(d)
        main_logger.debug("Sending schedule update command:" + str(scheduleData))
        response = requests.post(device_schedule_update_url,params=query_dict,json={'data':scheduleData})
        response.raise_for_status()
        main_logger.info("Schedule data successfully submitted")
        time.sleep(0) #No need to wait; if response was got, scheduled saved to table. Check immediately
        recheck_count = 3
        while recheck_count:
            unchanged_vars = []
            result = requests.get(url=device_schedule_retrieve_url, params=query_dict)
            try:
                result.raise_for_status()
            except:
                main_logger.error("get_schedule endpoint failed")
                raise

            saved_schedule_data = result.json()
            main_logger.debug("Got device data:" + str(saved_schedule_data))
            if not compareSchedule(saved_schedule_data,scheduleData):
                recheck_count -= 1
                time.sleep(5) #There is a mismatch, lets wait 5 more seconds and see if it will match next time
                main_logger.debug("Some variables did not change; waiting 5 sec: " + str(unchanged_vars))
                continue
            else:
                break
        if not recheck_count:
            main_logger.error("Device schedule was submitted approved, but the change did not reflect on the scheduleData table")
            raise Exception("Device schedule was submitted approved, but the change did not reflect on the scheduleData table")

        main_logger.info("Schedule Data table was successfully updated")
        if built_in_schedule:
            main_logger.debug("Testing if built-in schedule was updated")
            time.sleep(5)
            recheck_count = 3
            while recheck_count:
                unchanged_vars = list()
                result = requests.get(url=device_list_url, params=query_dict)
                try:
                    result.raise_for_status()
                except Exception as exp:
                    main_logger.error(device_list_url+" end point failed")
                    raise

                device_data = result.json()
                main_logger.debug("Got device data:" + str(device_data))
                if not device_data or 'Building1' not in device_data or device_type not in device_data['Building1'][
                    'devices'] or \
                        not device_data['Building1']['devices'][device_type]:
                    main_logger.debug("Device  not found in get_better_list")
                    time.sleep(10)
                    recheck_count -= 1
                    continue
                else:
                    device_data = device_data['Building1']['devices'][device_type][0]

                device_schedule_data = device_data['scheduleData']
                main_logger.debug("scheduleData in device: "+str(device_schedule_data))
                everyday = dict()
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

                class Continue(Exception):
                    pass

                try:
                    for day in days:
                        id = 0
                        for entry in scheduleData[day]:
                            device_entry = device_schedule_data[day][id]
                            if float(entry['at']) != float(device_entry[1]) or float(entry['heat_setpoint']) != float(device_entry[3]) or float(entry['cool_setpoint']) != float(device_entry[2]):
                                main_logger.info("Mismtach found. Submitted entry for day "+day+" was "+str(entry)+" Found entry: "+str(device_entry))
                                main_logger.info("Waiting a bit more")
                                raise Continue()
                            id +=1
                except Continue:
                    time.sleep(5)
                    recheck_count -= 1
                    continue
                else:
                    break

            if not recheck_count:
                main_logger.error("Device schedule was saved but the built-in schedule in device could not be updated")
                raise Exception("Device schedule was saved but the built-in schedule in device could not be updated")

            main_logger.info("Built-in schedule was successfully updated")

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
    scheduleList = test_settings.thermostat_schedule_data
    print(deviceScheduleTest(token, device_model, agent_id, scheduleList))
    # cleanup()