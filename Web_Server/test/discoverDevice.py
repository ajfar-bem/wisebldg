import test_settings
import requests
import time
import getToken
import addPassword
import cleanup
from bemoss_lib.utils.catcherror import getErrorInfo
import logging
main_logger = logging.getLogger("testlogger")

def discoverDevice(token, device_info):
    main_logger.debug("Starting discoveryTest")
    if device_info['cloud_device']:
        password_data = dict()
        password_data['username'] = device_info['username']
        password_data['password'] = device_info['password']
        password_data['device_model'] = device_info['device_model']
        addPassword.addPassword(token, password_data)
        main_logger.info("Successfully added password data to the table and verified")

    device_type = device_info['device_type']
    token_dict = {"token": token}
    # Testing Discovery
    discovery_url = test_settings.URL + "/discovery/discover_new_devices_api"
    discovery_data = [device_info["device_model"]]
    result = requests.post(discovery_url, params=token_dict, json={'data':discovery_data})
    result.raise_for_status()
    main_logger.debug("Sent start discovery message")
    devices_list_url = test_settings.URL + "/api/get_pending_devices_list"
    time.sleep(2)
    recheck_count = 3
    while recheck_count:

        result = requests.get(url=devices_list_url, params=token_dict)
        device_infos = result.json()
        for building, building_data in device_infos.items():

            if device_type not in building_data['devices']:
                break

            pending_devices = building_data['devices'][device_type]
            if len(pending_devices) == 0:
                break
            for pnd_device in pending_devices:
                if pnd_device['device_model'] != device_info["device_model"]:
                    main_logger.error("model mismatch between discovered device and attempted to discover devices. Found model:"+str(pnd_device['device_model']))
                    raise Exception("model mismatch of discovered devices")

            return pending_devices  # we only process the first building
        recheck_count -= 1
        time.sleep(5)

    main_logger.error("No devices found to have been discovered")
    raise Exception("Devices could not be discovered")


if __name__ == "__main__":
    cleanup.cleanup()
    try:
        device_info = test_settings.DEVICE_INFO["RTH8580WF"]
        token = getToken.login(test_settings.testusername, test_settings.testuserpassword)
        discDevices = discoverDevice(token, device_info)
        print(discDevices)
        print(len(discDevices))
    except:
        print(getErrorInfo())
        pass
    cleanup.cleanup()
