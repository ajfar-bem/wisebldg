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
import logging
import sys

from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.platform.agentstats import agentstats
from bemoss_lib.utils import db_helper
from bemoss_lib.utils import find_own_ip
from bemoss_lib.utils.BEMOSS_globals import *

#initiliazation
_log = logging.getLogger(__name__)
Agents_DIR = settings.Agents_DIR
clock_time = 20 #frequency of polling nodes
Agents_Launch_DIR = settings.Agents_Launch_DIR
building_name = settings.PLATFORM['node']['building_name']
db_database = settings.DATABASES['default']['NAME']

my_ip_address = find_own_ip.getIPs()[-1] #use the last IP in the list for host ip

debug_agent = settings.DEBUG
host_name = settings.PLATFORM['node']['name']
db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']
db_table_node_info = settings.DATABASES['default']['TABLE_node_info']
db_table_node_device = settings.DATABASES['default']['TABLE_node_device']
db_table_device_info = settings.DATABASES['default']['TABLE_device_info']
db_table_device_data = settings.DATABASES['default']['TABLE_device']
db_table_active_alert = settings.DATABASES['default']['TABLE_active_alert']
db_table_device_type = settings.DATABASES['default']['TABLE_device_type']
db_table_bemoss_notify = settings.DATABASES['default']['TABLE_bemoss_notify']
db_table_alerts_notificationchanneladdress = settings.DATABASES['default']['TABLE_alerts_notificationchanneladdress']
db_table_temp_time_counter = settings.DATABASES['default']['TABLE_temp_time_counter']
db_table_temp_failure_time = settings.DATABASES['default']['TABLE_temp_failure_time']
db_table_priority = settings.DATABASES['default']['TABLE_priority']

node_type = settings.PLATFORM['node']['type']
node_name = settings.PLATFORM['node']['name']
my_zone = settings.PLATFORM['node']['zone']

if node_type == "core":
    node_offline_timeout = settings.PLATFORM['node']['node_offline_timeout']
    node_monitor_time = settings.PLATFORM['node']['node_monitor_time']
else:
    node_monitor_time = 60000000  # arbitrary large number since it's not required for type "node"
    node_offline_timeout = 60000000  # arbitrary large number since it's not required for type "node"

#offline_event var


