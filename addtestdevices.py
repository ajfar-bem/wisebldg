N = 400
from queue import  Queue, Empty
import requests
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import threading
import time
import logging

logging.basicConfig(filename="testlog.log", level=logging.WARNING, filemode="w")

logging.debug("This is a debug message")
logging.info("Informational message 2")
logging.error("An error has happened! 2")
logging.warning("Watch out")
print "hola"
devname = 'thermo'

devQ = Queue()


def addDevice():

    while True:
        try:
            devicename,data = devQ.get(block=False)
        except Empty:
            #logging.exception("Error")
            return
        url = "https://kty062pfk6.execute-api.us-east-1.amazonaws.com/beta/DeviceData?device_id="+devicename
        code = 0
        while code != 200:
            response = requests.post(url,json=data)
            code = response.status_code
            if response.status_code != 200:
                logging.error("Unsuccessful Request", exc_info=True)
                print "Whoa!" + devicename
                print response.content
                print response.status_code
                print response.reason
                time.sleep(0.1)
        print(devicename)



for i in range(N):
    name = devname + str(i)
    data = {"thermostat_mode": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL,
         "thermostat_state": BEMOSS_ONTOLOGY.THERMOSTAT_STATE.POSSIBLE_VALUES.COOL,
         "fan_mode": BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.ON,
        "fan_state": BEMOSS_ONTOLOGY.FAN_STATE.POSSIBLE_VALUES.ON,
        "cool_setpoint": 76,
        "heat_setpoint": 70,
        "temperature": 79.15}
    devQ.put((name,data))

tic = time.time()
threads = list()
for i in range(50):
    t = threading.Thread(target=addDevice)
    t.start()
    threads.append(t)

for th in threads:
    th.join()

toc = time.time()
print ("Difference: %s" % (toc - tic))








