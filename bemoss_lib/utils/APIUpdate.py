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
#__created__ = "2017-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''

import os
import sys
import json
import importlib
import settings
os.chdir(os.path.expanduser( settings.PROJECT_DIR + "/"))
#os.system("service postgresql restart")
current_working_directory = os.getcwd()
sys.path.append(current_working_directory)
import psycopg2
import datetime
import netifaces as ni
import socket
import struct
import fcntl
import shutil
# CONFIGURATION ---------------------------------------------------------------------------------------------
#@params agent
agent_id = 'PlatformInitiator'

# @params DB interfaces
db_database = settings.DATABASES['default']['NAME']
db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']
db_table_building_zone = settings.DATABASES['default']['TABLE_building_zone']
db_table_global_zone_setting = settings.DATABASES['default']['TABLE_global_zone_setting']
db_table_holiday = settings.DATABASES['default']['TABLE_holiday']
db_table_device_info = settings.DATABASES['default']['TABLE_device_info']
db_table_device_model = settings.DATABASES['default']['TABLE_device_model']
db_table_application_running = settings.DATABASES['default']['TABLE_application_running']
db_table_application_registered = settings.DATABASES['default']['TABLE_application_registered']
db_table_device = settings.DATABASES['default']['TABLE_device']

db_table_alerts_notificationchanneladdress = settings.DATABASES['default'][
        'TABLE_alerts_notificationchanneladdress']
db_table_active_alert = settings.DATABASES['default']['TABLE_active_alert']
db_table_bemoss_notify = settings.DATABASES['default']['TABLE_bemoss_notify']
db_table_node_info = settings.DATABASES['default']['TABLE_node_info']

PROJECT_DIR = settings.PROJECT_DIR
Agents_Launch_DIR = settings.Agents_Launch_DIR
Loaded_Agents_DIR = settings.Loaded_Agents_DIR

# Autostart_Agents_DIR = settings.Autostart_Agents_DIR
Applications_Launch_DIR = settings.Applications_Launch_DIR
#----------------------------------------------------------------------------------------------------------

#1. Connect to bemossdb database
conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                            user=db_user, password=db_password)
cur = conn.cursor()  # open a cursor to perform database operations
print "{} >> Done 1: connect to database name {}".format(agent_id, db_database)

#2. clean tables



for file in os.listdir(os.path.expanduser(settings.PROJECT_DIR + "/DeviceAPI")):
    if file.startswith('API_') and file.endswith('.py'):
        try:
            file = file.split('.')[0]
            print file
            APImodule = importlib.import_module("DeviceAPI."+file)
            APIinstance = APImodule.API()
            API_infos = APIinstance.API_info()
            for API_info in API_infos:
                #TODO: Change column name device_type to device_type_id
                try:
                    if 'built_in_schedule_support' in API_info:
                        built_in_schedule_support = API_info['built_in_schedule_support']
                    else:
                        built_in_schedule_support = False

                    cur.execute("INSERT INTO supported_devices (device_model,vendor_name,communication,device_type_id,api_name,"
                            "html_template,chart_template,agent_type,identifiable,authorizable,is_cloud_device,support_oauth,"
                            "schedule_weekday_period,schedule_weekend_period,allow_schedule_period_delete,built_in_schedule_support) "
                            "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (API_info["device_model"],API_info["vendor_name"],API_info["communication"],API_info["device_type_id"],
                 API_info["api_name"],API_info["html_template"],API_info["chart_template"],API_info["agent_type"],API_info["identifiable"],
                 API_info["authorizable"],API_info["is_cloud_device"], API_info["support_oauth"], API_info["schedule_weekday_period"],
                 API_info["schedule_weekend_period"],API_info["allow_schedule_period_delete"],built_in_schedule_support))
                    conn.commit()
                except psycopg2.IntegrityError as ex:
                    # "UPDATE devicedata SET data=%s, dashboard_view=%s, last_update_time=%s WHERE agent_id=%s"
                    #            ,(json.dumps(new_data),json.dumps(Device.dashboard_view()),tzNow(),agent_id)"
                    conn.close()
                    conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                                            user=db_user, password=db_password)
                    cur = conn.cursor()  # open a cursor to perform database operations
                    cur.execute("UPDATE supported_devices SET vendor_name=%s, communication=%s, device_type_id=%s,"
                    "api_name=%s, html_template=%s, chart_template=%s, agent_type=%s, identifiable=%s, authorizable=%s, is_cloud_device=%s,"
                    "support_oauth=%s, schedule_weekday_period=%s, schedule_weekend_period=%s, allow_schedule_period_delete=%s,"
                    "built_in_schedule_support=%s where device_model=%s",(API_info["vendor_name"],API_info["communication"],API_info["device_type_id"],
                 API_info["api_name"],API_info["html_template"],API_info["chart_template"],API_info["agent_type"],API_info["identifiable"],
                 API_info["authorizable"],API_info["is_cloud_device"], API_info["support_oauth"], API_info["schedule_weekday_period"],
                 API_info["schedule_weekend_period"],API_info["allow_schedule_period_delete"],built_in_schedule_support,API_info["device_model"]))
                    conn.commit()
                    print "Updated the API"


        except Exception as er:
            raise
            print er
            print ("Error occurred while filling {} into supported_device table".format(file))

print "Table supported_devices populated successfully!"

# cur.execute("INSERT INTO node_info (node_id,node_name,node_type,node_model,node_status, building_name, ip_address, mac_address, associated_zone, date_added, communication, last_scanned_time, last_offline_time, node_resources_score) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
#                 (1, core_name, 'core', 'Odroid', 'ONLINE', 'blding', '192.168.10.234', 'test123abc', '999', datetime.datetime.now(), 'WiFi', None, None, 0.8))
# conn.commit()


cur.execute("UPDATE miscellaneous SET value='OFF' WHERE key='auto_discovery'")
conn.commit()

#8. close database connection
try:
    if conn:
        conn.close()
        print "{} >> Done 6: database {} connection is closed".format(agent_id, db_database)
except:
    print "{} >> database {} connection has already closed".format(agent_id, db_database)

#9. clear volttron log file, kill volttron process, kill all BEMOSS processes


