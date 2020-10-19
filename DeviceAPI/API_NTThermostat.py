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

#__author__ = "Rajendra Adhikari"
#__credits__ = ""
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__lastUpdated__ = "2017-7-27 11:55:33"
'''

'''This API class is for an agent that want to discover/communicate/monitor/control
devices that compatible with ICM Thermostat Wi-Fi '''
import os
import time
import sys
import urllib2
import json
import datetime
from urlparse import urlparse
import settings
from bemoss_lib.utils.find_own_ip import getIPs


from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import socket
from DeviceAPI.BaseAPI_Thermostat import BaseAPI_Thermsostat

debug = True

class API(BaseAPI_Thermsostat):

    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)
        self.device_supports_auto = False
        self._debug = True
        self.Nicknames = ['WAKE','LEAVE','RETURN','SLEEP']
        self.cookie_path = os.path.expanduser(settings.PROJECT_DIR + '/.temp/.ICMcookie.txt')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)  # 3 second timeout on commands

        if 'username' in kwargs.keys():
            self.username = kwargs['username']
            self.password = kwargs['password']
            self.address = kwargs['address']
            self.account_login(self.username, self.password,self.address)

    def API_info(self):
        return [{'device_model': 'NTThermostat', 'vendor_name': 'NT', 'communication': 'WiFi', 'support_oauth': False,
                'device_type_id': 1,'api_name': 'API_NTThermostat','html_template':'thermostat/thermostat.html',
                'agent_type':'ThermostatAgent','identifiable': False, 'authorizable': False, 'is_cloud_device': True,
                'schedule_weekday_period': 4,'schedule_weekend_period': 4, 'allow_schedule_period_delete': True, 'chart_template': 'charts/charts_thermostat.html'},
                ]

    def dashboard_view(self):
        if self.get_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": None, "image":"Thermostat.png"}
        else:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": BEMOSS_ONTOLOGY.SETPOINT.NAME, "image":"Thermostat.png"}

    def ontology(self):
        return {"thermostat_mode":BEMOSS_ONTOLOGY.THERMOSTAT_MODE,"thermostat_state":BEMOSS_ONTOLOGY.THERMOSTAT_STATE,
                "fan_mode":BEMOSS_ONTOLOGY.FAN_MODE,"fan_state":BEMOSS_ONTOLOGY.FAN_STATE,
                "cool_setpoint":BEMOSS_ONTOLOGY.COOL_SETPOINT,"heat_setpoint":BEMOSS_ONTOLOGY.HEAT_SETPOINT,
                "indoor_temperature":BEMOSS_ONTOLOGY.TEMPERATURE,"hold":BEMOSS_ONTOLOGY.HOLD,
                "setpoint":BEMOSS_ONTOLOGY.SETPOINT,"anti-tampering":BEMOSS_ONTOLOGY.ANTI_TAMPERING}

    def renewConnection(self):
        discovered_devices= self.discover(self.username,self.password)
        new_address = None
        for device in discovered_devices:
            macaddress = device['mac']
            if macaddress == self.config['mac_address']:
                new_address = device['address']
                break
        if new_address != None:
            self.set_variable('address',new_address)
            self.account_login(self.username,self.password,self.address)

    tmode_dict = {'OFF':BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF,
                  'COOL':BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL,
                  'HEAT':BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT,
                  'AUTO':BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.AUTO}
    fmode_dict = {'FAN AUTO':BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.AUTO,
                  'FAN ON':BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.ON,
                  'FAN RECIRC':BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.CIRCULATE}
    hold_dict  =  {'NO':BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE,
                  'YES':BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY}

    # GET Open the URL and read the data
    def getDataFromDevice(self):
        
        try:
            self.account_login(self.username, self.password,self.address)
            self.sock.sendall(b'RAS1\r')
            reply = self.sock.recv(4096).strip()
        except socket.error:
            raise
        command, output = reply.split(':')
        states = output.split(',')
        result = dict()
        result['indoor_temperature'] = states[0]
        result['thermostat_mode'] = self.tmode_dict.get(states[2],None)
        result['fan_mode'] = self.fmode_dict.get(states[3],None)
        result['hold'] = self.hold_dict.get(states[4],None)
        result['cool_setpoint'] = states[6]
        result['heat_setpoint'] = states[7]
        result['thermostat_state'] = self.tmode_dict.get(states[8],None)
        result['setpoint'] = None #default non setpoint
        if result['thermostat_mode'] == 'COOL':
            result['setpoint'] = result['cool_setpoint']
        elif result['thermostat_mode'] == 'HEAT':
            result['setpoint'] = result['heat_setpoint']
        elif result['thermostat_mode'] == 'AUTO':
            if result['thermostat_state'] == 'COOL':
                result['setpoint'] = result['cool_setpoint']
            elif result['thermostat_state'] == 'HEAT':
                result['setpoint'] = result['heat_setpoint']

        result['fan_state'] = result['fan_mode'] #thermostat doesn't have fan state
        return result

    def getDeviceSchedule(self):
        scheduleData = dict()
        days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        scheduleData['Enabled'] = True #Always make it true. (Legacy purpose.)
        schedule = self.get_variable('scheduleList')
        for day in days:
            scheduleData[day]=list()
            for i in range(1,5):
                command = b'R'+str(i)+day[:2].upper()+'1\r'
                self.sock.sendall(command)
                output = self.sock.recv(4096)[7:].strip() #disard the initial command
                outputs = output.split(',')
                time = outputs[4]
                hours, min = time.split(':')
                minutes = int(hours)*60
                minutes += int(min[:2])
                minutes += 12*60 if min[:-1] == 'P' and hours != '12' else 0
                cool_setpoint = outputs[5]
                heat_setpoint = outputs[6]
                scheduleData[day].append([self.Nicknames[i-1],str(minutes),str(cool_setpoint),str(heat_setpoint)])
        self.set_variable('scheduleData',scheduleData)
        return self.get_variable('scheduleData')



    def setDeviceData(self, postmsg):
        is_success = True
        def send_message(message):
            self.sock.sendall(message)
            reply = self.sock.recv(4096).strip().split(':')
            if reply[0] != message.strip():
                is_success = False

        if BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME in postmsg:
            value = postmsg[BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME]
            send_val = self.dict_rev_translate(self.tmode_dict,value)
            message = b'WMS1D'+send_val[0]+'\r' #only one letter used. HEAT = H, COOL = C, AUTO = A, OFF = O
            send_message(message)

        if BEMOSS_ONTOLOGY.FAN_MODE.NAME in postmsg:
            value = postmsg[BEMOSS_ONTOLOGY.FAN_MODE.NAME]
            send_val = self.dict_rev_translate(self.fmode_dict,value)
            letter = 'O' if send_val == 'FAN ON' else 'A' #auto or ON
            message = b'WFM1D'+letter+'\r' #FAN AUTO = A,
            send_message(message)

        if BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME in postmsg:
            value = postmsg[BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME]
            send_val = str(int(value))
            message = b'WOC1D'+send_val+'\r'
            send_message(message)

        if BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME in postmsg:
            value = postmsg[BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME]
            send_val = str(int(value))
            message = b'WOH1D' + send_val + '\r'
            send_message(message)

        if BEMOSS_ONTOLOGY.HOLD.NAME in postmsg:
            value = postmsg[BEMOSS_ONTOLOGY.HOLD.NAME]
            if value == BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE: #release hold
                message = b'WOR1D0:00\r'
                send_message(message)
            if value == BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY: #default temporary hold to 2 hours
                message = b'WOR1D2:00\r'
                send_message(message)
            #ignore permanent hold
        return is_success

    def setDeviceSchedule(self,scheduleData):
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        schedule = self.get_variable('scheduleList')
        success = True
        for day in days:
            days_schedule = scheduleData[day]
            for i in range(1, 5):
                current_schedule = days_schedule[i-1]
                minutes = current_schedule[1]
                hour = int(minutes/60)
                minute = minutes % 60
                am_pm = 'A'
                if hour >= 13:
                    hour -= 12
                    am_pm = 'P'
                time = str(hour)+':'+str(minute)+am_pm

                cool_setpoint = current_schedule[2]
                heat_setpoint = current_schedule[3]
                command = b'W' + str(i) + day[:2].upper() + '1D'
                message = b'X,X,X,A,'+time+','+str(int(cool_setpoint))+','+str(int(heat_setpoint))+'\r'
                self.sock.sendall(command+message)
                reply = self.sock.recv(4096)
                if reply[:6] != command:
                    success = False
        return True

    def getList(self, inputSchedule):

        schedule = list()
        days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        for day in days:
            sch = [[int(x[1])/60,int(x[1])%60,int(x[2]),int(x[3])] for x in inputSchedule[day]]
            if len(sch) < 4: #if not four entry for the day, append dummy entries
                for i in range(0,4-len(sch)):
                    temp = sch[:-1]
                    temp[0] = 23
                    temp[1] = 55+i
                    sch.append(temp)
            schedule += sch

        schedule = sum(schedule,[]) #join the list
        return schedule

    def getScheduleSetpoint(self, testDate):
        if self.get_variable('scheduleData') is None:
            self.getDeviceSchedule()
        schData = self.get_variable('scheduleData')
        daysofweek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        todayDay = daysofweek[testDate.weekday()]
        if todayDay != 'monday':
            yesterdayDay = daysofweek[testDate.weekday() - 1]
        else:
            yesterdayDay = 'sunday'

        TodaysSchedule = schData[todayDay]
        YesterdaysSchedule = schData[yesterdayDay]
        setPoints = YesterdaysSchedule[-1][2:]  # yesterday's last setpoint
        nowminute = testDate.hour * 60 + testDate.minute
        for entries in TodaysSchedule:
            if int(entries[1]) <= nowminute:
                setPoints = [int(entries[2]), int(entries[3])]
            else:
                break
        return setPoints

    def account_login(self,username,password,address):
        try:
            self.sock.close()
        except:
            pass
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(3)  # 3 second timeout on commands
        address,port = address.split(':')
        port = int(port)
        self.sock.connect((address, port))
        login_message = b'WML1D'+username+','+password+'\r'
        self.sock.sendall(login_message)
        reply = self.sock.recv(4096).strip()
        is_ok = reply.split(',')[0] == "OK"
        return is_ok

    def discover(self,username, password, token=None):
        myIps = getIPs()
        device_list = []

        for ip in myIps:
            for i in range(1,256):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.05)  # 0.01 second timeout on commands
                parts = ip.split('.')
                new_ip = '.'.join(parts[:3]+[str(i)])
                port = 10001
                try:
                    sock.connect((new_ip,port))
                except socket.error as er:
                    continue
                sock.settimeout(3)
                login_message = b'WML1D'+username+','+password+'\r'
                sock.sendall(login_message)
                reply = sock.recv(4096).strip()
                is_ok = reply.split(',')[0] == "OK"
                if is_ok:
                    mac_message = b'RMMI1\r'
                    sock.sendall(mac_message)
                    mac = sock.recv(4096)[6:].strip().replace(':','')
                    name_message = b'RMTN1\r'
                    sock.sendall(name_message)
                    name = sock.recv(4096)[6:].strip()
                    model_message = b'REV1\r'
                    sock.sendall(model_message)
                    model = sock.recv(4096)[5:].strip().split(',')[0]
                    device_list.append({'address': new_ip+':'+str(port) , 'mac': mac,
                                    'model': self.API_info()[0]['device_model'], 'vendor': self.API_info()[0]['vendor_name'],
                                    'nickname': name})

            #print device_list
            return device_list


# This main method will not be executed when this class is used as a module
def main():
    pass

    #print result

if __name__ == "__main__": main()
