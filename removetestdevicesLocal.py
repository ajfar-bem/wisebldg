N = 3200
from queue import  Queue, Empty
import requests
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from bemoss_lib.utils.db_helper import db_connection,actual_db_connection
import threading
import time
import json
import datetime
devname = 'thermo'

from DeviceAPI.API_VirtualThermostat import API

devAPI = API()
info = devAPI.API_info()[0]

devQ = Queue()



def addDevice():

    while True:
        try:
            agent_id = devQ.get(block=False)
        except Empty:
            return
        dbcon = actual_db_connection()
        dbcon.execute(
            "DELETE FROM devicedata where agent_id=%s",
            (agent_id,))
        dbcon.commit()

        dbcon.execute(
        "DELETE FROM device_info where agent_id=%s",
        (agent_id,))
        dbcon.commit()


        print(agent_id)


for i in range(N):
    name = devname + str(i)
    devQ.put(name)

tic = time.time()
threads = list()
for i in range(30):
    t = threading.Thread(target=addDevice)
    t.start()
    threads.append(t)

for th in threads:
    th.join()


toc = time.time()
print ("Difference: %s" % (toc - tic))








