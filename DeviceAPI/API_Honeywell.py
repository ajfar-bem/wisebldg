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

#__author__ = "Imran Rahman"
#__credits__ = ""
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2016-10-31 12:30:00"
#__lastUpdated__ = "2016-11-02 01:34:50"
'''

'''This API class is for an agent that wants to discover/communicate/monitor/control
devices that compatible with Honeywell Thermostat Wi-Fi '''

import urllib
import json
import datetime
import re
import time
import httplib
import os
import sys
import psycopg2

from urlparse import urlparse
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import settings
from DeviceAPI.BaseAPI_Thermostat import BaseAPI_Thermsostat

class API(BaseAPI_Thermsostat):

    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.device_supports_auto = False
        self.set_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF)
        self.AUTH="https://mytotalconnectcomfort.com/portal"
        self.cookiere=re.compile('\s*([^=]+)\s*=\s*([^;]*)\s*')
        if 'username' in kwargs.keys():
            self.username = kwargs['username']
            self.password = kwargs['password']
        self._debug = False

    def API_info(self):
        return [{'device_model': 'RTH8580WF', 'vendor_name': 'Honeywell', 'communication': 'WiFi', 'support_oauth' : False,
                 'device_type_id': 1, 'api_name': 'API_Honeywell', 'html_template': 'thermostat/thermostat.html',
                 'agent_type': 'ThermostatAgent', 'identifiable': True, 'authorizable': False, 'is_cloud_device': True,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': False,
                 'chart_template': 'charts/charts_thermostat.html',"built_in_schedule_support": True},]


    def dashboard_view(self):
        if self.get_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": None, "image":"Thermostat.png"}
        else:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": BEMOSS_ONTOLOGY.SETPOINT.NAME, "image":"Thermostat.png"}


    def ontology(self):
        return {"tmode": BEMOSS_ONTOLOGY.THERMOSTAT_MODE, "tstate": BEMOSS_ONTOLOGY.THERMOSTAT_STATE,
                "fmode": BEMOSS_ONTOLOGY.FAN_MODE, "fstate": BEMOSS_ONTOLOGY.FAN_STATE,
                "t_cool": BEMOSS_ONTOLOGY.COOL_SETPOINT, "t_heat": BEMOSS_ONTOLOGY.HEAT_SETPOINT,
                "temp": BEMOSS_ONTOLOGY.TEMPERATURE, "hold": BEMOSS_ONTOLOGY.HOLD,
                "setpoint": BEMOSS_ONTOLOGY.SETPOINT, "theatstat":BEMOSS_ONTOLOGY.THERMOSTAT_HEATSTATUS,
                "tcoolstat":BEMOSS_ONTOLOGY.THERMOSTAT_COOLSTATUS, "anti-tampering":BEMOSS_ONTOLOGY.ANTI_TAMPERING}

    def discover(self, username, password, token=None):

        self.username = username
        self.password = password
        thermostat_deviceids = list()

        cookie = self.get_login()

        if cookie == 0:
            return thermostat_deviceids

        headers = {
            "Accept": "*/*",
            "DNT": "1",
            # "Accept-Encoding":"gzip,deflate,sdch",
            "Accept-Encoding": "plain",
            "Cache-Control": "max-age=0",
            "Accept-Language": "en-US,en,q=0.8",
            # "Connection":"keep-alive",
            "Host": "mytotalconnectcomfort.com",
            "Referer": self.AUTH,
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
            "Cookie": cookie
        }
        conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=10)
        conn.request("GET", "/portal/", None, headers)
        r2 = conn.getresponse()

        if (r2.status != 200):
            print("Error Didn't get 200 status on R2 status={0} {1}".format(r2.status, r2.reason))
            self.logout(cookie)
            return thermostat_deviceids

        redirectlocation = r2.read()
        j = json.loads(redirectlocation)

        if "/portal/Device/Control/" in j["Redirect"]:
            deviceid = str(j["Redirect"]).replace('/portal/Device/Control/', '').replace('?page=1', '')
            # print deviceid
            thermostat_deviceids.append(deviceid)
            self.logout(cookie)

        elif "/portal/Locations" in j["Redirect"]:
            print "No device in Honeywell account"
            self.logout(cookie)

        else:
            location = j["Redirect"]

            # location="/portal/945557/Zones"
            # print "THIRD"
            headers = {
                "Accept": "*/*",
                "DNT": "1",
                # "Accept-Encoding":"gzip,deflate,sdch",
                "Accept-Encoding": "plain",
                "Cache-Control": "max-age=0",
                "Accept-Language": "en-US,en,q=0.8",
                "Connection": "keep-alive",
                "Host": "mytotalconnectcomfort.com",
                "Referer": self.AUTH,
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
                "Cookie": cookie
            }
            conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=10)
            # conn.set_debuglevel(999);
            # print "LOCATION R3 is",location
            conn.request("GET", location, None, headers)
            r2 = conn.getresponse()
            if (r2.status != 200):
                print("Error Didn't get 200 status on R2 status={0} {1}".format(r2.status, r2.reason))
                self.logout(cookie)
                return thermostat_deviceids

            rawdata = r2.read()

            with open('honeywell.txt', 'wt') as outfile:
                outfile.write(rawdata)

            with open('honeywell.txt', 'r') as infile:
                for line in infile:
                    # print line
                    if 'data-url="/portal/Device/Control/' in line:
                        if "red-capsule" not in line:
                            line = line.strip()
                            deviceid = line.split('data-url="/portal/Device/Control/')[1].replace(
                                '?page=1" data-clickenabled="True">', '')
                            # print deviceid
                            thermostat_deviceids.append(deviceid)

            os.remove("honeywell.txt")

        device_list = list()
        for device in thermostat_deviceids:
            nickname = self.getDeviceNickname(cookie,device)
            device_list.append({'address': device, 'mac': device,
                                'model': 'RTH8580WF', 'vendor': 'Honeywell',
                                'nickname': nickname})

        self.logout(cookie)

        return device_list

    tmode_dict = {1: BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT,
                  2: BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF,
                  3: BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL,
                  4: BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.AUTO}
    fmode_dict = {0: BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.AUTO,
                  1: BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.ON}
    hold_dict = {0: BEMOSS_ONTOLOGY.THERMOSTAT_COOLSTATUS.POSSIBLE_VALUES.NONE,
                 1: BEMOSS_ONTOLOGY.THERMOSTAT_COOLSTATUS.POSSIBLE_VALUES.TEMPORARY,
                 2: BEMOSS_ONTOLOGY.THERMOSTAT_COOLSTATUS.POSSIBLE_VALUES.PERMANENT}

    def client_cookies(self, cookiestr, container):
        if not container: container = {}
        toks = re.split(';|,', cookiestr)
        for t in toks:
            k = None
            v = None
            m = self.cookiere.search(t)
            if m:
                k = m.group(1)
                v = m.group(2)
                if (k in ['path', 'Path', 'HttpOnly']):
                    k = None
                    v = None
            if k:
                # print k,v
                container[k] = v
        return container

    def export_cookiejar(self, jar):
        s = ""
        for x in jar:
            s += '%s=%s;' % (x, jar[x])
        return s

    def get_login(self, relogin=False):
        self.cookie_path = os.path.expanduser(settings.PROJECT_DIR + '/.temp/.HWTHcookie') + self.username
        # if not relogin:
        #     try:
        #         with open(self.cookie_path, 'r') as cokiefile:
        #             cookie = cokiefile.read()
        #             return cookie
        #     except IOError as er:
        #         if er[0] == 2:  # No such file or directory
        #             pass

        cookiejar = None
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Encoding": "sdch",
                   "Host": "mytotalconnectcomfort.com",
                   "DNT": "1",
                   "Origin": self.AUTH,
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36"
                   }
        conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=20)
        conn.request("GET", "/portal/", None, headers)
        r0 = conn.getresponse()
        # print r0.status, r0.reason

        for x in r0.getheaders():
            (n, v) = x
            # print "R0 HEADER",n,v
            if (n.lower() == "set-cookie"):
                cookiejar = self.client_cookies(v, cookiejar)
        # cookiejar = r0.getheader("Set-Cookie")
        location = r0.getheader("Location")

        retries = 5
        params = urllib.urlencode({"timeOffset": "240",
                                   "UserName": self.username,
                                   "Password": self.password,
                                   "RememberMe": "false"})
        # print params
        newcookie = self.export_cookiejar(cookiejar)
        # print "Cookiejar now",newcookie
        headers = {"Content-Type": "application/x-www-form-urlencoded",
                   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Accept-Encoding": "sdch",
                   "Host": "mytotalconnectcomfort.com",
                   "DNT": "1",
                   "Origin": self.AUTH,
                   "Cookie": newcookie,
                   "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36"
                   }
        conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=20)
        conn.request("POST", "/portal/", params, headers)
        r1 = conn.getresponse()
        # print r1.status, r1.reason

        for x in r1.getheaders():
            (n, v) = x
            # print "GOT2 HEADER",n,v
            if (n.lower() == "set-cookie"):
                cookiejar = self.client_cookies(v, cookiejar)
        cookie = self.export_cookiejar(cookiejar)
        # cookie=re.sub(";\s*expires=[^;]+","",cookie)
        # print "Cookiejar now",cookie
        location = r1.getheader("Location")

        if ((location == None) or (r1.status != 302)):
            # raise BaseException("Login fail" )
            print("classAPI_HoneywellThermostat: ERROR: Got redirect on initial login  status={0} {1}".format(r1.status,
                                                                                                              r1.reason))
            return 0

        try:
            with open(self.cookie_path, 'w') as cokiefile:
                cokiefile.write(cookie)
                cokiefile.truncate()
        except IOError as er:
            print er

        if not cookie:
            raise Exception("Login failed")
        return cookie

    def logout(self, cookie):
        headers = {
            "Accept": "*/*",
            "DNT": "1",
            # "Accept-Encoding":"gzip,deflate,sdch",
            "Accept-Encoding": "plain",
            "Cache-Control": "max-age=0",
            "Accept-Language": "en-US,en,q=0.8",
            "Host": "mytotalconnectcomfort.com",
            "Referer": self.AUTH,
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
            "Cookie": cookie
        }
        conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=20)
        # conn.set_debuglevel(999);
        # print "LOCATION R3 is",location
        conn.request("GET", '/portal/Account/LogOff', None, headers)
        r3 = conn.getresponse()
        if (r3.status != 200):
            print("classAPI_HoneywellThermostat: ERROR: at logout on status={0} {1}".format(r3.status, r3.reason))
            return

    # method1: GET Open the URL and read the data
    def getDeviceNickname(self,cookie, address):
        # print cookie
        code = str(address)

        location = "/portal/Device/Control/" + code

        headers = {
            "Accept": "*/*",
            "DNT": "1",
            # "Accept-Encoding":"gzip,deflate,sdch",
            "Accept-Encoding": "plain",
            "Cache-Control": "max-age=0",
            "Accept-Language": "en-US,en,q=0.8",
            # "Connection":"keep-alive",
            "Host": "mytotalconnectcomfort.com",
            "Referer": self.AUTH,
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
            "Cookie": cookie
        }
        conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=20)
        # conn.set_debuglevel(999);
        # print "LOCATION R3 is",location
        conn.request("GET", location, None, headers)
        r3 = conn.getresponse()
        if (r3.status != 200):
            print("classAPI_HoneywellThermostat: ERROR: getdevicestatus couldn't get data on status={0} {1}".format(
                r3.status, r3.reason))
            # self.logout(cookie)
            return

        rawdata = r3.read()

        with open('honeywell2.txt', 'wt') as outfile:
            outfile.write(rawdata)

        with open('honeywell2.txt', 'r') as infile:
            for line in infile:
                # print line
                if '<h1 id="ZoneName">' in line:
                    line = line.strip()
                    devicenickname = line.split('<h1 id="ZoneName">')[1].replace(' Control</h1>', '')
                    # print devicenickname
                    break

        os.remove("honeywell2.txt")
        # self.logout(cookie)
        return devicenickname

    def getDataFromDevice(self):
        cookie = self.get_login()
            # print cookie
        code = str(self.config['address'])

        t = datetime.datetime.now()
        utc_seconds = (time.mktime(t.timetuple()))
        utc_seconds = int(utc_seconds * 1000)
        location = "/portal/Device/CheckDataSession/" + code + "?_=" + str(utc_seconds)

        headers = {
            "Accept": "*/*",
            "DNT": "1",
            # "Accept-Encoding":"gzip,deflate,sdch",
            "Accept-Encoding": "plain",
            "Cache-Control": "max-age=0",
            "Accept-Language": "en-US,en,q=0.8",
            # "Connection":"keep-alive",
            "Host": "mytotalconnectcomfort.com",
            "Referer": self.AUTH,
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
            "Cookie": cookie
        }
        conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=20)
        # conn.set_debuglevel(999);
        # print "LOCATION R3 is",location
        conn.request("GET", location, None, headers)
        r3 = conn.getresponse()
        if (r3.status != 200):

            self.logout(cookie)
            self.get_login(relogin=True)  # This will regenerate the cookie-file, so should be fine next time
            raise Exception(
                "classAPI_HoneywellThermostat: ERROR: getdevicestatus couldn't get data on status={0} {1}".format(
                    r3.status, r3.reason))
        else:
            rawdata = r3.read()
            _response = json.loads(rawdata)
            if _response['deviceLive'] == False:
                print 'Cloud reports this honeywell device as offline'
                return None
            else:
                devicedata = self.getDeviceStatusJson(_response)
                scheduleData = self.getDeviceSchedule(cookie)
                devicedata['scheduleData'] = scheduleData
                self.variables.update(devicedata)
                return devicedata



    def getDeviceStatusJson(self, _data):
        # Use the json module to load the string data into a dictionary
        # 1. temperature
        devicedata ={"temp": _data['latestData']['uiData']["DispTemperature"]}
        # 2. thermostat_mode
        if _data['latestData']['uiData']["SystemSwitchPosition"] in [1, 2, 3, 4]:
            thermostat_mode = self.tmode_dict[_data['latestData']['uiData']["SystemSwitchPosition"]]
        else:
            raise Exception("Invalid value for device thermostat_mode")

        devicedata["tmode"] = thermostat_mode
        # 3. Set point
        devicedata["t_heat"]= _data['latestData']['uiData']["HeatSetpoint"]
        devicedata["t_cool"]= _data['latestData']['uiData']["CoolSetpoint"]

        if thermostat_mode == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL:
            devicedata['setpoint'] = devicedata["t_cool"]
        elif thermostat_mode == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT:
            devicedata['setpoint'] = devicedata["t_heat"]
        else:
            devicedata['setpoint'] = None
        # 4. fan_mode
        devicedata["fmode"] = self.fmode_dict[_data['latestData']['fanData']["fanMode"]]
        # 5. thermostat_state
        devicedata["tstate"] = thermostat_mode
        # 6. fan_state
        devicedata["fstate"] = devicedata["fmode"]
        # 7. Additional Required Data
        devicedata["tcoolstat"]= self.hold_dict[_data['latestData']['uiData']["StatusCool"]]
        devicedata["theatstat"]= self.hold_dict[_data['latestData']['uiData']["StatusHeat"]]
        devicedata["hold"] = devicedata["tcoolstat"]

        return devicedata

    def setDeviceStatus(self, postmsg):
        is_success = True
        # Ex. postmsg = {"thermostat_mode":"HEAT","heat_setpoint":85})
        # step1: parse postmsg
        # step2: send message to change status of the device

        cookie = self.get_login()
        if 'scheduleData' in postmsg:
            scheduleData = postmsg.pop('scheduleData')
            self.setDeviceSchedule(cookie,scheduleData)

        if not postmsg:
            return #if there is nothing left return, otherwise procced with the rest
        # print cookie
        code = str(self.config['address'])
        headers = {
            "Accept": 'application/json; q=0.01',
            "DNT": "1",
            "Accept-Encoding": "gzip,deflate,sdch",
            'Content-Type': 'application/json; charset=UTF-8',
            "Cache-Control": "max-age=0",
            "Accept-Language": "en-US,en,q=0.8",
            # "Connection":"keep-alive",
            "Host": "mytotalconnectcomfort.com",
            "Referer": "https://mytotalconnectcomfort.com/portal/",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
            'Referer': "/TotalConnectComfort/Device/CheckDataSession/" + code,
            "Cookie": cookie
        }

        payload = self.convertPostMsg(postmsg)

        location = "/portal/Device/SubmitControlScreenChanges"

        rawj = json.dumps(payload)

        conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=20)
        # conn.set_debuglevel(999);
        # print "R4 will send"
        # print rawj
        conn.request("POST", location, rawj, headers)
        r4 = conn.getresponse()
        if (r4.status != 200):
            raise Exception(
            "classAPI_HoneywellThermostat: ERROR: setdevicestatus couldn't set status on R4 status={0} {1}".format(
                r4.status, r4.reason))




    def isPostmsgValid(self, postmsg):  # check validity of postmsg
        return True #supress data validitiy test. If it going to fail, it will fail; but we can take chance
        dataValidity = True
        for k, v in postmsg.items():
            if k == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME:
                if postmsg.get(
                        BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT:
                    for k, v in postmsg.items():
                        if k == BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME:
                            dataValidity = False
                            break
                elif postmsg.get(
                        BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL:
                    for k, v in postmsg.items():
                        if k == BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME:
                            dataValidity = False
                            break
        return dataValidity

    def convertPostMsg(self, postmsg):
        payload = {"CoolNextPeriod": None, "CoolSetpoint": None, "DeviceID": int(self.config['address']),
                   "FanMode": None, "HeatNextPeriod": None, "HeatSetpoint": None, "SystemSwitch": None}
        payload["StatusCool"] = self.dict_rev_translate(self.hold_dict, postmsg.get('hold'))
        payload["StatusHeat"] = self.dict_rev_translate(self.hold_dict, postmsg.get('hold'))

        if BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME in postmsg:
            payload["SystemSwitch"] = self.dict_rev_translate(self.tmode_dict, postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME))

        if BEMOSS_ONTOLOGY.FAN_MODE.NAME in postmsg:
            payload["FanMode"] = self.dict_rev_translate(self.fmode_dict,postmsg.get(BEMOSS_ONTOLOGY.FAN_MODE.NAME))

        if BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME in postmsg:
            payload["HeatSetpoint"] = int(postmsg.get(BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME))

        if BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME in postmsg:
            payload["CoolSetpoint"] = int(postmsg.get(BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME))

        return payload

    def getRawSchedule(self,cookie):

        code = str(self.config['address'])

        # location="/portal/Device/CheckDataSession/"+code+"?_="+str(utc_seconds)
        # location="/portal/Device/Menu/"+code
        location = "/portal/Device/Menu/GetScheduleData/" + code
        # location="/portal/Device/Menu/SendSchedule?deviceId="+code

        headers = {
            "Accept": "*/*",
            "DNT": "1",
            # "Accept-Encoding":"gzip,deflate,sdch",
            "Accept-Encoding": "plain",
            "Cache-Control": "max-age=0",
            "Accept-Language": "en-US,en,q=0.8",
            # "Connection":"keep-alive",
            "Host": "mytotalconnectcomfort.com",
            "Referer": "https://mytotalconnectcomfort.com/portal/Device/Menu/" + code,
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
            "Cookie": cookie
        }
        conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=20)
        # conn.set_debuglevel(999);
        # print "LOCATION R3 is",location
        # conn.request("GET", location,None,headers)
        conn.request("POST", location, {}, headers)
        r3 = conn.getresponse()
        if (r3.status != 200):
            raise Exception(
            "classAPI_HoneywellThermostat: ERROR: getdeviceschedule couldn't get schedule on status={0} {1}".format(
                r3.status, r3.reason))

        else:
            rawdata = r3.read()
            # print rawdata
            _response = json.loads(rawdata)

        return _response

    def getDeviceSchedule(self, cookie):
            _response = self.getRawSchedule(cookie)
            # print _response
            daysofweek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            scheduleData = {'Enabled': True, 'monday': list(), 'tuesday': list(),
                                              'wednesday': list(), 'thursday': list(), 'friday': list(),
                                              'saturday': list(), 'sunday': list()}
            for perioddata in _response['Schedule']['SchedulePeriods']:
                if perioddata['IsCancelled'] == False:
                    scheduleData[daysofweek[perioddata['Day']]].append(
                        [_response['PeriodHeaders'][perioddata['PeriodType']]['Label'],
                         perioddata['StartTime']['TotalMinutes'], perioddata['CoolSetpoint'],
                         perioddata['HeatSetpoint']])

            return scheduleData

    def cleanSchedulePostms(self,schedulepostmsg):
        #the four periods must be named, Wake, Leave, Return and Sleep
        periods = ['Wake','Leave','Return','Sleep']
        days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        for day, dailySchedule in schedulepostmsg.items():
            if day not in days:
                schedulepostmsg.pop(day)
                continue
            for id,entry in enumerate(dailySchedule):
                entry[0] = periods[id]

    def setDeviceSchedule(self,cookie, schedulepostmsg):

        code = str(self.config['address'])
        self.cleanSchedulePostms(schedulepostmsg)
        # Get Previous Schedule from Device
        previousschedule = self.getRawSchedule(cookie)
        scheduleData = self.getDeviceSchedule(cookie)

        # Make changes to the schedule
        headers = {
            "Accept": "*/*",
            # "Accept":'application/json; q=0.01',
            "DNT": "1",
            # "Accept-Encoding":"gzip,deflate,sdch",
            "Accept-Encoding": "plain",
            'Content-Type': 'application/json; charset=UTF-8',
            "Cache-Control": "max-age=0",
            "Accept-Language": "en-US,en,q=0.8",
            # "Connection":"keep-alive",
            "Host": "mytotalconnectcomfort.com",
            "Referer": "https://mytotalconnectcomfort.com/portal/Device/Menu/" + code,
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
            "Cookie": cookie
        }

        daysofweek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        periodnicknames = [previousschedule['PeriodHeaders'][i]['Label'] for i in range(0, 4)]

        changeflag = False
        for day in daysofweek:
            for periodnickname in periodnicknames:
                old_period = None
                for perioddata in scheduleData[day]:
                    if perioddata[0] == periodnickname:
                        old_period = perioddata
                        break
                new_period = None
                for perioddata in schedulepostmsg[day]:
                    if perioddata[0] == periodnickname:
                        new_period = perioddata
                        break

                if old_period != new_period:
                    cancelperiod = None
                    if old_period == None:
                        cancelperiod = False
                    elif new_period == None:
                        cancelperiod = True

                    dayindex = daysofweek.index(day)
                    periodindex = periodnicknames.index(periodnickname)

                    for previousperiod in previousschedule['Schedule']['SchedulePeriods']:
                        if previousperiod['Day'] == dayindex and previousperiod['PeriodType'] == periodindex:
                            previousperiodfulldata = previousperiod
                            break

                    payload = self.convertSchedulePostMsg(new_period, previousperiodfulldata, cancelperiod)

                    location = "/portal/Device/Menu/EditScheduledPeriod/" + code

                    rawj = json.dumps(payload)

                    #print rawj

                    conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=20)
                    # conn.set_debuglevel(999);
                    # print "R4 will send"
                    # print rawj
                    conn.request("POST", location, rawj, headers)
                    # conn.request("POST", location,{},headers)
                    r4 = conn.getresponse()
                    if (r4.status != 200):
                        print (
                        "classAPI_HoneywellThermostat: ERROR: setdeviceschedule couldn't edit schedule on status={0} {1}".format(
                            r4.status, r4.reason))
        changeflag = True
        # need to submit send_sechule as well, otherwise it will remain pending

        if changeflag == True:

            headers = {
                "Accept": "*/*",
                # "Accept":'application/json; q=0.01',
                "DNT": "1",
                # "Accept-Encoding":"gzip,deflate,sdch",
                "Accept-Encoding": "plain",
                "Cache-Control": "max-age=0",
                "Accept-Language": "en-US,en,q=0.8",
                # "Connection":"keep-alive",
                "Host": "mytotalconnectcomfort.com",
                "Referer": "https://mytotalconnectcomfort.com/portal/Device/Menu/" + code,
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
                "Cookie": cookie
            }
            location = "/portal/Device/Menu/SendSchedule?deviceId=" + code
            conn = httplib.HTTPSConnection("mytotalconnectcomfort.com", timeout=20)
            conn.request("POST", location, {}, headers)
            r4 = conn.getresponse()
            if (r4.status != 200):
                raise Exception(
                "classAPI_HoneywellThermostat: ERROR: setdeviceschedule couldn't submit schedule on status={0} {1}".format(
                    r4.status, r4.reason))

    def convertSchedulePostMsg(self, newschedule, previousschedule, cancelperiod):
        if cancelperiod == None:
            IsCancelled = previousschedule['IsCancelled']
            HeatSetpoint = newschedule[3]
            CoolSetpoint = newschedule[2]
            StartTime = self.convertTotalMinutestoTimeformat(newschedule[1])
        elif cancelperiod == True:
            IsCancelled = cancelperiod
            HeatSetpoint = previousschedule['HeatSetpoint']
            CoolSetpoint = previousschedule['CoolSetpoint']
            StartTime = self.convertTotalMinutestoTimeformat(previousschedule['StartTime']['TotalMinutes'])
        else:
            IsCancelled = cancelperiod
            HeatSetpoint = newschedule[3]
            CoolSetpoint = newschedule[2]
            StartTime = self.convertTotalMinutestoTimeformat(newschedule[1])

        payload = {
            "PeriodTemplate.StartTime": StartTime,
            "PeriodTemplate.OrigStartTime": self.convertTotalMinutestoTimeformat(
                previousschedule['StartTime']['TotalMinutes']),
            "PeriodTemplate.HeatSetpoint": HeatSetpoint,
            "PeriodTemplate.OrigHeatSetpoint": previousschedule['HeatSetpoint'],
            "PeriodTemplate.CoolSetpoint": CoolSetpoint,
            "PeriodTemplate.OrigCoolSetpoint": previousschedule['CoolSetpoint'],
            "PeriodTemplate.IsCancelled": IsCancelled,
            "PeriodTemplate.OrigIsCancelled": previousschedule['IsCancelled'],
            "IsCommercial": False,
            "PeriodType": previousschedule['PeriodType'],
            "Deadband": 0.0000,
            "SwitchAutoAllowed": False,
            "DisplayUnits": "Fahrenheit",
            "DeviceID": int(self.config['address']),
            "DayOfWeek": previousschedule['Day']
        }

        return payload

    def convertTotalMinutestoTimeformat(self,Totalminutes):
        hours = int(Totalminutes)/60
        minutes = int(Totalminutes)%60
        return str(hours).zfill(2)+":"+str(minutes).zfill(2)+":00"

    def getScheduleSetpoint(self,testDate,scheduleData):
        schData = scheduleData
        daysofweek=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        todayDay = daysofweek[testDate.weekday()]
        if todayDay != 'monday':
            yesterdayDay = daysofweek[testDate.weekday()-1]
        else:
            yesterdayDay = 'sunday'

        TodaysSchedule = schData[todayDay]
        YesterdaysSchedule = schData[yesterdayDay]
        setPoints = YesterdaysSchedule[-1][2:] #yesterday's last setpoint
        nowminute = testDate.hour*60+testDate.minute
        for entries in TodaysSchedule:
            if int(entries[1]) <= nowminute:
                setPoints = [int(entries[2]),int(entries[3])]
            else:
                break
        return {'cool_setpoint':setPoints[0],'heat_setpoint':setPoints[1]}

def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    HoneywellThermostat = API(model='RTH8580', agent_id='wifithermostat1', api='API1', address='989550', username='srahman@akashsolar.com', password='smart900VT')  # 1146061
    # print("{0}agent is initialzed for {1} using API={2} at {3}".format(CT50Thermostat.get_variable('agent_id'),CT50Thermostat.get_variable('model'),CT50Thermostat.get_variable('api'),CT50Thermostat.get_variable('address')))
    # HoneywellThermostat.getDeviceStatus()
    # Step4: change device operating set points
    # HoneywellThermostat.setDeviceStatus({"thermostat_mode":"OFF","fan_mode":"AUTO"})
    # HoneywellThermostat.setDeviceStatus({"thermostat_mode":"COOL","fan_mode":"ON"})
    # HoneywellThermostat.setDeviceStatus({"heat_setpoint":63, "fan_mode":"ON"})
    # HoneywellThermostat.setDeviceStatus({"thermostat_mode":"HEAT","heat_setpoint":75})
    # Step5: read current thermostat status
    print HoneywellThermostat.discover('srahman@akashsolar.com', 'smart900VT')
    cookie = HoneywellThermostat.get_login()
    print HoneywellThermostat.getDeviceSchedule(cookie)
    _data = {'sunday': [[u'Wake', 360, 78.0, 71.0], [u'Leave', 480, 85.0, 63.0], [u'Return', 1080, 78.0, 70.0],
                        [u'Sleep', 1320, 82.0, 62.0]],
             'monday': [[u'Wake', 390, 78.0, 70.0], [u'Leave', 480, 85.0, 62.0], [u'Return', 1080, 78.0, 70.0],
                        [u'Sleep', 1320, 82.0, 62.0]],
             'tuesday': [[u'Wake', 360, 78.0, 70.0], [u'Leave', 480, 85.0, 64.0], [u'Return', 1080, 78.0, 70.0],
                         [u'Sleep', 1320, 82.0, 62.0]],
             'friday': [[u'Wake', 360, 79.0, 70.0], [u'Leave', 480, 85.0, 62.0], [u'Return', 1080, 78.0, 70.0],
                        [u'Sleep', 1320, 82.0, 62.0]], 'enabled': True,
             'wednesday': [[u'Wake', 360, 78.0, 70.0], [u'Leave', 480, 85.0, 62.0], [u'Return', 1080, 78.0, 70.0],
                           [u'Sleep', 1320, 82.0, 62.0]],
             'thursday': [[u'Wake', 360, 78.0, 70.0], [u'Leave', 480, 85.0, 62.0], [u'Return', 1080, 78.0, 70.0],
                          [u'Sleep', 1320, 82.0, 62.0]],
             'saturday': [[u'Wake', 360, 78.0, 70.0], [u'Leave', 480, 85.0, 62.0], [u'Return', 1080, 78.0, 70.0],
                          [u'Sleep', 1320, 82.0, 62.0]]}
    HoneywellThermostat.setDeviceSchedule(cookie,_data)
    print "DONE"
    # print HoneywellThermostat.getDeviceStatus()


    # HoneywellThermostat.getDeviceSchedule()


if __name__ == "__main__": main()
