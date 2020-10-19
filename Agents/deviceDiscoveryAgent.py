# -*- coding: utf-8 -*-
'''
Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''
import datetime
import importlib
import json
import netifaces as ni
import os
import re
import subprocess
import sys
import time
import settings
from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils.security import encrypt_value,decrypt_value
from bemoss_lib.utils.catcherror import getErrorInfo
from bemoss_lib.platform.BEMOSSThread import BThread
import traceback
# 1. @params agent

device_scan_time = 5*60
db_database = settings.DATABASES['default']['NAME']
db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']
db_table_device_info = settings.DATABASES['default']['TABLE_device_info']
db_table_supported_devices = settings.DATABASES['default']['TABLE_supported_devices']
db_table_device_type = settings.DATABASES['default']['TABLE_device_type']
db_oauth=settings.DATABASES['default']['TABLE_oauth']
device_monitor_time = settings.DEVICES['device_monitor_time']
PROJECT_DIR = settings.PROJECT_DIR
Applications_Launch_DIR = settings.Applications_Launch_DIR
Agents_Launch_DIR = settings.Agents_Launch_DIR


class DiscoveryAgent(BEMOSSAgent):

    def __init__(self,*args, **kwargs):
        super(DiscoveryAgent, self).__init__(*args, **kwargs)
        # Connect to database
        sys.path.append(PROJECT_DIR)

        self.device_scan_time = device_scan_time
        self.scan_for_devices = True
        self.gateway_discovery_finished= True
        self.discovery_list = list()
        #self.discovery_list.append('ICM100')
        print self.discovery_list


        self.new_discovery=True
        self.no_new_discovery_count=0

        try:
            # Find total number of devices in the dashboard_device_info table
            time.sleep(0.5) #small pause to let the metadataagent properly start
            self.dbcon.execute("SELECT * FROM "+db_table_device_info)
            self.device_num = self.dbcon.rowcount  # count no. of devices discovered by Device Discovery Agent
            print "{} >> there are existing {} device(s) in database".format(self.agent_id, self.device_num)
            #if self.device_num != 0:  # change network status of devices to OFF (OFFLINE)
            #    rows = self.dbcon.fetchall()
            #    for row in rows:
            #        dbcon.execute("UPDATE "+db_table_device_info+" SET device_status=%s", ("OFF",))
            #        dbcon.commit()
        except Exception as er:
            print "exception: ",er
            self.device_num = 0
        self.subscribe('gateway_discovered_devices',self.gateway_discovered_devices)
        self.subscribe('discovery_request',self.manualDiscoveryBehavior)
        self.setup()
        self.run()

    def setup(self):
        #super(DiscoveryAgent, self).setup()
        '''Discovery Processes'''
        pass

    def deviceDiscoveryBehavior(self, dbcon, discovery_message):
        print "Start Discovery Process--------------------------------------------------"
        # Update bemossdb miscellaneous and bemoss_notify tables with discovery start
        dbcon.execute("UPDATE miscellaneous SET value = 'ON' WHERE key = 'auto_discovery'")
        dbcon.commit()
        # Send message to UI about discovery start
        topic = 'discovery_request_response'
        message = 'ON'
        message = message.encode(encoding='utf_8')
        self.bemoss_publish(target=['ui'],topic=topic,message=message)
        #self.vip.pubsub.publish('pubsub',topic, headers, message)

            #run one discovery cycle for selected devices
        self.deviceScannerCycle(dbcon, discovery_message)
        # keep track of consecutive discovery cycles with no new discovered device
        self.local_discovery = True
        if self.gateway_discovery_finished and not self.already_published:
            self.already_published=True
            # Update bemossdb miscellaneous and bemoss_notify tables with discovery end
            dbcon.execute("UPDATE miscellaneous SET value = 'OFF' WHERE key = 'auto_discovery'")
            dbcon.commit()
        print "Stop Discovery Process--------------------------------------------------"

    def isCloud(self,dbcon, model):
        dbcon.execute("SELECT is_cloud_device from " + db_table_supported_devices
                      + " where device_model=%s", (model,))
        is_cloud = dbcon.fetchone()[0]
        if is_cloud is not None:
            return is_cloud
        else:
            return False

    def deviceScannerCycle(self,dbcon, discovery_message):
        self.new_discovery=False
        gateway_devices=dict()
        building_id = discovery_message['building_id']
        account_id = discovery_message['account_id']
        discoverylist = discovery_message['devices']
        for model in discoverylist:
            if not self.isCloud(dbcon,model):
                gateway_devices[model] = None  # in future append any model specific parameters here
        self.already_published = False
        if gateway_devices.keys() and self.gateway_exists_and_approved(dbcon, building_id):
            def respond_discover():
                time.sleep(settings.gateway_discover_response_timeout)
                message = {"GATEWAY ID": None}
                self.bemoss_publish(target="devicediscoveryagent", topic="gateway_discovered_devices",
                                          message=message, sender=self)

            send_to_gateway=dict()
            send_to_gateway["BUILDING_ID"]=building_id
            send_to_gateway["MODEL_NAMES"]=gateway_devices
            self.gateway_discovery_finished=False
            self.local_discovery=False
            self.bemoss_publish(target="gatewayagent", topic='gateway_discover'+'_'+str(building_id), message=send_to_gateway, sender=self)
            parallelThread = BThread(target=respond_discover,name="respond_discover")
            parallelThread.id = -1
            parallelThread.daemon = True
            parallelThread.start()
            parallelThread.id = self.id

        print "Start Discovery Cycle--------------------------------------------------"
        print "{} >> device next scan time in {} sec".format(self.agent_id, str(self.device_scan_time ))
        self.device_discovery_start_time = datetime.datetime.now()
        print "{} >> start_time {}".format(self.agent_id, str(self.device_discovery_start_time))
        print "{} >> is trying to discover all available devices\n".format(self.agent_id)
        api_map=dict()
        baseclassdict= dict()
        for discover_device_model in discoverylist:
            dbcon.execute("SELECT api_name from "+db_table_supported_devices
                                         +" where device_model=%s",(discover_device_model,))
            if dbcon.rowcount:
                deviceapi = dbcon.fetchone()[0]
                api_class = self.return_APImodule(deviceapi).__class__
                while api_class and "discover" not in api_class.__dict__:
                    api_class=api_class.__base__
                if api_class not in baseclassdict:
                    baseclassdict[api_class] = deviceapi
                    if deviceapi not in api_map:
                        api_map[deviceapi] = [discover_device_model]
                    else:
                        api_map[deviceapi] += [discover_device_model]
                else:
                    sibling_api = baseclassdict[api_class]
                    api_map[sibling_api] += [discover_device_model]

            else:
                print discover_device_model + " is not supported"

        self.infoLog(__name__,str(api_map),comments="These things will be attempted to be discovered")
        self.findDevices(dbcon,api_map,building_id,account_id )
        self.debugLog(__name__,comments="Stop Discovery Cycle")

    def findDevices(self, dbcon, api_map,building_id,account_id):
        #******************************************************************************************************
        #api_map has dictionary where key is api and value is a list of models
        #this function should discover devicess for those api and models and update the database
        self.num_new_Devices = 0
        for API, modellist in api_map.iteritems():
            self.num_new_Devices = 0
            self.infoLog(__name__,payload=str(modellist),comments="{} API is finding available devices ...".format(API))
            discovery_module = self.return_APImodule(API)
            dbcon.execute("SELECT is_cloud_device from " + db_table_supported_devices
                             + " where api_name=%s", (API,))
            is_cloud = dbcon.fetchone()
            dbcon.execute("SELECT device_model,address from " + db_table_supported_devices
                                + " where api_name=%s", (API,))
            ModelAddresspair = dbcon.fetchall()
            ModelAddressmap=dict((x, y) for x, y in ModelAddresspair)
            if list(set(ModelAddressmap.values()))[0]!=None:
                allmodellist=ModelAddressmap.keys()
            else:
                allmodellist=modellist
            if is_cloud is not None:
                is_cloud = is_cloud[0]
            discovered_devices = []
            if is_cloud:
                for model in allmodellist:
                    try:
                        login_infos = list()
                        dbcon.execute("SELECT * from passwords_manager where device_model=%s and building_id=%s", (model,building_id))
                        device_login_data = dbcon.fetchall()
                        if device_login_data:
                            for entry in device_login_data:
                                login_infos.append(
                                    {'username': entry[1].encode('utf8'), 'password': entry[2].encode('utf8')})
                        vendor = self.getvendor(dbcon,model)
                        dbcon.execute("SELECT token from " + db_oauth + " where service_provider=%s and building_id=%s",
                                            (vendor.lower(),building_id))
                        oauth_tokens = dbcon.fetchall()
                        if oauth_tokens:
                            for token in oauth_tokens[0]:
                                login_infos.append({'token': token})
                        if login_infos:
                            for login_info in login_infos:
                                newly_discovered_devices = []
                                if login_info.get('password'):
                                    password = decrypt_value(login_info.get('password'))
                                else:
                                    password = None
                                if list(set(ModelAddressmap.values()))[0] != None:
                                    try:
                                        newly_discovered_devices = discovery_module.discover(login_info.get('username'), password,
                                                                                  login_info.get('token'),
                                                                                  ModelAddressmap[model], model)
                                    except TypeError as e:  # if address is not required for API or "" go to old discovery
                                        newly_discovered_devices = discovery_module.discover(login_info['username'],
                                                                                  decrypt_value(
                                                                                      login_info['password']))
                                else:
                                    # Oauth devices
                                    newly_discovered_devices = discovery_module.discover(username=login_info.get('username'),
                                                                                   password=password,
                                                                                   token=login_info.get('token'))
                                for discovered_device in newly_discovered_devices:
                                    discovered_device['username'] = login_info.get('username')
                                    discovered_device['password'] = password
                                    discovered_device['token'] = login_info.get('token')

                                discovered_devices += newly_discovered_devices
                        else:
                            discovered_devices = list()
                            print "DeviceDiscoveryAgent: Couldn't find login info while trying to discover cloud device " + model
                    except Exception as er:
                        print er
                        print "DeviceDiscoveryAgent: ERROR occurred while trying to discover devices in " + API + ":" + str(
                            er)
                        self.infoLog(__name__,getErrorInfo(),header='devicediscoveryagent/discovery',comments="Failed during discovery")
            elif list(set(ModelAddressmap.values()))[0]!=None:
                #address can be a list if there are multiple devices with multiple addresses for that api
                for model,address in ModelAddresspair:
                    try:
                        local_devices = discovery_module.discover(address,model)
                        if local_devices:
                            discovered_devices=discovered_devices+local_devices
                    except Exception as e:
                        print e#if address is not required for API or "" go to old discovery
                        discovered_devices = discovery_module.discover()
            else:
                    discovered_devices = discovery_module.discover()
            if not discovered_devices: #no devices discovered for this API
                self.infoLog(__name__,comments="No devices discovered")
                continue
            self.infoLog(__name__,payload=str(discovered_devices),comments="Some devices are discovered")
            self.update_deviceinfo(dbcon, modellist,building_id, discovered_devices,account_id)


    def update_deviceinfo(self,dbcon, modellist, building_id,discovered_devices, account_id, gateway_discovery=False,gateway_id=None):

            for discovered_device in discovered_devices:
                devicemodel = discovered_device["model"]
                if devicemodel in modellist:

                    address = discovered_device["address"]
                    macaddress = discovered_device["mac"]
                    #print "{} >> Device discovered with address: {} and macaddress: {}".format(self.agent_id,address,macaddress)

                    if not gateway_discovery and not self.isCloud(dbcon,devicemodel):
                        #this means it is a local device. Do building_id insensetive-test
                        building_id_test = None #local (without gateway) device. Building_id doesn't matter. Only one unique MAC possible
                    else:
                        #is either a gateway device or a cloud device. Building_id matter; multiple same MAC possible
                        building_id_test = building_id

                    if self.checkMACinDB(dbcon, macaddress, account_id):
                        newdeviceflag = False
                        dbcon.execute("SELECT agent_id, address from device_info where device_model=%s and mac_address=%s", (devicemodel, macaddress))
                        res = dbcon.fetchone()
                        dbaddress = res[1]
                        dbagent_id = res[0]
                        if address != dbaddress:
                            self.infoLog(__name__,payload=address,
                                         comments="Address of device with mac {} changed from {}".format(macaddress,dbaddress))
                            dbcon.execute("UPDATE device_info SET address=%s WHERE agent_id=%s",(address,dbagent_id))
                            dbcon.commit()
                        else:
                            self.infoLog(__name__,comments='Device with Old Mac {}. No address changed '.format(macaddress))

                    #case2: new device has been discovered
                    else:
                        print '{} >> Device discovered with macaddress {} is a new find!'\
                            .format(self.agent_id, macaddress)
                        newdeviceflag = True

                    if newdeviceflag:
                        deviceModel = discovered_device["model"]
                        deviceVendor = discovered_device["vendor"]

                        print "{} >> Model: {} and Vendor: {}".format(self.agent_id,deviceModel,deviceVendor)

                        try:
                            dbcon.execute("SELECT * from "+db_table_supported_devices
                                             +" where vendor_name=%s and device_model=%s",(deviceVendor,deviceModel))
                            supported_entry = dbcon.fetchone()[0]
                            supported=True
                        except Exception as er:
                            print "exception: ",er
                            supported=False

                        if (supported):


                            self.device_num+=1
                            dbcon.execute("SELECT device_type_id from "+db_table_supported_devices
                                             +" where vendor_name=%s and device_model=%s",(deviceVendor,deviceModel))
                            device_type_id = dbcon.fetchone()[0]

                            dbcon.execute("SELECT device_type from "+db_table_device_type
                                             +" where id=%s",(str(device_type_id)))
                            device_type = dbcon.fetchone()[0]
                                 #attempting to make agent_id same for both gateway and cloud
                            device_id = discovered_device.get('agent_id') if 'agent_id' in discovered_device.keys() else deviceModel[:4].replace("-","")+"_"+macaddress+"_"+str(account_id)


                            dbcon.execute("SELECT identifiable from "+db_table_supported_devices
                                             +" where vendor_name=%s and device_model=%s",(deviceVendor,deviceModel))
                            identifiable = dbcon.fetchone()[0]

                            dbcon.execute("SELECT authorizable from "+db_table_supported_devices
                                             +" where vendor_name=%s and device_model=%s",(deviceVendor,deviceModel))
                            authorizable = dbcon.fetchone()[0]

                            dbcon.execute("SELECT communication from "+db_table_supported_devices
                                             +" where vendor_name=%s and device_model=%s",(deviceVendor,deviceModel))
                            communication = dbcon.fetchone()[0]

                            dbcon.execute("SELECT agent_type from " + db_table_supported_devices
                                          + " where vendor_name=%s and device_model=%s", (deviceVendor, deviceModel))
                            agent_type = dbcon.fetchone()[0]

                            deviceNickname = discovered_device.get('nickname') if 'nickname' in discovered_device.keys() else device_type + str(self.device_num)
                            username = discovered_device.get('username') if 'username' in discovered_device.keys() else None
                            password = discovered_device.get('password') if 'password' in discovered_device.keys() else None
                            config = discovered_device.get('config',None)
                            token=discovered_device.get('token') if 'token' in discovered_device.keys() else None
                            if gateway_discovery:
                                agent_type="gatewaydeviceagent"
                            device_config={"username":username,"password":encrypt_value(password),"token":token,"min_range":None,"max_range":None,"config":config,"gateway_device":gateway_discovery,"agent_type":agent_type}

                            dbcon.execute("INSERT INTO "+db_table_device_info+"(agent_id,vendor_name,device_model,mac_address,nickname,address,config,identifiable,authorizable,communication,date_added,approval_status,device_type_id,node_id,building_id,account_id,gateway_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                                     (device_id, deviceVendor, deviceModel, macaddress, deviceNickname, address, json.dumps(device_config),identifiable, authorizable, communication, str(datetime.datetime.now()), 'PND',device_type_id,0,building_id,account_id,gateway_id))
                            dbcon.commit()

                            self.num_new_Devices+=1
                            self.new_discovery=True
                        else:
                            print "{} >> This device currently is not supported by BEMOSS".format(self.agent_id)
                    else:
                        pass
            #Print how many WiFi devices this DeviceDiscoverAgent found!
            #print("{} >> Found {} new with {} API".format(self.agent_id,self.num_new_Devices,API))
            print " "

            return self.num_new_Devices

    def gateway_discovered_devices(self, dbcon, sender, topic, message):

        modellist = list()
        gateway_id=message["GATEWAY ID"]
        if gateway_id is not None:
            discovered_devices = message["DISCOVERED_DEVICES"]
            building_id = message["BUILDING ID"]
            for discovered_device in discovered_devices:
                modellist.append(discovered_device["model"])
            self.update_deviceinfo(dbcon,modellist,building_id,discovered_devices,gateway_discovery=True,gateway_id=gateway_id)
            if message["FINAL_MESSAGE"]:
                self.gateway_discovery_finished = True
                if not self.already_published and self.local_discovery:
                    self.already_published = True
                    dbcon.execute("UPDATE miscellaneous SET value = 'OFF' WHERE key = 'auto_discovery'")
                    dbcon.commit()
        else:

            dbcon.execute("UPDATE miscellaneous SET value = 'OFF' WHERE key = 'auto_discovery'")
            dbcon.commit()
            
    def getvendor(self,dbcon, model):
        dbcon.execute("SELECT vendor_name from " + db_table_supported_devices
                            + " where device_model=%s", (model,))
        Vendor_name = dbcon.fetchone()[0]
        return Vendor_name

    def return_APImodule(self, API):
        api_module = importlib.import_module("DeviceAPI." + API)
        discovery_module = api_module.API(parent=self)
        return discovery_module

    def manualDiscoveryBehavior(self, dbcon, sender, topic, message):


        #print discovery_model_names
        self.infoLog(__name__,payload=message,comments="Got discovery request")
        self.scan_for_devices = True
        try:
            self.deviceDiscoveryBehavior(dbcon, message)
        except:
            self.warningLog(__name__,payload=traceback.format_exc(),comments="Discovery failure")
            dbcon.execute("UPDATE miscellaneous SET value = 'OFF' WHERE key = 'auto_discovery'")
            dbcon.commit()
        # Send message to UI about discovery end
        message = 'OFF'
        message = message.encode(encoding='utf_8')

        self.bemoss_publish(target='ui',topic='discovery_request_response',message=message)


    def checkMACinDB(self, dbcon, macaddr, account_id):
        # if building_id is None:
        #     dbcon.execute(
        #         "SELECT agent_id FROM " + db_table_device_info + " WHERE mac_address='{}'".format(macaddr,))
        # else:
        #     # dbcon.execute("SELECT agent_id FROM "+db_table_device_info+" WHERE mac_address='{}' and building_id={}".format(macaddr,building_id,))
        #     dbcon.execute(
        #         "SELECT agent_id FROM " + db_table_device_info + " WHERE mac_address='{}'".format(
        #             macaddr,))
        #     #MAC now has to be unique across all buildings
        dbcon.execute(
            "SELECT agent_id FROM " + db_table_device_info + " WHERE mac_address='{}' and account_id='{}'".format(
                macaddr, account_id,))
        if dbcon.rowcount != 0:
            mac_already_in_db = True
        else:
            mac_already_in_db = False
        return mac_already_in_db

    def device_agent_still_running(self,agent_launch_filename):
        statusreply = subprocess.check_output( settings.PROJECT_DIR + '/env/bin/volttron-ctl status',shell=True)
        statusreply = statusreply.split('\n')
        agent_still_running = False
        reg_search_term = agent_launch_filename
        for line in statusreply:
            #print(line, end='') #write to a next file name outfile
            match = re.search(reg_search_term, line) and re.search('running', line)
            if match:  # The agent for this device is running
                agent_still_running = True
            else:
                pass
        return agent_still_running

    def write_launch_file(self, executable, deviceID, device_monitor_time, deviceModel, deviceVendor, deviceType,
                          api, address, macaddress, db_host, db_port, db_database, db_user, db_password):
        try:
            host_ip_address = ni.ifaddresses('eth0')[2][0]['addr']
        except Exception as er:
            print "exception: ",er
            host_ip_address = None
        if host_ip_address is None:
            try:
                host_ip_address = ni.ifaddresses('wlan0')[2][0]['addr']
            except Exception as er:
                print "exception: ",er
                pass

        else: pass
        data= {
                "agent": {
                    "exec": executable+"-0.1-py2.7.egg --config \"%c\" --sub \"%s\" --pub \"%p\""
                },
                "agent_id": deviceID,
                "device_monitor_time": device_monitor_time,
                "model": deviceModel,
                "vendor":deviceVendor,
                "type": deviceType,
                "api": api,
                "address": address,
                "macaddress": macaddress,
                "db_host": db_host,
                # "db_host": host_ip_address,
                "db_port": db_port,
                "db_database": db_database,
                "db_user": db_user,
                "db_password": db_password,
                "building_name": "bemoss",
                "zone_id" : 999
            }
        if 'ZigBee' in api:
            discovery_module = importlib.import_module("DeviceAPI.discoverAPI."+'ZigBee')
            gatewayid = discovery_module.getGateWayId()
            data['gateway_id'] = gatewayid
        __launch_file = os.path.join(Agents_Launch_DIR+deviceID+".launch.json")
        #print(__launch_file)
        with open(__launch_file, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)

if __name__ == '__main__':
    # Entry point for script
    print "This agent cannot be run as script."
