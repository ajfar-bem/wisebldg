import test_settings
import requests
import time
import getToken
from discoverDevice import discoverDevice
from cleanup import cleanup
from approveDevice import approveDevice
import importlib
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from deviceMonitorTest import deviceMonitorTest
from deviceControlTest import deviceControlTest
from deviceScheduleTest import deviceScheduleTest

import logging
main_logger = logging.getLogger("testlogger")

def deviceTest(token, device_model):
    device_info = test_settings.DEVICE_INFO[device_model]
    devices = discoverDevice(token,device_info)
    main_logger.info("Successfully discovered the device")
    one_device = devices[0]
    agent_id = one_device['agent_id']
    approveDevice(token,one_device)
    main_logger.info("Successfully approved the device")
    deviceMonitorTest(token,device_model,one_device)
    main_logger.info("Successfully monitored the device")
    controlCommandList = test_settings.test_control_commands[device_model]
    deviceControlTest(token,device_model,agent_id,controlCommandList)
    main_logger.info("Successfully controlled the device")
    scheduleList = test_settings.test_schedule_lists[device_model]
    deviceScheduleTest(token,device_model,agent_id,scheduleList)
    main_logger.info("Successfully saved schedule to/for the device")

if __name__ == "__main__":
    cleanup()
    token = getToken.login(test_settings.testusername, test_settings.testuserpassword)
    print(deviceTest(token, "ICM100"))
    #cleanup()