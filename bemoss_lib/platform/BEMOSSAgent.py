import re
import pytz
from datetime import datetime
from bemoss_lib.utils import date_converter
from bemoss_lib.utils import db_helper
import uuid
from bemoss_lib.utils.offline_table_init import *
import settings
import os
from bemoss_lib.platform.platformAgent import PlatformAgent

class BEMOSSAgent(PlatformAgent):


    def __init__(self, *args, **kwargs):
        super(BEMOSSAgent, self).__init__(*args, **kwargs)
        self.agent_id = kwargs['name']
        self.multinode_data = db_helper.get_multinode_data()
        self.node_name = self.multinode_data['this_node']
        if not os.path.isfile(settings.MULTINODE_PARENT_IP_FILE):  # but parent file doesn't exists
            parent_addr = self.multinode_data['known_nodes'][0]['address']
            parent_ip = self.extract_ip(parent_addr)
            with open(settings.MULTINODE_PARENT_IP_FILE, 'w') as f:
                f.write(parent_ip)
        self.subscription_dict = {}
        self.listenMessages(self.handle_message)



    def subscribe(self,topic,callback):
        if topic not in self.subscription_dict:
            self.subscription_dict[topic] = []
        self.subscription_dict[topic].append(callback)

    def remove_subscription(self,topic):
        if topic in self.subscription_dict:
            self.subscription_dict.pop(topic)

    def handle_message(self,dbcon,sender,topic,message):
        def isPrefix(prefix_str,main_str):
            try:
                return main_str.index(prefix_str) == 0
            except ValueError:
                return False

        if sender == "ui":
            if settings.DEBUG:
                print "message from UI: " + topic + " " + str(message)
        for subs_topic, func_list in self.subscription_dict.items():
            if isPrefix(subs_topic,topic):
                for func in func_list:
                    func(dbcon,sender,topic,message)


    def bemoss_publish(self,target,topic,message,sender=None):
        if type(target) != list:
            target = [target]
        if not sender:
            sender = self.name
        self.publish(sender, target,topic,message)

    def TSDInsert(self,agentID,all_vars,log_vars,cur_timeLocal=None,tablename=None):
        message = dict()
        all_vars = dict(all_vars)  # make a copy to prevent the source from being modified
        for key in all_vars.keys():
            if key not in log_vars:
                all_vars.pop(key)

        message['agentID'] = agentID
        message['all_vars'] = all_vars
        message['log_vars'] = log_vars
        message['cur_timeLocal'] = cur_timeLocal
        message['tablename'] = tablename
        self.bemoss_publish(target='tsdagent',topic='insert',message=message)

    def TSDCustomInsert(self, all_vars, log_vars, tablename):
        all_vars = dict(all_vars) #make a copy to prevent the source from being modified
        for key in all_vars.keys():
            if key not in log_vars:
                all_vars.pop(key)
        for key, val in all_vars.items():
            if log_vars[key] == "TIMESTAMP":
                all_vars[key] = date_converter.serializeDate(val)
            if log_vars[key] == 'UUID':
                all_vars[key] = str(val)

        message = dict()
        message['all_vars'] = all_vars
        message['log_vars'] = log_vars
        message['tablename'] = tablename
        self.bemoss_publish(target='tsdagent',topic='custominsert',message=message)

    def EventRegister(self,dbcon,event,reason=None,source=None,event_time=None,notify=True):
        evt_vars = dict()

        event_time = date_converter.localToUTC(event_time) if event_time else datetime.now(pytz.UTC)
        source = source if source else self.agent_id
        reason = reason if reason else 'Unknown'
        logged_by = self.agent_id

        evt_vars['date_id'] = str(event_time.date())
        evt_vars['logged_time'] = datetime.now(pytz.UTC)
        evt_vars['event_id'] = uuid.uuid4()
        evt_vars['time'] = event_time
        evt_vars['source'] = source
        evt_vars['event'] = event
        evt_vars['reason'] = reason
        evt_vars['logged_by']=logged_by
        evt_vars['node_name'] = self.node_name

        #save to cassandra
        self.TSDCustomInsert(all_vars=evt_vars, log_vars=EVENTS_TABLE_VARS,tablename=EVENTS_TABLE_NAME)
        if notify:
            #save to notification table
            localTime = date_converter.UTCToLocal(event_time)
            message = source + ' ' + event + '. Reason: ' + reason
            dbcon.execute("select id from possible_events where event_name=%s", (event,))
            event_id = dbcon.fetchone()[0]
            dbcon.execute("select building_id from device_info where agent_id=%s",(source))
            building_id = dbcon.fetchone()[0]
            dbcon.execute(
                "insert into notification (dt_triggered, seen, event_type_id, message, building_id) VALUES (%s, %s, %s, %s, %s)",
                (localTime, False, event_id, message, building_id))
            dbcon.commit()

    def extract_ip(self,addr):
        return re.search(r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', addr).groups()[0]

    def is_gateway_device(self,dbcon,agent_id):

        config = self.getdevice_config(dbcon,agent_id)
        if config is not None:
            gateway_device=config["gateway_device"]
            return gateway_device
        #raise

    def getdevice_config(self,dbcon,agent_id):

        dbcon.execute("SELECT config from device_info " + " where agent_id=%s", (agent_id,))
        config = dbcon.fetchone()[0]
        return config

    def gateway_exists_and_approved(self,dbcon,building_id):

        gateway_connected = False
        dbcon.execute("SELECT status from iot_gateway where building_id=%s", (building_id,))
        if dbcon.rowcount != 0:
            status_list = dbcon.fetchall()[0]
            for status in status_list:
                if status=="APR":
                    gateway_connected=True
        return gateway_connected

    def getgateway_id(self,dbcon,agent_id):

        dbcon.execute("SELECT gateway_id from device_info where agent_id=%s", (agent_id,))
        gateway_id = dbcon.fetchone()[0]
        return gateway_id

    def get_gateway_config(self,dbcon,gateway_id):#returns none if gateway doesn't exist
        dbcon.execute("SELECT * from " + "iot_gateway" + " where gateway=%s", (str(gateway_id),))
        if dbcon.rowcount:
            gateway_details = dbcon.fetchone()
            return gateway_details
        return None

