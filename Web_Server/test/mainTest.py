import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import logging
from logging import handlers
main_logger = logging.getLogger("testlogger")
main_logger.level = logging.DEBUG

fileHandler = handlers.RotatingFileHandler(filename="BEMOSSTEST.log",maxBytes=50000000,backupCount=10) #50 MB limit
consoleHandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")
fileHandler.setFormatter(formatter)
fileHandler.level = logging.DEBUG
consoleHandler.level = logging.INFO
main_logger.handlers = [fileHandler,consoleHandler]
main_logger.propagate = False
from bemoss_lib.utils.catcherror import getErrorInfo

from  deviceTest import deviceTest
import test_settings
import getToken
from cleanup import cleanup





main_logger.info("Cleaning up old stuffs")
cleanup()
main_logger.info("Begin Testing")
#device_models_to_test = ['RTH8580WF','Dimmer']
device_models_to_test = test_settings.models_to_test

token = getToken.login(test_settings.testusername, test_settings.testuserpassword)
failed_models = []
for device_model in device_models_to_test:
    try:
        main_logger.info("Testing device model: "+device_model)
        deviceTest(token,device_model)
    except Exception as exp:
        failed_models.append(device_model)
        main_logger.info("Testing failed for device model: " + str(device_model) + "Error: "+ str(exp))
    else:
        main_logger.info("**************************\nDevice model: " + device_model + " passed all the tests\n****************************\n")

main_logger.info("Test Concluded")
if not failed_models:
    main_logger.info("********************\n All models passed the tests \n *********************\n")
    main_logger.info('\n'.join(device_models_to_test))
else:
    main_logger.info("********\n The following models failed the tests; check the log files for details")
    main_logger.info('\n'.join(failed_models))
    main_logger.info("********\n The following models passed the tests")
    for model in failed_models:
        device_models_to_test.remove(model)
    main_logger.info('\n'.join(device_models_to_test))