class NetworkAgent(BEMOSSAgent):

    def __init__(self, *args, **kwargs):
        super(NetworkAgent, self).__init__(*args,**kwargs)
        self.agent_id = kwargs['name']
        self.building_name = building_name
        self.host_ip_address = my_ip_address
        self.db_host = db_host
        self.host_name = host_name
        self.host_type = settings.PLATFORM['node']['type']
        self.host_building_name = building_name

        self.my_node_id = db_helper.get_node_id()

        print "host_zone_id "+str(self.my_node_id)

        self.time_sent_notifications = {}
        self.subscribe('update_parent',self.updateParent)
        self.subscribe('status_change',self.on_match_change)
        self.run()

    def updateParent(self,dbcon, sender,topic, message):
        print "Updating Connection to database"
        dbcon.close()  # close old connection
        dbcon = db_helper.db_connection()  # start new connection using new parent_ip


    def on_match_change(self,dbcon, sender,topic, message):
        #can approve or make pending a list of agents
        if debug_agent:
            print "{} >> received the message at {}".format(self.agent_id, datetime.datetime.now())
            print "Topic: {topic}".format(topic=topic)
            print "Message: {message}\n".format(message=message)
        APRlist=list()
        PNDlist=list()
        NBMlist=list()
        status_change=dict()
        for entry in message:
            if entry["agent_status"]=="start":
                APRlist.append(entry["agent_id"])
            elif entry["agent_status"]=="stop":
                PNDlist.append(entry["agent_id"])
            else:
                NBMlist.append(entry["agent_id"])
        status_change["APR"]=APRlist
        status_change["PND"] = PNDlist
        status_change["NBM"] = NBMlist
        self.bemoss_publish("gatewayagent","gateway_device_status_update",status_change)
        for entry in message:
            platform_agents_status = agentstats()
            agent_status = entry[STATUS_CHANGE.AGENT_STATUS]
            if STATUS_CHANGE.NODE in entry:
                requested_node_id = int(entry[STATUS_CHANGE.NODE])
            agent_id = entry[STATUS_CHANGE.AGENT_ID]
            is_app=False
            dbcon.execute('select agent_id from device_info where agent_id=%s',(agent_id,))
            if dbcon.rowcount:
                is_app = False
            dbcon.execute('select app_agent_id from application_running where app_agent_id=%s',(agent_id,))
            if dbcon.rowcount:
                is_app = True

            if 'is_app' in entry:
                is_app = entry['is_app']


            zone_assignment_type = ZONE_ASSIGNMENT_TYPES.TEMPORARY #default zone assignment type

            if STATUS_CHANGE.NODE_ASSIGNMENT_TYPE in entry:
                zone_assignment_type =  entry[STATUS_CHANGE.NODE_ASSIGNMENT_TYPE]

            running = False
            installed = False
            if agent_id in platform_agents_status:
                installed = True
                running = platform_agents_status[agent_id] == 'running'

            if agent_status == 'start' and requested_node_id == self.my_node_id:
                if not running:
                    if not is_app:
                        self.initialize_devicedata(dbcon, agent_id)
                    self.launch_agent(dbcon,agent_id,installed,is_app)
            elif running and (requested_node_id != self.my_node_id or agent_status == 'stop'):
                self.stopAgent(agent_id)
                continue
            else:
                continue
            dbcon.execute("SELECT assigned_node_id FROM "+db_table_node_device+ " WHERE agent_id=%s",  (agent_id,))
            if dbcon.rowcount == 0:
                # update node_device_table with the new zone of a device
                dbcon.execute("INSERT INTO "+db_table_node_device+" (agent_id, assigned_node_id,current_node_id,date_move) "
                                                                     "VALUES(%s,%s,%s,%s)",
                                 (agent_id, requested_node_id, requested_node_id, datetime.datetime.now()))
                dbcon.commit()
            else:
                existing_assigned_node_id = dbcon.fetchone()
                if zone_assignment_type == ZONE_ASSIGNMENT_TYPES.PERMANENT:
                    new_assigned_node_id = requested_node_id
                else:
                    new_assigned_node_id = existing_assigned_node_id
                dbcon.execute("UPDATE "+db_table_node_device+" SET assigned_node_id=(%s),current_node_id=(%s), \
                date_move=(%s) WHERE agent_id=(%s)",(new_assigned_node_id, requested_node_id, datetime.datetime.now(), agent_id))
                dbcon.commit()



    def initialize_devicedata(self, dbcon, agent_id):

        if agent_id in settings.SYSTEM_AGENTS:
            return #System agents already have configuration json file
        dbcon.execute("SELECT data FROM " + db_table_device_data + " WHERE agent_id=%s", (agent_id,))
        if dbcon.rowcount == 0:
            # no entry made for this agent
            json_temp = '{}'
            dbcon.execute(
                "INSERT INTO " + db_table_device_data + " (agent_id, data,network_status,last_scanned_time,last_offline_time,dashboard_view) "
                                                        "VALUES(%s,%s,%s,%s,%s,%s)",
                (agent_id, json_temp, 'ONLINE', datetime.datetime.now(), None, json_temp))
            dbcon.commit()

    def launch_agent(self,dbcon, agent_id, installed, is_app=False):
        #_launch_file = os.path.join(dir, launch_file)

        if agent_id in settings.SYSTEM_AGENTS:
            self.bemoss_publish(target='platformmanager',topic='launch_agent',message=(agent_id+' '+agent_id))

        else:
            if not is_app:
                gateway_device=self.is_gateway_device(dbcon,agent_id)
                if not gateway_device:
                    dbcon.execute("select device_model from device_info where agent_id=(%s)", (agent_id,))
                    if not dbcon.rowcount:
                        print "Bad agent_id name"
                        return
                    device_model = dbcon.fetchone()[0]

                    dbcon.execute("select agent_type from supported_devices where device_model=(%s)",(device_model,))
                    if not dbcon.rowcount:
                        print "Non supported device"
                        return
                    agent_name = dbcon.fetchone()[0]
                else:
                    agent_name = "gatewaydeviceagent"  #todo take care of thermostat agent
            else:
                dbcon.execute("select app_type_id from application_running where app_agent_id=(%s)", (agent_id,))
                app_type_id = dbcon.fetchone()[0]
                dbcon.execute("select app_name from application_registered where application_id=(%s)", (app_type_id,))
                agent_name = dbcon.fetchone()[0]

            self.bemoss_publish(target='platformmanager', topic='launch_agent',message=(agent_name + ' ' + agent_id))


        print "{} >> has successfully launched {} located in {}".format(self.agent_id, agent_id, dir)

    def stopAgent(self, agent_id):
        self.bemoss_publish(target='platformmanager', topic='stop_agent', message=agent_id)

def main(argv=sys.argv):
    print "This agent cannot be run as script."


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
