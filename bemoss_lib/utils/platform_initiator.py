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
import os
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



# Clear temp folder
temp_path = os.path.expanduser(settings.PROJECT_DIR + "/.temp")
shutil.rmtree(temp_path)
os.mkdir(temp_path)

os.system("clear")
#1. Connect to bemossdb database
conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                            user=db_user, password=db_password)
cur = conn.cursor()  # open a cursor to perform database operations
print "{} >> Done 1: connect to database name {}".format(agent_id, db_database)

#2. clean tables
cur.execute("DELETE FROM node_device")
cur.execute("DELETE FROM "+db_table_device)
cur.execute("DELETE FROM "+db_table_device_info)
cur.execute("DELETE FROM "+db_table_global_zone_setting)
conn.commit()



cur.execute("select * from information_schema.tables where table_name=%s", (db_table_bemoss_notify,))
print bool(cur.rowcount)
if bool(cur.rowcount):
    cur.execute("DELETE FROM "+db_table_bemoss_notify)
    conn.commit()

cur.execute("select * from information_schema.tables where table_name=%s", ('holiday',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    cur.execute("DELETE FROM "+db_table_holiday)
    conn.commit()

cur.execute("select * from information_schema.tables where table_name=%s", ('devicedata',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    cur.execute("DELETE FROM "+db_table_device)
    conn.commit()


#3. adding holidays ref www.archieves.gov/news/federal-holidays.html
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 01, 01).date(), "New Year's Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 1, 16).date(), "Birthday of Martin Luther King Jr."))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 2, 20).date(), "President's Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 5, 29).date(), "Memorial Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 7, 4).date(), "Independence Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 9, 4).date(), "Labor Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 10, 9).date(), "Columbus Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 11, 10).date(), "Veterans Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 11, 23).date(), "Thanksgiving Day"))
cur.execute("INSERT INTO "+db_table_holiday+" VALUES(%s,%s)",
            (datetime.datetime(2017, 12, 25).date(), "Christmas Day"))
conn.commit()
print "{} >> Done 2: added holidays to {}".format(agent_id, db_table_holiday)






#8. create tables
cur.execute("select * from information_schema.tables where table_name=%s", ('application_running',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    cur.execute("DELETE FROM application_running")
    conn.commit()
else:
    pass



cur.execute("select * from information_schema.tables where table_name=%s", ('passwords_manager',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    print "table already exits. Clearing"
    cur.execute("DELETE FROM passwords_manager")
    conn.commit()

cur.execute("select * from information_schema.tables where table_name=%s", ('supported_devices',))
print bool(cur.rowcount)
if bool(cur.rowcount):
    print "table already exits. Dropping"
    cur.execute("DELETE FROM supported_devices")
    conn.commit()


cur.execute("DELETE FROM oauth_token")


# cur.execute("INSERT INTO node_info (node_id,node_name,node_type,node_model,node_status, building_name, ip_address, mac_address, associated_zone, date_added, communication, last_scanned_time, last_offline_time, node_resources_score) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
#                 (1, core_name, 'core', 'Odroid', 'ONLINE', 'blding', '192.168.10.234', 'test123abc', '999', datetime.datetime.now(), 'WiFi', None, None, 0.8))
# conn.commit()


cur.execute("UPDATE miscellaneous SET value='OFF' WHERE key='auto_discovery'")
conn.commit()

import APIUpdate #run the API update
#8. close database connection
try:
    if conn:
        conn.close()
        print "{} >> Done 6: database {} connection is closed".format(agent_id, db_database)
except:
    print "{} >> database {} connection has already closed".format(agent_id, db_database)

#9. clear volttron log file, kill volttron process, kill all BEMOSS processes


#TODO make a backup of log files

os.system("rm " + settings.PROJECT_DIR + "/log/cassandra.log")



