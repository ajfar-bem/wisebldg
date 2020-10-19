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

# }}}


import importlib
import json
import socket
import sys
from datetime import datetime

import settings
from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils import db_helper
from bemoss_lib.utils.security import decrypt_value


class GatewayDeviceAgent(BEMOSSAgent):
    def __init__(self, *args, **kwargs):

        super(GatewayDeviceAgent, self).__init__(*args, **kwargs)
        self.variables = kwargs
        self.variables = dict()

        def valid_ip(ip):
            parts = ip.split('.')
            return (
                len(parts) == 4
                and all(part.isdigit() for part in parts)
                and all(0 <= int(part) <= 255 for part in parts)
            )

        # 1. @params agent
        self.device_monitor_time = int(settings.DEVICES['device_monitor_time'])
        self.max_monitor_time = int(settings.DEVICES['max_monitor_time'])
        self.already_offline = False

        # 3. DB interfaces
        # TODO get database parameters from settings.py, add db_table for specific table
        self.db_host = settings.DATABASES['default']['HOST']
        self.db_port = settings.DATABASES['default']['PORT']
        self.db_database = settings.DATABASES['default']['NAME']
        self.db_user = settings.DATABASES['default']['USER']
        self.db_password = settings.DATABASES['default']['PASSWORD']
        self.db_table_active_alert = settings.DATABASES['default']['TABLE_active_alert']
        self.db_table_bemoss_notify = settings.DATABASES['default']['TABLE_bemoss_notify']
        self.db_table_alerts_notificationchanneladdress = settings.DATABASES['default'][
            'TABLE_alerts_notificationchanneladdress']
        self.db_table_temp_time_counter = settings.DATABASES['default']['TABLE_temp_time_counter']
        self.db_table_priority = settings.DATABASES['default']['TABLE_priority']
        self.zone_id = settings.PLATFORM['node']['zone']

        # 2. @params device_info
        # TODO correct the launchfile in Device Discovery Agent
        self.dbcon.execute('select device_type_id, device_model, address,config, identifiable, '
                           'mac_address from device_info where agent_id=%s', (self.agent_id,))
        info = self.dbcon.fetchone()

        self.device_type_id = info[0]
        self.device_model = info[1]
        self.device_config = info[3]
        self.mac_address = info[5]
        if self.device_config:
            if self.device_config.get("password") != None:
                self.password = decrypt_value(self.device_config.get("password"))
            else:
                self.password = None
            self.username = self.device_config.get("username")
            self.token = self.device_config.get("token")

        self.address = info[2]
        _address = self.address
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
        self.ip_address = ip_address if ip_address != None else None
        self.identifiable = info[5]

        self.changed_variables = None
        self.db_table_device = settings.DATABASES['default']['TABLE_device']

        # 4. @params device_api
        self.dbcon.execute('select (api_name) from supported_devices where device_model=%s', (self.device_model,))
        api_info = self.dbcon.fetchone()

        self.api = api_info[0]
        apiLib = importlib.import_module("DeviceAPI." + self.api)

        # 4.1 initialize device object
        self.Device = apiLib.API(model=self.device_model, api=self.api, address=self.address,
                                 mac_address=self.mac_address, username=self.username, password=self.password,
                                 agent_id=self.agent_id, parent=self, token=self.token, api_config=self.device_config)

        print(
        "{0}agent is initialized for {1} using API={2} at {3}".format(self.agent_id, self.Device.get_variable('model'),
                                                                      self.Device.get_variable('api'),
                                                                      self.Device.get_variable('address')))

        if 'default_monitor_interval' in self.Device.API_info()[0]:
            self.device_monitor_time = self.Device.API_info()[0]['default_monitor_interval']

        self.dbcon.execute(
            "UPDATE " + self.db_table_device + " SET dashboard_view=%s WHERE agent_id=%s",
            (json.dumps(self.Device.dashboard_view()), self.agent_id,))
        self.dbcon.commit()

        # Initialize ONLINE status, in case of previous offline. In consistent with self.already_offline == False.
        self.updateDB(self.dbcon, self.db_table_device, 'network_status', 'agent_id', 'ONLINE', self.agent_id)

        # Generating log variables
        log_variables = {'user': 'text'}
        for var in self.Device.ontology().values():
            log_variables[var.NAME] = var.TYPE
        self.log_variables = log_variables

        # TODO: Uncomment below when the API side's dashboard_view is ready

        # 5. topics define:
        self.monitor_topic='gateway_monitor_data'
        self.update_ui_topic = 'device_status'
        self.device_identify_topic = 'identify'
        self.device_control_topic = 'update'
        self.skip_backup = True
        self.setup(self.dbcon)
        self.identify = False
        self.identify_response=False
        self.runPeriodically(self.MonitorgatewayBehaviour, self.device_monitor_time)
        self.runPeriodically(self.backupSaveData, self.max_monitor_time)
        self.last_gateway_message=datetime.now()
        self.subscribe(topic=self.monitor_topic, callback=self.deviceMonitorBehavior)  #I think shuld have subscribe topic as gatewayid/agentid
        #sef.variable
        self.subscribe(topic=self.update_ui_topic, callback=self.updateUIBehavior)
        self.subscribe(topic=self.device_identify_topic, callback=self.deviceIdentifyBehavior)
        self.subscribe(topic=self.device_control_topic, callback=self.deviceControlBehavior)
        self.subscribe(topic='gateway_control_response',callback=self.control_response)
        self.run()

    def setup(self,dbcon):
        """
        Setup code goes here. Inherited agents can put their special initialization code here. Their __init__ code won't
        #run because the call to super's __init__ method is blocking
        :return:
        """
        self.initialize_devicedata(dbcon)
        pass

    def set_variable(self, k, v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self,k,default=None):
        return self.variables.get(k, default)  #  default of get_variable is none

    def backupSaveData(self, dbcon):
        print 'backup saving data'
        if self.skip_backup:  # skip the first call which happens at the agent start
            self.skip_backup = False
            return

        try:
            api_vars = dict(self.variables)
            api_vars['user'] = 'backupsave'
            self.TSDInsert(self.agent_id, api_vars, self.log_variables)
            print('Every Data Pushed to cassandra')
        except Exception as er:
            print("ERROR: {} fails to update cassandra database".format(self.agent_id))
            print er

    def renewConnection(self):
        self.Device.renewConnection()

    # 4. updateUIBehavior (generic behavior)
    def updateUIBehavior(self, sender, topic, message):
        print "{} agent got\nTopic: {topic}".format(self.get_variable("agent_id"), topic=topic)
        print "Message: {message}\n".format(message=message)
        # reply message
        self.updateUI()

    def updateUI(self):
        _data = self.variables
        message = json.dumps(_data)
        message = message.encode(encoding='utf_8')
        self.bemoss_publish(topic='device_status_response', target='ui', message=message)

    def deviceIdentifyBehavior(self,dbcon, sender, topic, message):
        self.identify_return_entry=sender
        print "{} agent got\nTopic: {topic}".format(self.get_variable("agent_id"), topic=topic)
        print "Message: {message}\n".format(message=message)
        # step1: change device status according to the receive message
        identifyDevice = self.Device.preidentify_message()
        if identifyDevice:
            self.deviceControlBehavior( dbcon,sender, "Initial_identify", identifyDevice)

        # step2: send reply message back to the UI

    def MonitorgatewayBehaviour(self,dbcon):

        diff = datetime.now()-self.last_gateway_message
        time = divmod(diff.days * 86400 + diff.seconds, 60)
        time_seconds=time[0]*60+time[1]
        if time_seconds>(self.device_monitor_time+60): #todo + 60 not needed
            print("updating offline count")
            self.deviceMonitorBehavior(dbcon,"gatewayDeviceAgent","offline_check",{})

    def convertDeviceStatus(self, data):

        for variable_name in data.keys():
            if data[variable_name]=="":
                continue
            if variable_name in self.Device.ontology().keys():
                ont = self.Device.ontology()[variable_name]
                if ont.TYPE in ['float','double']:
                    try:
                        val = round(float(data[variable_name]),2)
                    except (TypeError, ValueError):
                        val = None
                elif ont.TYPE in ['string','text']:
                    val = str(data[variable_name])
                elif ont.TYPE in ['int']:
                    try:
                        val=int(data[variable_name])
                    except (TypeError, ValueError):
                        val = None
                else:
                    val = data[variable_name]
                self.set_variable(ont.NAME, val)

    def deviceControlBehavior(self, dbcon, sender, topic, message):
        # print received message from UI
        print "{} agent got\nTopic: {topic}".format(self.get_variable("agent_id"), topic=topic)
        print "Message: {message}\n".format(message=message)
        if topic=="Initial_identify":
            self.identify=True
        elif topic=="Final_identify":
            self.identify=False
        # topic to/<receive_entity>/topic/from/<return_entity>/<optional: republished>
        self.return_entity = sender
        # step1: change device status according to the receive message
        if self.isPostmsgValid(message):
            # _data = json.loads(message)
            _data = message
            _data_complete = dict(_data)
            payload=dict()
            payload["AGENT_ID"]=self.agent_id
            payload["POSTMSG"]=_data_complete
            gateway_id=self.getgateway_id(dbcon,self.agent_id)
            self.bemoss_publish("gatewayagent",'gateway_device_control'+'_'+str(gateway_id),payload)
            # setDeviceStatusResult = self.Device.setDeviceStatus(json.loads(message)) #convert received message from string to JSON

            # TODO need to do additional checking whether the device setting is actually success!!!!!!!!
            # step3: send reply message back to the UI
            # No matter success or failure, record this attempt anyway.
            self.TSDInsert(self.agent_id, _data_complete, self.log_variables)
        else:
            print("The POST message is invalid, check brightness, status or color setting and try again\n")
            message = 'failure'


    def control_response(self,dbcon, sender, topic, message):
        if self.identify:
            self.identify_response=True
            identifyDevice = self.Device.postidentify_message()
            self.deviceControlBehavior(dbcon, sender, "Final_identify", identifyDevice)
        elif self.identify_response:
            self.identify_response=False
            self.bemoss_publish(topic='identify_response', target=self.identify_return_entry, message=message)
        else:
            self.bemoss_publish(topic='update_response', target=self.return_entity, message=message)
        # self.deviceMonitorBehavior()

    def isPostmsgValid(self, postmsg):
        # check validity of postmsg, this method will be overwritten by child class method
        dataValidity = True
        return dataValidity

    def updateOfflineCount(self,getDeviceStatusResult):
        if getDeviceStatusResult == True:
            self.set_variable('offline_count', 0)
        else:
            self.set_variable('offline_count', self.get_variable('offline_count',0) + 1)

    def isChanged(self, variable_name, value1, value2):
        return True if value1 != value2 else False

    def deviceMonitorBehavior(self,dbcon, sender, topic, message):
        # step1: Send collected message items as .variables
        if sender=="gatewayagent":
            self.last_gateway_message=datetime.now()


        getDeviceStatusResult=True
        if not message:
            getDeviceStatusResult = False
        else:
            self.Device.convertDeviceStatus(message)
        self.updateOfflineCount(getDeviceStatusResult)
        self.changed_variables = dict()
        for v in self.log_variables:
            if v in self.Device.variables:
                if not v in self.variables or self.isChanged(v, self.variables[v], self.Device.variables[v]):
                    self.variables[v] = self.Device.variables[v]
                    self.changed_variables[v] = self.log_variables[v]
            else:
                if v not in self.variables:  # it won't be in self.variables either (in the first time)
                    self.changed_variables[v] = self.log_variables[v]
                    self.variables[v] = None
        try:

            # Put scan time in database
            _time_stamp_last_scanned = datetime.now()
            dbcon.execute("UPDATE " + self.db_table_device + " SET last_scanned_time=%s "
                                                             "WHERE agent_id=%s",
                          (_time_stamp_last_scanned, self.agent_id))
            dbcon.commit()
        except Exception as er:
            print er
            print("ERROR: {} failed to update last scanned time".format(self.agent_id))

        self.onlineOfflineDetection(dbcon)
        if len(self.changed_variables) == 0:
            print 'nothing changed'
            return

        self.updateUI()

        # step4: update PostgresQL (meta-data) database
        self.updatePostgresDB(dbcon)

        # step5: update Cassandra (time-series) database
        self.saveCassandraDB()

    def saveCassandraDB(self):
        try:
            # log data to cassandra
            self.variables['user'] = 'device_monitor'
            self.TSDInsert(self.agent_id, self.variables, self.log_variables)
            print('Data Pushed to cassandra')
            print "{} success update database".format(self.agent_id)

        except Exception as er:
            print("ERROR: {} fails to update cassandra database".format(self.agent_id))
            print er

    def onlineOfflineDetection(self, dbcon):

        if self.get_variable('offline_count') >= 3:
            self.updateDB(dbcon, self.db_table_device, 'network_status', 'agent_id', 'OFFLINE', self.agent_id)
            if self.already_offline is False:
                self.already_offline = True
                _time_stamp_last_offline = str(datetime.now())
                self.updateDB(dbcon, self.db_table_device, 'last_offline_time', 'agent_id', _time_stamp_last_offline,
                              self.agent_id)
                # Save offline event in DB
                nickname = db_helper.get_device_nickname(dbcon, self.agent_id)
                self.EventRegister(dbcon, 'device-offline', reason='communication-error', source=nickname)

        elif self.get_variable('offline_count') == 0:
            self.updateDB(dbcon, self.db_table_device, 'network_status', 'agent_id', 'ONLINE', self.agent_id)
            if self.already_offline == True:
                self.already_offline = False
                # Save online event in DB
                nickname = db_helper.get_device_nickname(dbcon, self.agent_id)
                self.EventRegister(dbcon, 'device-online', reason='communication-restored', source=nickname)

    def updatePostgresDB(self, dbcon):
        try:
            post_data = dict()
            for k in self.log_variables.keys():
                if k == 'offline_count' or k == 'user':
                    pass
                else:
                    value = self.get_variable(k)
                    if value is not None:
                        post_data[k] = value

            self.updateDB(dbcon, self.db_table_device, 'data', 'agent_id', json.dumps(post_data), self.agent_id)
            self.updateDB(dbcon, self.db_table_device, 'dashboard_view', 'agent_id',
                          json.dumps(self.Device.dashboard_view()),
                          self.agent_id)

            print("{} updates the Postgresql during deviceMonitorBehavior successfully".format(self.agent_id))
        except Exception as er:
            print (er)
            print("ERROR: {} failed to update the Postgresql.".format(self.agent_id))

    def updateDB(self, dbcon, table, column, column_ref, column_data, column_ref_data):
        dbcon.execute("UPDATE " + table + " SET " + column + "=%s "
                                                             "WHERE " + column_ref + "=%s",
                      (column_data, column_ref_data))
        dbcon.commit()

    def initialize_devicedata(self, dbcon):

        dbcon.execute("SELECT data FROM " + self.db_table_device + " WHERE agent_id=%s", (self.agent_id,))
        if dbcon.rowcount == 0: #initialize only if blank
            # no entry made for this agent
            json_temp = '{}'
            dbcon.execute(
                "INSERT INTO " + self.db_table_device + " (agent_id, data,network_status,last_scanned_time,last_offline_time,dashboard_view) "
                                                        "VALUES(%s,%s,%s,%s,%s,%s)",
                (self.agent_id, json_temp, 'ONLINE', datetime.now(), None, json_temp))
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
