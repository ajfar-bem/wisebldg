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
import sys
import time
import uuid

from cassandra import cluster

from bemoss_lib.communication.Email import EmailService
from bemoss_lib.communication.sms import SMSService
from bemoss_lib.databases.cassandraAPI import cassandraDB
from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.platform.agentstats import agentstats
from bemoss_lib.utils import date_converter
from bemoss_lib.utils import db_helper
from bemoss_lib.utils import find_own_ip
from bemoss_lib.utils.BEMOSS_globals import *
from bemoss_lib.utils.catcherror import catcherror

debug_agent = settings.DEBUG
from bemoss_lib.utils.offline_table_init import *
import pytz

#1.Basic variables initialized

Agents_Launch_DIR = settings.Agents_Launch_DIR

Agents_DIR = settings.Agents_DIR
db_database = settings.DATABASES['default']['NAME']
db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']
db_table_node_device = settings.DATABASES['default']['TABLE_node_device']
db_table_device_info = settings.DATABASES['default']['TABLE_device_info']
db_table_node_info = settings.DATABASES['default']['TABLE_node_info']

multinode_data = db_helper.get_multinode_data()

node_name = multinode_data['this_node']

myips = find_own_ip.getIPs()
_email_subject = node_name+'@'+str(myips[0])
emailService = EmailService()

#email settings
email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
email_recipients = settings.NOTIFICATION['email']['recipients']
email_username = settings.NOTIFICATION['email']['username']
email_password = settings.NOTIFICATION['email']['password']
email_mailServer = settings.NOTIFICATION['email']['mailServer']


smsService = SMSService()
notify_heartbeat = settings.NOTIFICATION['heartbeat']

#Offline variables initialized

platform_table = 'platform_event'
platform_log_variables = {'agent_id':'text','start_time':'TIMESTAMP','event_id':'UUID','date_id':'text','end_time':'TIMESTAMP'}
platform_log_partition_keys = ['agent_id']
platform_log_clustering_keys = ['start_time','event_id']
#Start_time made the clustering key so that we can order the result by start_time and sort in desc order to find the latest entry
platform_variables=dict()

notification_table = 'email_sent'
notification_log_variables = {'agent_id': 'text', 'date_id': 'text', 'last_event_log_time': 'TIMESTAMP', 'email_sent_time': 'TIMESTAMP'}
notification_log_partition_keys = ['date_id']
notification_log_clustering_keys = ['last_event_log_time']
#Start_time made the clustering key so that we can order the result by start_time and sort in desc order to find the latest entry
notification_variables=dict()

