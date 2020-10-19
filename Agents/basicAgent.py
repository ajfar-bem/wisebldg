# -*- coding: utf-8 -*- {{{
# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright (c) 2013, Battelle Memorial Institute
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.
#

# This material was prepared as an account of work sponsored by an
# agency of the United States Government.  Neither the United States
# Government nor the United States Department of Energy, nor Battelle,
# nor any of their employees, nor any jurisdiction or organization
# that has cooperated in the development of these materials, makes
# any warranty, express or implied, or assumes any legal liability
# or responsibility for the accuracy, completeness, or usefulness or
# any information, apparatus, product, software, or process disclosed,
# or represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or
# service by trade name, trademark, manufacturer, or otherwise does
# not necessarily constitute or imply its endorsement, recommendation,
# r favoring by the United States Government or any agency thereof,
# or Battelle Memorial Institute. The views and opinions of authors
# expressed herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY
# operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830

#}}}


import importlib
import json
import socket
import sys
from datetime import datetime, timedelta
from queue import Empty
import settings
from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils import db_helper
from bemoss_lib.utils.security import decrypt_value
import threading
from queue import Queue
import traceback
import re
import urllib2
import threading
from bemoss_lib.utils.catcherror import getErrorInfo
from bemoss_lib.platform.platformData import logQueue
from bemoss_lib.utils.date_converter import tzNow
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY

CAPTURE_ID = "Nest_02AA01AC021503FG_1"

