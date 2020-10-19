N = 400
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
            agent_id,address,macaddress = devQ.get(block=False)
        except Empty:
            return

        device_type_id = 1
        building_id = 1
        gateway_id = None
        account_id = "LabContract1"
        dbcon = actual_db_connection()
        try:
            dbcon.execute(
            "INSERT INTO device_info (agent_id,vendor_name,device_model,mac_address,nickname,address,config,identifiable,authorizable,communication,date_added,approval_status,device_type_id,node_id,building_id,gateway_id,account_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (agent_id, info['vendor_name'], info['device_model'], macaddress, agent_id, address, json.dumps({}),
             False, False, "WiFi", str(datetime.datetime.now()), 'APR', device_type_id, 0,
             building_id, gateway_id,account_id))
            dbcon.commit()
        except:
            continue

        print(agent_id)


for i in range(N):
    name = devname + str(i)
    address = "https://kty062pfk6.execute-api.us-east-1.amazonaws.com/beta/DeviceData?device_id="+name
    macaddress = "MAC"+name
    devQ.put((name,address,macaddress))

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








