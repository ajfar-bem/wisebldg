import test_settings
import requests
import time
import getToken
import addPassword
import cleanup
from discoverDevice import discoverDevice
from bemoss_lib.utils.catcherror import getErrorInfo
import logging
main_logger = logging.getLogger("testlogger")

def approveDevice(token, device):
    main_logger.info("Trying to approve device")
    approval_request_message = [
        [device['agent_id'], test_settings.BUILDING_NAME, device['nickname'], "APR"]]
    approval_url = test_settings.URL + "/dashboard/change_zones_api"

    token_dict = {"token":token}
    post_data = {'data':approval_request_message}
    result = requests.post(approval_url, params=token_dict, json=post_data)
    result.raise_for_status()
    main_logger.info("Device approval request successfully sent")
    devices_list_url = test_settings.URL + "/api/get_approved_devices_list"
    recheck_count = 3
    while recheck_count:
        result = requests.get(url=devices_list_url, params=token_dict)
        device_infos = result.json()
        for building, building_data in device_infos.items():
            if device['device_type'] not in building_data['devices']:
                break

            approved_devices = building_data['devices'][device['device_type']]
            if len(approved_devices) == 0:
                break
            for approved_device in approved_devices:
                if approved_device['device_model'] != device["device_model"]:
                    main_logger.error("Device was approved but a different model found in DB")
                    raise Exception("model mismatch of discovered devices")

            return approved_devices  # we only process the first building
        recheck_count -= 1
        time.sleep(5)
    main_logger.error("Device was approved but was not found in the table")
    raise Exception("Devices could not be approved")


if __name__ == "__main__":
    cleanup.cleanup()
    try:
        token = getToken.login(test_settings.testusername, test_settings.testuserpassword)
        discDevices = discoverDevice(token, test_settings.DEVICE_INFO['ICM100'])
        result = approveDevice(token, discDevices[0])
        print(result)
        print(len(result))
    except:
        print(getErrorInfo())
    cleanup.cleanup()