class BasicAgent(BEMOSSAgent):

    def __init__(self, *args, **kwargs):

        super(BasicAgent, self).__init__(*args,**kwargs)
        self.variables = kwargs
        self.variables = dict()
        self.monitorQ = Queue()
        self.controlQ = Queue()
        self.dblock = threading.Lock()

        #1. @params agent
        self.device_monitor_time =int(settings.DEVICES['device_monitor_time'])
        self.max_monitor_time =int(settings.DEVICES['max_monitor_time'])
        self.already_offline = False

        #3. DB interfaces
        #TODO get database parameters from settings.py, add db_table for specific table
        self.zone_id = settings.PLATFORM['node']['zone']

        # 2. @params device_info
        # TODO correct the launchfile in Device Discovery Agent
        # TODO: Uncomment below when the API side's dashboard_view is ready

        #5. topics define:
        self.update_ui_topic = 'device_status'
        self.device_identify_topic = 'identify'
        self.device_control_topic = 'update'
        self.skip_backup = True
        self.setup(self.dbcon)
        self.firstTimeMonitored = dict()

        for i in range(50):
            self.runContinuously(self.deviceMonitorBehavior)

        for i in range(20):
            self.runContinuously(self.deviceControlBehavior)

        self.runPeriodically(self.fillMonitorQ,self.device_monitor_time)

        #self.subscribe(topic=self.update_ui_topic, callback=self.updateUIBehavior)
        #self.subscribe(topic=self.device_identify_topic, callback=self.deviceIdentifyBehavior)
        self.subscribe(topic=self.device_control_topic, callback=self.fillControlQ)
        self.subscribe(topic='onDemandMonitor',callback=self.onDemandMonitor)

        self.debugLog(__name__,comments="startedBasicAgent")
        self.run()

    def setup(self,dbcon):
        """
        Setup code goes here. Inherited agents can put their special initialization code here. Their __init__ code won't
        #run because the call to super's __init__ method is blocking
        :return:
        """
        #self.initialize_devicedata(dbcon)
        pass

    def set_variable(self,k,v):  # k=key, v=value
        self.variables[k] = v
    
    def get_variable(self,k):
        return self.variables.get(k, None)

    def updateUI(self,new_data,agent_id):
        message = json.dumps(new_data)
        message = message.encode(encoding='utf_8')
        self.debugLog(__name__,str(message),comments="Message being sent to UI")
        self.bemoss_publish(topic='device_status_response',target='ui',message=message,sender=agent_id)


    # def deviceIdentifyBehavior(self,dbcon,sender,topic,message):
    #     print "{} agent got\nTopic: {topic}".format(self.get_variable("agent_id"),topic=topic)
    #     print "Message: {message}\n".format(message=message)
    #     #step1: change device status according to the receive message
    #     identifyDeviceResult = self.Device.identifyDevice()
    #     #TODO need to do additional checking whether the device setting is actually success!!!!!!!!
    #     #step2: send reply message back to the UI
    #     return_entity = sender
    #     if identifyDeviceResult:
    #         message = 'success'
    #     else:
    #         message = 'failure'
    #     self.bemoss_publish(topic='identify_response',target=return_entity,message=message)


    def fillControlQ(self,dbcon,sender,topic,message):

        agent_id = message.get('agent_id','')
        self.debugLog(__name__,message,header=agent_id+'/'+topic,comments="Filling control Q")
        self.controlQ.put((sender,topic,message))

    def deviceControlBehavior(self, dbcon):
        #print received message from UI

        try:
            sender, topic, message = self.controlQ.get(True,30)
        except Empty:
            return


        agent_id = message['agent_id']

        self.infoLog(__name__, message, header=agent_id + "/" + topic, comments="Processing control request")

        Device, TSDTablename = self.getAPI(agent_id)

        log_variables = {'user': 'text'}
        device_variables = []
        for var in Device.ontology().values():
            log_variables[var.NAME] = var.TYPE
            device_variables.append(var.NAME)

        if 'scheduleData' in message:
            message['scheduleData'] = self.convertSchdeuleType(message['scheduleData'])

        if "locked_variables" in message:
            with self.dblock:
                self.dbcon.execute("UPDATE devicedata SET locked_variables=%s WHERE agent_id=%s",(json.dumps(message['locked_variables']),agent_id))
                self.dbcon.commit()

        #topic to/<receive_entity>/topic/from/<return_entity>/<optional: republished>
        return_entity = sender
        #step1: change device status according to the receive message
        if self.isPostmsgValid(message):
            # _data = json.loads(message)
            _data = message
            _data_complete = dict(_data)

            with self.dblock:
                self.dbcon.execute('select data from devicedata where agent_id=%s', (agent_id,))
                if self.dbcon.rowcount:
                    old_data = self.dbcon.fetchone()[0]
                else:
                    old_data = dict()

            old_data.update(_data_complete)

            with self.dblock:
                self.dbcon.execute("UPDATE devicedata SET data=%s WHERE agent_id=%s",(json.dumps(old_data),agent_id))
                self.dbcon.commit()

            if 'user' in _data:
                user = _data.pop('user')
            else:
                user = 'unknown-UI'
                _data_complete['user'] = 'unknown-UI'
            # setDeviceStatusResult = self.Device.setDeviceStatus(json.loads(message)) #convert received message from string to JSON
            try:
                Device.setDeviceStatus(message)
            except:
                message = 'failure'
                self.warningLog(__name__, payload=getErrorInfo(),header=agent_id, comments="Device Control Failure")
            else:
                message = 'success'
                self.infoLog(__name__, header=agent_id + "/" + topic, comments="Device Control Success")
            # No matter success or failure, record this attempt anyway.
            try:
                self.TSDInsert(agent_id, _data_complete, log_variables, tablename=TSDTablename)
            except:
                self.warningLog(__name__, payload=getErrorInfo()+" "+str(_data_complete), header=agent_id,
                                comments="Inserting control data to TSD failure")
            else:
                self.warningLog(__name__, payload=str(_data_complete), header=agent_id,
                                comments="Inserting control data to TSD Success")
        else:
            message = 'failure'

        if return_entity:
            self.bemoss_publish(topic='update_response',target=return_entity,message=message,sender=agent_id)

        self.monitorQ.put(agent_id,block=False) #also flag for immediate monitoring


    def isPostmsgValid(self, postmsg):
        # check validity of postmsg, this method will be overwritten by child class method
        dataValidity = True
        return dataValidity

    def isChanged(self, variable_name, value1, value2):
        return True if value1 != value2 else False

    def getAPI(self,agent_id):
        def valid_ip(ip):
            parts = ip.split('.')
            return (
                len(parts) == 4
                and all(part.isdigit() for part in parts)
                and all(0 <= int(part) <= 255 for part in parts)
            )

        with self.dblock:
            self.dbcon.execute('select device_type_id, device_model, address,config, identifiable, '
                               'mac_address, nickname, building_id from device_info where agent_id=%s', (agent_id,))
            info = self.dbcon.fetchone()


        device_type_id = info[0]
        device_model = info[1]
        device_config = info[3]
        mac_address = info[5]
        nickname = info[6]
        building_id = info[7]
        if device_config:
            if device_config.get("password") != None:
                password = decrypt_value(device_config.get("password"))
            else:
                password = None
            username = device_config.get("username")
            token = device_config.get("token")
        else:
            username = None
            password = None
            token = None

        address = info[2]
        if address:
            _address = address
            _address = _address.replace('http://', '')
            _address = _address.replace('https://', '')
            try:  # validate whether or not address is an ip address
                socket.inet_aton(_address)
                if valid_ip(_address):
                    ip_address = _address
                else:
                    ip_address = None
            except socket.error:
                ip_address = None
            ip_address = ip_address if ip_address != None else None
        identifiable = info[5]


        # 4. @params device_api
        with self.dblock:
            self.dbcon.execute('select (api_name) from supported_devices where device_model=%s', (device_model,))
            api_info = self.dbcon.fetchone()

        api = api_info[0]
        apiLib = importlib.import_module("DeviceAPI." + api)

        # 4.1 initialize device object
        Device = apiLib.API(model=device_model, api=api, address=address, nickname=nickname,
                                 mac_address=mac_address, username=username, password=password,
                                 agent_id=agent_id, parent=self, token=token, api_config=device_config)

        TSDTablename = "B"+ str(building_id) + "_" + device_model.replace(" ","_").replace("-","_")
        TSDTablename = re.sub(r'\W', '_',TSDTablename)
        return Device, TSDTablename

    def onDemandMonitor(self, dbcon, sender, topic, message):
        agent_id = message.get('agent_id', '')
        self.debugLog(__name__, message, header=agent_id + '/' + topic, comments="Filling monitor Q on Demand")
        self.monitorQ.put(agent_id,block=False)

    def fillMonitorQ(self,dbcon):
        this_thread = threading.currentThread()
        this_thread.name = "FillMonitorQ"
        with self.dblock:
            self.dbcon.execute('select agent_id from device_info where approval_status=%s',("APR",))
            approved_agents = self.dbcon.fetchall()
        with self.dblock:
            self.dbcon.execute('select agent_id from devicedata where network_status=%s', ("ONLINE",))
            online_agents = self.dbcon.fetchall()
        with self.dblock:
            self.dbcon.execute('select agent_id, last_scanned_time from devicedata where network_status=%s', ("OFFLINE",))
            offline_agents = self.dbcon.fetchall()
        offline_agent_dict = dict()
        for offline_agent, last_scan_time  in offline_agents:
            offline_agent_dict[offline_agent] = last_scan_time



        for agent_id in approved_agents:
            this_thread.name = "DeviceMonitorQ/" + agent_id[0]
            if agent_id in online_agents or agent_id[0] not in offline_agent_dict:
                self.monitorQ.put(agent_id[0],block=False)
                self.debugLog(__name__, header=agent_id[0], comments="Device Put to monitor Queue")
            else:
                time_diff = tzNow() - offline_agent_dict[agent_id[0]]
                if time_diff > timedelta(minutes=30) or time_diff < timedelta(minutes=2.5): #2.5 to let it make a second attempt
                    self.monitorQ.put(agent_id[0], block=False)
                    self.debugLog(__name__, header=agent_id[0], comments="Offline Device attempt to monitor Queue")

    def deviceMonitorBehavior(self,dbcon):
        # step1: get current status of a thermostat, then map keywords and variables to agent knowledge
        try:
            agent_id = self.monitorQ.get(True,30)
        except Empty:
            return

        if agent_id == CAPTURE_ID:
            print "Captured"
        this_thread = threading.currentThread()
        this_thread.name = "DeviceMonitoring/"+agent_id

        self.debugLog(__name__, header=agent_id, comments="Device being processed for monitoring")

        Device, TSDTablename = self.getAPI(agent_id)

        # Generating log variables
        log_variables = {'user': 'text'}
        for var in Device.ontology().values():
            log_variables[var.NAME] = var.TYPE

        default_data = Device.default_variables
        existing_data = default_data
        with self.dblock:
            self.dbcon.execute('select data from devicedata where agent_id=%s',(agent_id,))
            if self.dbcon.rowcount == 0:  # initialize with default data if blank
                # no entry made for this agent
                self.dbcon.execute(
                    "INSERT INTO devicedata (agent_id, data,network_status,last_scanned_time,last_offline_time,dashboard_view,locked_variables) "
                    "VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    (agent_id, json.dumps(default_data), 'ONLINE', tzNow(), None, '{}','{}'))
                self.dbcon.commit()
                existing_data = default_data
            else:
                existing_data = self.dbcon.fetchone()[0]
                if not existing_data:
                    self.dbcon.execute("UPDATE devicedata SET data=%s WHERE agent_id=%s",
                                       (json.dumps(default_data), agent_id))
                    self.dbcon.commit()
                    existing_data = default_data


        ##This correcting code can be eliminated in a prefectly running system, since, all the default values must
        ##have been added to DB in the first run. However, if the code is updated and new default values has been added
        ##this code can help fill them
        missing_flag = False
        for key, value in default_data.items():
            if key not in existing_data:
                existing_data[key] = value
                missing_flag = True

            if missing_flag: #if the existing entry has some missing default values, add them
                with self.dblock:
                    self.dbcon.execute("UPDATE devicedata SET data=%s WHERE agent_id=%s",
                                       (json.dumps(existing_data), agent_id))
                    self.dbcon.commit()
        ###############################
        _time_stamp_last_scanned = tzNow()
        with self.dblock:
            self.dbcon.execute("UPDATE devicedata SET last_scanned_time=%s "
                                                            "WHERE agent_id=%s",
                         (_time_stamp_last_scanned, agent_id))
            self.dbcon.commit()

        new_data = {}
        try:
            deviceData = Device.getDeviceStatus()
        except:
            self.warningLog(__name__, payload=getErrorInfo(),header=agent_id, comments="Device monitoring failed")
            with self.dblock:
                self.dbcon.execute("select network_status from devicedata WHERE agent_id=%s",
                                   (agent_id,))
                status = self.dbcon.fetchone()[0]
                if status == "ONLINE":
                    self.dbcon.execute("UPDATE devicedata SET network_status=%s "
                                       "WHERE agent_id=%s",
                                       ("OFFLINE",agent_id))
                    self.dbcon.execute("UPDATE devicedata SET last_offline_time=%s "
                                       "WHERE agent_id=%s",
                                       (_time_stamp_last_scanned, agent_id))
                    self.dbcon.commit()

            return
        else:
            with self.dblock:
                self.dbcon.execute("select network_status from devicedata WHERE agent_id=%s",
                                   (agent_id,))
                status = self.dbcon.fetchone()[0]
                if status == "OFFLINE":
                    self.dbcon.execute("UPDATE devicedata SET network_status=%s "
                                       "WHERE agent_id=%s",
                                       ("ONLINE",agent_id))
                    self.dbcon.commit()

        for v in deviceData.keys():
            if not v in existing_data or self.isChanged(v, existing_data[v], deviceData[v]):
                new_data = deviceData #if there is any difference, then get the new data
                break


        if agent_id == CAPTURE_ID:
            print "Captured"

        #self.onlineOfflineDetection(dbcon,Device,agent_id) #OFFLINE detection should be based on last scanned time
        if not new_data and agent_id in self.firstTimeMonitored:
            with self.dblock:
                self.dbcon.execute("select last_update_time from devicedata where agent_id=%s",(agent_id,))
                last_update_time = self.dbcon.fetchone()[0]
            if last_update_time and tzNow()-last_update_time > timedelta(seconds=self.max_monitor_time):
                self.debugLog(__name__, header=agent_id, comments="No changes on data but doing backup save")
            else:
                self.debugLog(__name__, header=agent_id, comments="No changes on data during monitoring; Ignorning")
                return
        else:
            self.debugLog(__name__, payload=new_data, header=agent_id, comments="Data changed during monitoring")

        existing_data.update(new_data)
        new_data = existing_data

        self.updateUI(new_data,agent_id)
        if 'scheduleData' in new_data:
            self.updateScheduleToDB(agent_id,scheduleData=new_data['scheduleData'],dbcon=self.dbcon)

         #step4: update PostgresQL (meta-data) database
        #self.updateDB(self.dbcon, 'devicedata', 'data', 'agent_id', new_data, agent_id)
        with self.dblock:
            self.dbcon.execute("UPDATE devicedata SET data=%s, dashboard_view=%s, last_update_time=%s WHERE agent_id=%s"
                               ,(json.dumps(new_data),json.dumps(Device.dashboard_view()),tzNow(),agent_id))
            self.dbcon.commit()

        new_data['user'] = 'device_monitor'
        #step5: update Cassandra (time-series) database
        self.TSDInsert(agent_id,new_data,log_variables,tablename=TSDTablename)
        self.firstTimeMonitored[agent_id] = True
        self.checkTampering(agent_id) #


    def getScheduledValues(self,agent_id, testDate):
        #get the scheduled variables and values at testDate if schedule exist for the given agent_id
        with self.dblock:
            self.dbcon.execute("SELECT schedule from schedule_data WHERE agent_id=%s"
                               ,(agent_id,))
            if self.dbcon.rowcount:
                schedule_data = self.dbcon.fetchone()[0]
            else:
                return {}

        active_schedule_typ = schedule_data['active']
        if active_schedule_typ == 'everyday':
            active_schedule = schedule_data['schedulers'][active_schedule_typ]
            daysofweek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            todayDay = daysofweek[testDate.weekday()]
            yesterdayDay = daysofweek[testDate.weekday() - 1]

            TodaysSchedule = active_schedule[todayDay]
            YesterdaysSchedule = active_schedule[yesterdayDay]
            if not TodaysSchedule or not YesterdaysSchedule:
                return {} #no schedule data

            nowminute = testDate.hour * 60 + testDate.minute
            current_schedule = YesterdaysSchedule[-1] #initialize at yesterday's last schedule
            for entry in TodaysSchedule:
                if nowminute > entry['at']:
                    current_schedule = entry

            current_schedule.pop('at')
            current_schedule.pop('id')
            current_schedule.pop('nickname')
            return current_schedule

        else:
            raise Exception("Unsupported Active Schedule Type")



    def withinRange(self,value1,value2,range):
        if range is None:
            return value1 == value2
        if type(range) == list:
            return value1 in range

        if type(range) in [int,float]:
            if abs(value1-value2) <= range:
                return True
            else:
                return False


    def checkTampering(self,agent_id):
        with self.dblock:
            self.dbcon.execute("SELECT data, locked_variables from devicedata WHERE agent_id=%s"
                               ,(agent_id,))
            result = self.dbcon.fetchone()
            current_data = result[0]
            locked_variables = result[1]

        scheduled_vars = self.getScheduledValues(agent_id,tzNow())
        imminent_scheduled_vars = self.getScheduledValues(agent_id,tzNow()+timedelta(minutes=1))

        update_locked_variables_value={}
        tampered_variables_restore = {}
        locked_variables_updated_flag = False
        #IF variables has changed from locked variable, and is also not because of schedule, then it's tampering
        for current_var, current_value in current_data.items():
            if current_var in locked_variables:
                locked_var_val = locked_variables[current_var]['value']
                locked_var_range = locked_variables[current_var]['range']
                if not self.withinRange(current_value,locked_var_val,locked_var_range):
                    if current_var in scheduled_vars and (current_value == scheduled_vars[current_var] or current_value == imminent_scheduled_vars[current_value]):
                        #so the value changed from locked_value to scheduled_value; we need to update locked value
                        locked_variables[current_var]['value'] = current_value
                        locked_variables_updated_flag = True
                    else:
                        tampered_variables_restore[current_var] = locked_var_val #the_value

        if locked_variables_updated_flag:
            self.debugLog(source=__name__,payload=locked_variables,header=agent_id+'\tampering_lock_update',
                          comments="Locked Value has been updated from schedule.")
            with self.dblock:
                self.dbcon.execute("UPDATE devicedata SET locked_variables=%s WHERE agent_id=%s"
                                   ,(locked_variables,agent_id,))
                self.dbcon.commit()

        if tampered_variables_restore:
            tampered_variables_restore['agent_id'] = agent_id
            tampered_variables_restore['user'] = 'anti-tampering'
            self.infoLog(__name__, tampered_variables_restore, header=agent_id + '/' + "anti-tampering-restore",
                          comments="Tampering Detected: "+str(tampered_variables_restore) + "Changed to:" + str(current_data))
            self.controlQ.put(("", "anti-tampering-restore", tampered_variables_restore))



    def convertSchdeuleType(self,schedule):
        _new_schedule_object = schedule
        weeklySchedule = _new_schedule_object['schedulers']['everyday']
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        newSchedule = dict()
        for day in days:
            newSchedule[day] = [
                [x['nickname'], int(x['at']), int(float(x['cool_setpoint'])), int(float(x['heat_setpoint']))]
                for x in weeklySchedule[day]]

        newSchedule['Enabled'] = True
        return newSchedule

    def updateScheduleToDB(self,agent_id,scheduleData, dbcon):

        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        index = 0
        everyday = dict()
        for day in days:
            everyday[day] = list()
            id = 0
            for entry in scheduleData[day]:
                everyday[day].append(dict(
                    {"at": str(entry[1]), "id": str(id), "nickname": entry[0], "cool_setpoint": str(entry[2]),
                     "heat_setpoint": str(entry[3])}))
                id += 1

        with self.dblock:
            dbcon.execute("SELECT schedule FROM schedule_data WHERE agent_id=%s",(agent_id,))
            if dbcon.rowcount:
                _old_schedule_object = dbcon.fetchone()[0]
                old_schedules = _old_schedule_object['schedulers']
                old_schedules['everyday'] = everyday
                _json_data = json.dumps(_old_schedule_object)
                dbcon.execute("UPDATE schedule_data SET schedule=%s WHERE agent_id=%s",(_json_data,agent_id))
                dbcon.commit()
            else:
                _json_data = json.dumps({"active": "everyday",
                        "schedulers": {"everyday": everyday}
                    })
                dbcon.execute("insert into schedule_data (agent_id, schedule) VALUES (%s, %s)",(agent_id,_json_data))
                dbcon.commit()


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    print "This agent cannot be run as script."


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