class PlatformMonitorAgent(BEMOSSAgent):
    """Agent for querying WeatherUndergrounds API"""

    #1. agent initialization
    def __init__(self,*args, **kwargs):
        super(PlatformMonitorAgent, self).__init__(*args,**kwargs)

        self.agent_id = kwargs['name']
        multinode_data = db_helper.get_multinode_data()
        self.node_name = multinode_data['this_node']
        self.mynode = db_helper.get_node_id()

        self.poll_time = 60
        self.backup_poll_time = 300

        platform_variables['agent_id'] = self.agent_id + '_' + self.node_name
        notification_variables['agent_id'] = self.agent_id

        self.variables = kwargs
        self.db_host = db_host
        self.last_seen_dead = dict()
        self.cassandra_death_time = None #Arbitrary initialization
        self.cassandra_death_date = None
        self.crash_id = dict()
        self.last_event_log_time = None
        self.retry_resurrection = False
        self.setup_complete = False
        self.runPeriodically(self.agentMonitor, self.poll_time)
        self.runPeriodically(self.agentBackupMonitor, self.backup_poll_time,start_immediately=False)
        self.runPeriodically(self.eventMonitor, self.poll_time,start_immediately=False)
        self.run()

    def setup(self,dbcon):
        #Create offline_event table
        retry = True
        while retry:
            try:
                retry = False
                cassandraDB.createCustomTable(columns=EVENTS_TABLE_VARS, partition_keys=EVENTS_TABLE_PARTITION_KEYS,
                                              clustering_keys=EVENTS_TABLE_CLUSTERING_KEYS, tablename=EVENTS_TABLE_NAME)
            except cassandraDB.AlreadyExists as er:
                pass
            except (cluster.NoHostAvailable, cluster.OperationTimedOut) as er:
                print er
                print 'Retrying ...'
                retry = True
                time.sleep(10)
            except Exception as er:
                print er
                print 'Cannot create offline table'
                raise

        #Create platform_event table
        try:
            cassandraDB.createCustomTable(columns=platform_log_variables, partition_keys=platform_log_partition_keys,
                                          clustering_keys=platform_log_clustering_keys,tablename=platform_table)
        except cassandraDB.AlreadyExists as er:
            pass
        except Exception as er:
            print er
            print 'Cannot create platform table'
            raise

        #Create email_event table
        try:
            cassandraDB.createCustomTable(columns=notification_log_variables, partition_keys=notification_log_partition_keys,
                                          clustering_keys=notification_log_clustering_keys, tablename=notification_table)
        except cassandraDB.AlreadyExists as er:
            pass
        except Exception as er:
            print er
            print 'Cannot create email table'
            raise

        try:
            retrieve_vars = ['agent_id','start_time','end_time','event_id']
            result = cassandraDB.customQuery('SELECT {0} from {1} where agent_id=%s ORDER BY start_time DESC LIMIT 1'.\
                        format(', '.join(retrieve_vars),platform_table,self.agent_id),(platform_variables['agent_id'],))
        except Exception as er:
            print er
            print 'Error querrying platform table'
        else:
            if len(result)>0:
                last_entry = result[0]
                #Platformmonitor just started. Save last failure and current restart info
                #crash
                self.EventRegister(dbcon, 'shutdown',source=self.node_name,event_time=last_entry.end_time,notify=False)
                #restart
                self.EventRegister(dbcon, 'restart',source=self.node_name,notify=False)
            else:
                print 'Fresh boy'

            #Platform monitor agent fresh start. Save the event on platform_event table.
            #for reference: platform_log_variables = {'agent_id':'text','date_id':'text','start_time':'TIMESTAMP','end_time':'TIMESTAMP','event_id':'UUID'}
            platform_variables['start_time']=datetime.datetime.utcnow()
            platform_variables['date_id']=str(datetime.datetime.now().date())
            platform_variables['event_id']=uuid.uuid4()
            platform_variables['end_time']=datetime.datetime.utcnow()
            platform_variables['logged_time']=datetime.datetime.utcnow()
            self.TSDCustomInsert(platform_variables,platform_log_variables,platform_table)


    @catcherror('agentBackup Monitoring Failed')
    def agentBackupMonitor(self,dbcon):
        #clear the last_seen_dead set, so all agents are again attempted to be resurrected if required
        self.retry_resurrection = True

    #3. deviceMonitorBehavior (TickerBehavior)
    #@catcherror('agentMonitoring Failed @ platformmonitoragent')
    def agentMonitor(self,dbcon):
        if not self.setup_complete:
            self.setup(dbcon)
            self.setup_complete = True

        #Check if cassandra is available and update platform-running end time
        try:
            #Platfrom-monitor is running. Also serves to check if cassandra is running. Save every-poll-time. If it goes missing, means went off
            platform_variables['end_time']=datetime.datetime.utcnow()
            self.TSDCustomInsert(platform_variables,platform_log_variables,platform_table)
        except cluster.NoHostAvailable as er:
            #Cassandra offline. Save the offline time in temp variable
            print er
            print 'Cassandra Not available'
            if 'cassandra' not in self.last_seen_dead or self.retry_resurrection:
                if 'cassandra' not in self.last_seen_dead:
                    self.send_email('Cassandra Dead','Cassandra has gone offline. Please check asap. All logging has stopped')
                    self.last_seen_dead['cassandra']=datetime.datetime.now()
                    if self.cassandra_death_time is None:
                        self.cassandra_death_time = datetime.datetime.now(pytz.UTC)
                #TODO start cassandra
        else:
            #Cassandra Online Again
            if 'cassandra' in self.last_seen_dead:
                #Update the offline-table. Log both offline and online event
                self.EventRegister(dbcon, 'crash',source='cassandra',event_time=self.cassandra_death_time)
                self.EventRegister(dbcon, 'restart',reason='restart by PMA',source='cassandra')
                self.last_seen_dead.pop('cassandra')
                self.cassandra_death_time=None

        try:
            agentstatusresult = agentstats()
        except Exception as er:
            print er
            print 'Platform not running'
            if 'Platform' not in self.last_seen_dead:
                #Update Platform not running in the log databse
                self.last_seen_dead['Platform']=datetime.datetime.now()
                self.EventRegister(dbcon, 'crash',source='Platform')
            #If Platform not running, we are done
            return
        else:
            if 'Platform' in self.last_seen_dead:
                #Update Platform running again in Database
                self.last_seen_dead.pop('Platform')
                self.EventRegister(dbcon, 'restart',source='Platform')

        #Get #Get list of devices Serves to check if postgress is running
        try:
            rows = list()
            dbcon.execute("SELECT agent_id,approval_status,config from device_info")
            devices = dbcon.fetchall()
            dbcon.execute("SELECT application_running.app_agent_id, application_running.status,"
                          " application_registered.app_agent from application_running INNER JOIN application_registered"
                          " ON application_running.app_type_id = application_registered.application_id")
            apps = dbcon.fetchall()
            for app in apps:
                if app[1] in ['running','started']:
                    rows.append([app[0],'APR',app[2]])

                else:
                    rows.append([app[0],'PND',app[2]])

            for device in devices:
                agent_type=device[2]["agent_type"]
                rows.append([device[0],device[1],agent_type])

        except Exception as er:
            print er
            print 'Postgresql has failed'
            if 'postgresql' not in self.last_seen_dead:
                #Update postgresql down into database
                #postgresql goes offline; log it into database
                self.last_seen_dead['postgresql']=datetime.datetime.now()
                self.EventRegister('crash','postgresql')
            #Can't continue to restarting Agents, if prostgress is down. We don't know which agent are crashed, and which are regularly shutdown
            return
        else:
            if 'postgresql' in self.last_seen_dead:
                #Update postgresql up again into databse
                self.last_seen_dead.pop('postgresql')
                self.EventRegister(dbcon, 'restart',source='postgresql')

        #rows contains rows of agent_id,device_type_id, approval_status
        if rows:
            for row in rows:
                dbcon.execute("SELECT assigned_node_id,current_node_id FROM "+db_table_node_device+" WHERE agent_id=%s",
                                 (row[0],))
                if dbcon.rowcount == 0:
                    # print 'No info found for agent'
                    # print 'Assume node 0, then'
                    current_node = 0
                    assigned_node = 0
                else:
                    node_info = dbcon.fetchone()
                    current_node = node_info[1]
                    assigned_node = node_info[0]
                nickname = db_helper.get_device_nickname(dbcon,row[0])
                if row[0] in agentstatusresult:

                    if agentstatusresult[row[0]] in ['running']:
                        #device agent just starting, or already started; see if it was dead before:
                        if row[0] in self.last_seen_dead:
                            #Agent back after dead; update db
                            self.last_seen_dead.pop(row[0])
                            self.EventRegister(dbcon, 'restart',reason='restart by PMA',source=nickname)

                        if row[1].upper() not in ['APR','APPROVED'] or current_node != self.mynode:
                            #Stop the unapproved agent or agent on another node, if it is running
                            print 'Stopping unapproved agent: '+row[0]
                            self.bemoss_publish(target="platformmanager",topic="stop_agent",message=row[0])
                        #Nothing more to do with this agent
                        continue
                    else:
                        #device agent has crashed; proceed to start it if it was approved and belong to this node:
                        if current_node == self.mynode and row[1].upper() in ['APR', 'APPROVED']:
                            #Agent dead, which was supposed to be alive
                            if row[0] not in self.last_seen_dead or self.retry_resurrection:
                                print 'Found a dead agent, resurrecting: ' + row[0]
                                self.bemoss_publish(target='platformmanager',topic='start',message=row[0])
                                if row[0] not in self.last_seen_dead:
                                    #Freshly dead, log in DB
                                    self.last_seen_dead[row[0]]=datetime.datetime.now()
                                    self.EventRegister(dbcon, 'crash',source=nickname)
                            else:
                                #was dead before; ignore
                                print 'This agent is dead beyond resurrection: '+row[0]

                    agentstatusresult.pop(row[0]) #Done with this one
                else:
                    #found device that doesn't even have agent installed. Possibly, agent from previous run,
                    # or agent in another the node. Start it if it is on the same node and approved
                    if current_node == self.mynode and row[1].upper() in ['APR', 'APPROVED']:
                        #the agent is supposed to be running on this node
                        self.bemoss_publish(target='platformmanager',topic='launch_agent',message=row[2]+' '+row[0])
                    else:
                        #print "Agent from other node found, or agent not approved. Ignore. Agent on other node will be started by platformmonitor agent there"
                        pass



        for agent, status in agentstatusresult.items():
            if status not in ['running']:
                if agent not in self.last_seen_dead or self.retry_resurrection:
                    print 'Found a dead, non-device agent. Starting it up: '+agent
                    self.bemoss_publish(target='platformmanager',topic='start',message=agent)

                if agent not in self.last_seen_dead:
                    self.last_seen_dead[agent] = datetime.datetime.now()
                    #Agent Dead. Save in DB
                    self.EventRegister(dbcon, 'crash',source=agent)
                else:
                    print 'This agent is dead beyond resurrection: '+agent
            else:
                if agent in self.last_seen_dead:
                    #Agent just back from dead. Log in DB
                    self.last_seen_dead.pop(agent)
                    self.EventRegister(dbcon, 'restart',source=agent)
        #reset back the retry_resurrection variable to prevent attempting to resurrect repeatedly.
        self.retry_resurrection = False

    #@catcherror('email sending failed @ platformmonitoragent')
    def eventMonitor(self,dbcon):
        mydate = str(datetime.datetime.now().date())

        if self.last_event_log_time is None:
            email_vars = ['agent_id','date_id','last_event_log_time','email_sent_time']
            email_result = cassandraDB.customQuery('SELECT {0} from {1} where date_id=%s ORDER BY last_event_log_time DESC LIMIT 1'.format(', '.join(email_vars), notification_table), (mydate,))
            if len(email_result) > 0:
                self.last_event_log_time = email_result[0].last_event_log_time
            else:
                self.last_event_log_time = datetime.datetime.now(tz=pytz.UTC)

        offline_vars = EVENTS_TABLE_VARS.keys()

        if self.last_event_log_time is None:
            result = cassandraDB.customQuery('SELECT {0} from {1} where date_id=%s ORDER BY logged_time'.format(', '.join(offline_vars), EVENTS_TABLE_NAME), (mydate,))
        else:
            result = cassandraDB.customQuery('SELECT {0} from {1} where date_id=%s and logged_time>%s ORDER BY logged_time'.format(', '.join(offline_vars), EVENTS_TABLE_NAME), (mydate, self.last_event_log_time))

        event_count = 0
        result = list(result)


        if len(result) > 0:

            #create a map from all possible events to a list of notification addresses and their priority
            notificationchannel_map = dict()
            dbcon.execute("select id from possible_events") #get all possible event ids
            event_ids = dbcon.fetchall()
            for event_id in event_ids:
                #get all possible alert types associated with those events
                event_id = event_id[0]
                dbcon.execute("select alerttypes_id from alert_types_associated_events where possibleevents_id=%s",
                                    (event_id,))
                if dbcon.rowcount:
                    alert_types = dbcon.fetchall()
                    for alert_type in alert_types:
                        # get the alert and its priority assigned to that alert_type. If two alerts are tried to assign to same alert_type,
                        # they will be merged and hence, there will still be one-to-one relation
                        dbcon.execute("select id, priority_id from alerts where alert_type_id=%s", (alert_type,))
                        if dbcon.rowcount:
                            alert_and_priority_list = dbcon.fetchall()
                            #get all the notification addresses assigned to that alert
                            for alert_id, priority_id in alert_and_priority_list:
                                dbcon.execute(
                                    "select notificationchanneladdresses_id from alerts_alert_channels where alerts_id=%s",
                                    (alert_id,))
                                if dbcon.rowcount:
                                    notificationchannels = dbcon.fetchall()
                                    if event_id not in notificationchannel_map:
                                        notificationchannel_map[event_id] = dict()
                                    if priority_id not in notificationchannel_map[event_id]:
                                        notificationchannel_map[event_id][priority_id] = set()

                                    notificationchannel_map[event_id][priority_id].update(notificationchannels)

                #if there are two entries for the same channel for the same event with different priority, drop the lower priority
                if event_id in notificationchannel_map:
                    priorities = sorted(notificationchannel_map[event_id].keys())
                    for i in range(0,len(priorities)-1):
                        for j in range(i+1,len(priorities)):
                            overlap = notificationchannel_map[event_id][priorities[i]].intersection(notificationchannel_map[event_id][priorities[j]])
                            notificationchannel_map[event_id][priorities[i]] -= overlap

            # create a map of priority, notification_channel --> to list of events to send to that channel
            notification_map = dict()
            for event in result:

                # get event_id from the possible events table for current event
                dbcon.execute("select id from possible_events where event_name=%s", (event.event,))
                if dbcon.rowcount:
                    event_id = dbcon.fetchone()[0]
                    # get a dict of notification_priority, notification address) for this type of event from the map previously created
                    if event_id not in notificationchannel_map:
                        continue
                    prioritized_channels = notificationchannel_map[event_id]
                    for priority_id, notification_channels in prioritized_channels.items():
                        if priority_id not in notification_map:
                            notification_map[priority_id] = dict()
                        for (notification_channel,) in notification_channels:
                            if notification_channel not in notification_map[priority_id]:
                                notification_map[priority_id][notification_channel] = list()
                            # if there are two notification channel with two different priorities for the same event, the second priority takes over
                            notification_map[priority_id][notification_channel].append(event)

                self.last_event_log_time = event.logged_time
            dbcon.commit()
            notification_variables['date_id'] = mydate
            notification_variables['last_event_log_time'] = self.last_event_log_time
            notification_variables['email_sent_time'] = datetime.datetime.utcnow()
            self.TSDCustomInsert(notification_variables, notification_log_variables, notification_table)

            for priority in notification_map.keys():

                for notification_channel,eventlist in notification_map[priority].items():
                    dbcon.execute("select notification_channel.notification_channel, alerts_notificationchanneladdress.notify_address from alerts_notificationchanneladdress INNER JOIN notification_channel ON notification_channel.id=alerts_notificationchanneladdress.notification_channel_id  where alerts_notificationchanneladdress.id=%s",(notification_channel,))
                    channeltype, address = dbcon.fetchone()
                    if channeltype.lower()=="email":
                        report_lines = """
                            <html>
                            <head></head>
                            <body>
                            <p><b>Event Report</b></p>
                            """

                        for event in eventlist:
                            event_count += 1
                            report_lines += 'On '+str(date_converter.UTCToLocal(event.time).date()) + ', at '\
                                            +datetime.datetime.strftime(date_converter.UTCToLocal(event.time),'%H:%M:%S') + '<b> '+str(event.source) + ' : ' + str(event.event)+'</b> because of ' + str(event.reason)
                            report_lines += '<br/>'
                            self.last_event_log_time = event.logged_time

                        if event_count == 0:
                            return

                        report_lines += """
                        </body>
                        </html>
                        """
                        print report_lines
                        dbcon.execute("select priority_level from priority where id=%s",(priority,))
                        priority_text = dbcon.fetchone()[0] if dbcon.rowcount else ""
                        self.send_email(address,priority_text,report_lines)
                    elif channeltype.lower() =='text':
                        sms_text = ''
                        for event in eventlist:
                            sms_text += event.source + ' ' + event.event
                        self.send_sms(address,sms_text)


    @catcherror('email send function failed')
    def send_email(self,recipient,subject,text):
        emailService.sendEmail(email_fromaddr, [recipient], email_username, email_password, _email_subject+' '+subject, text, email_mailServer,html=True)

    @catcherror('SMS function failed')
    def send_sms(self, recipient, text):
        smsService.sendSMS(email_fromaddr, recipient, email_username, email_password, text, email_mailServer)


def main(argv=sys.argv):
    print "This agent cannot be run as script."


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
