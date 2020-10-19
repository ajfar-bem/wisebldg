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

__author__ = 'kruthika'
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)).replace('/run', ''))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_web_server.settings_tornado")
django.setup()

from webapps.alerts.models import PriorityLevels, NotificationChannels, AlertTypes, PossibleEvents
from webapps.deviceinfos.models import DeviceType, Miscellaneous
from webapps.bemoss_applications.models import ApplicationRegistered
# from webapps.buildingmap.models import Building_Zone, GlobalSetting
from django.contrib.auth.models import Group, Permission, User
from webapps.accounts.models import UserProfile
# from webapps.dashboard.models import GlobalSetting
from webapps.schedule.models import Holiday
from webapps.multinode.models import NodeInfo
# from webapps.discovery.models import Miscellaneous
import datetime

# zone_999 = Building_Zone(zone_id=999, zone_nickname="BEMOSS Core")
# zone_999.save()


#Adding global settings

# gz999 = GlobalSetting(id=999,heat_setpoint=70, cool_setpoint=72, illuminance=67, zone_id=999)
# gz999.save()


#User groups
admin = Group(id=1, name="Admin")
admin.save()

zonemgr = Group(id=2, name="Zone Manager")
zonemgr.save()

tenant = Group(id=3, name="Tenant")
tenant.save()

owner = Group(id=4, name="Owner")
owner.save()

#Add admin to user profile
admin = User.objects.get(username='admin')
admin.first_name = "Admin"
admin.save()
#userid = admin.id
#user_id = admin.id
#uprof = UserProfile.objects.create(user_id=userid, group_id=1, zone_id=999)
#uprof.save()
admin.groups.add(Group.objects.get(name='Admin'))
admin.save()

#Alerts and Notifications

#Priority
low_p = PriorityLevels(id=1, priority_level='Low', priority_notification_hours='12')
low_p.save()

med_p = PriorityLevels(id=2, priority_level='Warning', priority_notification_hours='4')
med_p.save()

high_p = PriorityLevels(id=3, priority_level='Critical', priority_notification_hours='1')
high_p.save()

#NotificationChannel
emailN = NotificationChannels(id=1, notification_channel='Email')
emailN.save()

textN = NotificationChannels(id=2, notification_channel='Text')
textN.save()

#Device Type
dt1 = DeviceType(id=1, device_type='HVAC')
dt1.save()

dt2 = DeviceType(id=2, device_type='Lighting')
dt2.save()

dt3 = DeviceType(id=3, device_type='Plugload')
dt3.save()

dt4 = DeviceType(id=4, device_type='Sensor')
dt4.save()

dt5 = DeviceType(id=5, device_type='Powermeter')
dt5.save()

dt6 = DeviceType(id=6, device_type='Der')
dt6.save()

dt7 = DeviceType(id=7, device_type='Camera')
dt7.save()

evt = PossibleEvents(id=1,event_name="device-offline",event_description="A device becomes offline because of communication problem")
evt.save()

evt1 = PossibleEvents(id=2,event_name="device-online",event_description="A device becomes online because of communication restore")
evt1.save()

evt2 = PossibleEvents(id=3,event_name="node-offline",event_description="A BEMOSS node becomes offline because of communication problem or node crash")
evt2.save()

evt3 = PossibleEvents(id=4,event_name="node-online",event_description="A BEMOSS node becomes online because of communication restoration or node restart")
evt3.save()


evt4 = PossibleEvents(id=5,event_name="hvac-fault",event_description="An anamoly has been detected on a HVAC device")
evt4.save()

evt5 = PossibleEvents(id=6,event_name="hvac-fault-cleared",event_description="An anamoly has cleared")
evt5.save()

evt7 = PossibleEvents(id=7,event_name="device-tampering",event_description="A device has been tampered with")
evt7.save()

evt8 = PossibleEvents(id=8,event_name="shutdown",event_description="BEMOSS system shutdown")
evt8.save()

evt9 = PossibleEvents(id=9,event_name="restart",event_description="The entity was restarted")
evt9.save()

evt10 = PossibleEvents(id=10,event_name="crash",event_description="The entity crashed")
evt10.save()

#Event Trigger
et1 = AlertTypes(id=1, alert_description="Device goes offline", alert_name="device_offline")
et1.save()
et1.associated_events.add(evt,evt1)
et1.save()

et2 = AlertTypes(id=2, alert_description="BEMOSS node goes offline", alert_name="node_offline")
et2.save()
et2.associated_events.add(evt2,evt3)
et2.save()


et3 = AlertTypes(id=3, alert_description="HVAC fault", alert_name="hvac_fault")
et3.save()
et3.associated_events.add(evt4,evt5)
et3.save()

et4 = AlertTypes(id=4, alert_description="Thermostat Tampering", alert_name="device_tampering")
et4.save()
et4.associated_events.add(evt7)
et4.save()

et5 = AlertTypes(id=5, alert_description="System Events", alert_name="system_events")
et5.save()
et5.associated_events.add(evt8,evt9,evt10)
et5.save()
#
# et4 = EventTrigger(id=4, device_type_id=9, event_trigger_desc="Any BEMOSS Node Offline", event_trigger_id="BEMOSSOffline", event_trigger_class="desc_prio")
# et4.save()
#
# et5 = EventTrigger(id=5, device_type_id=9, event_trigger_desc="Any BEMOSS Device Offline", event_trigger_id="BEMOSSDeviceOffline", event_trigger_class="desc_prio")
# et5.save()
#
# et6 = EventTrigger(id=6, device_type_id=9, event_trigger_desc="System Failure", event_trigger_id="SystemFailure", event_trigger_class="desc_prio")
# et6.save()

app = ApplicationRegistered(application_id=1,app_name='plugload_scheduler',description="Plugload schulding app",registered_time=datetime.datetime.now(),
                            app_agent='plugloadSchedulerAgent')
app.save()
app = ApplicationRegistered(application_id=2,app_name='lighting_scheduler',description="Lighting schulding app",registered_time=datetime.datetime.now(),
                            app_agent='lightingSchedulerAgent')
app.save()

app = ApplicationRegistered(application_id=3,app_name='iblc',description="Illuminance based lighting controller app",registered_time=datetime.datetime.now(),
                            app_agent='illuminanceBasedLightingControl')
app.save()


app = ApplicationRegistered(application_id=4,app_name='fault_detection',description="Thermostat Fault Detection",registered_time=datetime.datetime.now(),
                            app_agent='faultDetection')
app.save()

app = ApplicationRegistered(application_id=5,app_name='thermostat_control',description="Thermostat Control based on external sensor",registered_time=datetime.datetime.now(),
                            app_agent='thermostatControlAgent')
app.save()

app = ApplicationRegistered(application_id=6,app_name='dr_test',description="Demand response testing",registered_time=datetime.datetime.now(),
                            app_agent='demandResponse')
app.save()


#Miscellaneous table update with auto_discovery
auto_disc = Miscellaneous(id=1, key='auto_discovery', value='OFF')
auto_disc.save()
# Set default zipcode
zipcode = Miscellaneous(id=2, key='zipcode', value='22203')
zipcode.save()

#Default Node 0
node = NodeInfo(node_id=0, node_name='main',node_type='core', node_status='ONLINE' )
node.save()



