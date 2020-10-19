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

#__author__ = "Aditya nugur"
#__credits__ = ""
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2016-10-16 12:04:50"
#__lastUpdated__ = "2016-10-18 11:23:33"
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

from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from DeviceAPI.BaseAPI_Thermostat import BaseAPI_Thermsostat

debug = True


class ServerException(Exception):
    pass

class API(BaseAPI_Thermsostat):

    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)
        self.device_supports_auto = False
        self.set_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME,BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF)
        self._debug = True
        self.Nicknames = ['WAKE','LEAVE','RETURN','SLEEP']
        mac_address = kwargs['mac_address']
        self.cookie_path = os.path.expanduser(settings.PROJECT_DIR + '/.temp/.ICM' + mac_address+'cookie.txt')
        if 'username' in kwargs.keys():
            self.username = kwargs['username']
            self.password = kwargs['password']
        if 'api_config' in kwargs.keys():
            self.device_config=kwargs['api_config']

    def API_info(self):
        return [{'device_model': 'ICM100', 'vendor_name': 'ICM Controls', 'communication': 'WiFi', 'support_oauth' : False,
                'device_type_id': 1,'api_name': 'API_ICM','html_template':'thermostat/thermostat.html',
                'agent_type':'ThermostatAgent','identifiable': False, 'authorizable': False, 'is_cloud_device': True,
                'schedule_weekday_period': 4,'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_thermostat.html',"built_in_schedule_support": True},
                ]

    def dashboard_view(self):
        if self.get_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": None, "image":"Thermostat.png"}
        else:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": BEMOSS_ONTOLOGY.SETPOINT.NAME, "image":"Thermostat.png"}

    def ontology(self):
        return {"mode":BEMOSS_ONTOLOGY.THERMOSTAT_MODE,"thermostat_state":BEMOSS_ONTOLOGY.THERMOSTAT_STATE,
                "fanMode":BEMOSS_ONTOLOGY.FAN_MODE,"fan_state":BEMOSS_ONTOLOGY.FAN_STATE,
                "cool_setpoint":BEMOSS_ONTOLOGY.COOL_SETPOINT,"heat_setpoint":BEMOSS_ONTOLOGY.HEAT_SETPOINT,
                "currentTemperature":BEMOSS_ONTOLOGY.TEMPERATURE,"hold":BEMOSS_ONTOLOGY.HOLD,
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
            parsed = urlparse(new_address)
            new_address = parsed.scheme+"://"+parsed.netloc
            self.set_variable('address',new_address)
            with open(self.variables['config_path'],'r') as f:
                k = json.loads(f.read())
            k['address'] = new_address
            with open(self.variables['config_path'], 'w') as outfile:
                json.dump(k, outfile, indent=4, sort_keys=True)

    tmode_dict = {0:BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF,
                  1:BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL,
                  2:BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT,
                  3:BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.AUTO}
    fmode_dict = {0:BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.AUTO,
                  1:BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.ON,
                  2:BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.CIRCULATE}
    hold_dict  =  {0:BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE,
                  1:BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY,
                  2:BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.PERMANENT}

    # GET Open the URL and read the data
    def getDataFromDevice(self):

        _token = self.account_login(self.username, self.password)
        if _token != 0:
            for i in range(2): #response failed due to invalid token; trying once more to get data using new token;otherwise declaring server issue
                _response = self.postJSONtoICM(
                    {"action": "thermostatGetDetail", "thermostatKey": self.config["address"], "token": _token})
                if self._debug: print _response
                if _response != 0 and _response['result'] != 'failed':
                    devicedata = self.getDeviceStatusJson(_response)  # convert string data to JSON object
                    #self.printDeviceStatus()
                    #self.account_logout(_token)
                    return devicedata
                else:
                    _token = self.account_login(self.username,self.password,relogin=True)

            raise Exception('Bad response from server')

        else:
            getDeviceStatusResult = False
            #self.account_logout(_token)
            raise Exception('Cannot login; got no token')


    def getDeviceStatusJson(self, _data):
            # Use the json module to load the string data into a dictionary
            # 1. temperature
            if "detail" not in _data:
                return None

            devicedata = {"currentTemperature": _data["detail"]["currentTemperature"]}
            # 2. thermostat_mode
            if _data["detail"]["mode"] == 0:
                thermostat_mode =  BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF
            elif _data["detail"]["mode"] == 1:
                thermostat_mode =  BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL
            elif _data["detail"]["mode"] == 2:
                thermostat_mode =  BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT
            elif _data["detail"]["mode"] == 3:
                thermostat_mode =  BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.AUTO

            else:
                raise Exception("Invalid value for device thermostat_mode")

            devicedata["mode"] = thermostat_mode
            # 3. Set point
            devicedata["heat_setpoint"] = _data["detail"]["heatTo"]
            devicedata["cool_setpoint"] =  _data["detail"]["coolTo"]
            scheduleList = _data["detail"]['scheduleData']
            scheduleData = self.getDeviceSchedule(scheduleList)
            devicedata["scheduleData"] = scheduleData

            if _data["detail"]['runOnSchedule'] in {1,2}:  # schedule Off
                hold = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.PERMANENT  # schedule Off; permanent hold
            elif _data["detail"]['runOnSchedule'] == 0:  # run on Schedule
                sch = self.getScheduleSetpoint(scheduleData,datetime.datetime.now())  # current set-point according to schedule
                sch_near = self.getScheduleSetpoint(scheduleData,
                    datetime.datetime.now() + datetime.timedelta(minutes=10))  # set-point in 10 minutes
                hold = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.NONE  # default case (No hold, running on schedule)
                if self.get_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) in ['COOL',
                                                            'AUTO']:  # if cool mode or automode and set_point don't agree, then its temp hold
                    if self.get_variable(BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME) not in [sch[0], sch_near[0]]:
                        hold = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY  # Temporary Hold
                if self.get_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) in ['HEAT',
                                                            'AUTO']:  # if heat mode or automode and set_point don't agree, then its temp hold
                    if self.get_variable(BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME) not in [sch[1], sch_near[1]]:
                        hold = BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY  # Temporary Hold

            devicedata["hold"] = hold
            # 4. fan_mode
            if _data["detail"]["fanMode"] == 0:
                fan_mode = BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.AUTO
            elif _data["detail"]["fanMode"] == 1:
                fan_mode = BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.ON
            elif _data["detail"]["fanMode"] == 2:
                fan_mode = BEMOSS_ONTOLOGY.FAN_MODE.POSSIBLE_VALUES.CIRCULATE
            else:
                raise Exception(" Invalid value for fan_mode")

            devicedata["fanMode"] = fan_mode

            # 5. thermostat_state
            devicedata["thermostat_state"] = thermostat_mode

            # 6. fan_state
            devicedata["fan_state"] = fan_mode
            if self._debug: print devicedata
            return devicedata


    def getDeviceSchedule(self,scheduleList):
        scheduleData = dict()
        days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

        scheduleData['Enabled'] = True #Always make it true. (Legacy purpose.)

        for day in days:
            scheduleData[day]=list()
            for i in [0,4,8,12]:
                index = days.index(day)*16+i
                id = [0,4,8,12].index(i)
                cool_setpoint = scheduleList[index+2]
                heat_setpoint = scheduleList[index+3]

                scheduleData[day].append([self.Nicknames[id],str(scheduleList[index]*60+scheduleList[index+1]),str(cool_setpoint),str(heat_setpoint)])

        return scheduleData


    def setDeviceData(self, postmsg):
        is_success = True
        postmsg = self.validatePostmsg(postmsg)
        if postmsg:  # check if the data is not empty
            _token = self.account_login(self.username, self.password)
            #print _token
            if _token != 0:
                for i in range(2):
                    try:
                        if 'scheduleData' in postmsg:
                            scheduleData = postmsg.pop('scheduleData')
                            self.setDeviceSchedule(_token,scheduleData)

                        if not postmsg: #if it only contains scheduleData we are done
                            return True

                        _data = self.convertPostMsg(postmsg,_token)
                        for post_message in _data:

                            _response=self.postJSONtoICM(post_message)
                            if BEMOSS_ONTOLOGY.HOLD.NAME in postmsg:
                                if 'runOnSchedule' in post_message and postmsg['hold']==BEMOSS_ONTOLOGY.HOLD.POSSIBLE_VALUES.TEMPORARY: #need to do twice if trying to do temporary hold.
                                    time.sleep(15) #needs to wait before sending another command to change the setpoint, otherwise it would be ignored and the set-point goes back to schedule set-point.
                                    _response=self.postJSONtoICM(post_message)

                            if _response != 0:
                                if _response["result"]=="success":
                                    pass
                                else:
                                    raise ServerException('Server failed')

                    except ServerException: #the server failed, so get a fresh token
                        _token = self.account_login(self.username, self.password, relogin=True)

            else:
                raise Exception("classAPI_ICMThermostat: ERROR: setdevicestatus couldn't set status, Problem with token")

            #self.account_logout(_token)
        else:
            is_success = False
            raise Exception("The POST message is invalid, check thermostat_mode, heat_setpoint, cool_coolsetpoint setting and try again\n")


    def validatePostmsg(self, postmsg):  # validate of postmsg
        if BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME in postmsg:
            if postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.HEAT:
                if BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME in postmsg:
                    postmsg.pop(BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME)

            elif postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.COOL:
                for k,v in postmsg.items():
                    if k == BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME:
                        postmsg.pop(BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME)

        return postmsg

    def convertPostMsg(self, postmsg, token):
        msgToDevice = dict()
        allMsgsToDevice = list()
        msgToDevice["token"] = token
        msgToDevice["thermostatKey"] = self.config['address']
        if BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME in postmsg or BEMOSS_ONTOLOGY.FAN_MODE.NAME in postmsg:
            msgToDevice["action"] = "thermostatSetMode"
            if BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME in postmsg:
                msgToDevice["mode"]=self.dict_rev_translate(self.tmode_dict,postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME))
            else:
                msgToDevice ["mode"] = self.get_variable("thermostat_mode")
            if BEMOSS_ONTOLOGY.FAN_MODE.NAME in postmsg:
               msgToDevice["fanMode"]=self.dict_rev_translate(self.fmode_dict,postmsg.get(BEMOSS_ONTOLOGY.FAN_MODE.NAME))
            else:
               msgToDevice["fanMode"] = self.dict_rev_translate(self.fmode_dict, self.get_variable("fan_mode"))
            allMsgsToDevice.append(msgToDevice.copy())

        if BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME in postmsg or BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME in postmsg or BEMOSS_ONTOLOGY.HOLD.NAME in postmsg:
            msgToDevice["action"] = "thermostatSetPoint"
            if BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME in postmsg:
                msgToDevice["heatTo"] = str(postmsg.get(BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME))
            else:
                msgToDevice["heatTo"] = str(self.get_variable(BEMOSS_ONTOLOGY.HEAT_SETPOINT.NAME))
            if BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME in postmsg:
                msgToDevice["coolTo"] = str(postmsg.get(BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME))
            else:
                msgToDevice["coolTo"] = str(self.get_variable(BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME))

            if BEMOSS_ONTOLOGY.HOLD.NAME in postmsg:
                if postmsg.get("hold") in ["NONE","TEMPORARY"]: #if hold is None or Temp, schedule is On. If it is Permanent, schedule is OFF
                    msgToDevice["runOnSchedule"] = 0  # #schedule On
                    hold = str(self.dict_rev_translate(self.hold_dict, postmsg.get(BEMOSS_ONTOLOGY.HOLD.NAME)))
                    currentData = self.getDataFromDevice()
                    scheduleData = currentData['scheduleData']
                    if hold == 0:  #If hold has been set to 0, (schedule ON), then set the setpoint according to schedule
                            sch = self.getScheduleSetpoint(scheduleData,datetime.datetime.now())
                            if postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) in ["HEAT", "AUTO"]:
                                msgToDevice["heatTo"] = sch[1]
                            if postmsg.get(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) in ["COOL", "AUTO"]:
                                msgToDevice["coolTo"] = sch[0]
                else :
                    msgToDevice["runOnSchedule"] = "1"#schedule Off
                    msgToDevice["action"] = "thermostatSetPoint"
            else:
                msgToDevice["runOnSchedule"] = str(self.dict_rev_translate(self.hold_dict,self.get_variable(BEMOSS_ONTOLOGY.HOLD.NAME)))

            allMsgsToDevice.append(msgToDevice)

        return allMsgsToDevice

    def setDeviceSchedule(self,_token,scheduleData):
        self.variables['scheduleData'] = scheduleData
        scheduleList = self.getList(scheduleData)
        self.set_variable('scheduleList',scheduleList)
        if _token != 0:
            _response=self.postJSONtoICM({'action':'thermostatSetSchedule','thermostatKey': self.config["address"],"token": _token, 'scheduleData':scheduleList})
            if _response != 0:
                #print "Response 1:"+ str(_response)
                if _response["result"]=="success": # and _response2["result"]=="success":
                    #print ("Device status changed successfully")
                    pass
                else:
                    raise ServerException("classAPI_ICMThermostat: ERROR: setSchedule couldn't set Schedule. Unsuccessful response from server")
            else:
                raise ServerException("classAPI_ICMThermostat: ERROR: setSchedule couldn't set Schedule. No response")

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

    def getScheduleSetpoint(self, scheduleData, testDate):
        daysofweek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        todayDay = daysofweek[testDate.weekday()]
        if todayDay != 'monday':
            yesterdayDay = daysofweek[testDate.weekday() - 1]
        else:
            yesterdayDay = 'sunday'

        TodaysSchedule = scheduleData[todayDay]
        YesterdaysSchedule = scheduleData[yesterdayDay]
        setPoints = YesterdaysSchedule[-1][2:]  # yesterday's last setpoint
        nowminute = testDate.hour * 60 + testDate.minute
        for entries in TodaysSchedule:
            if int(entries[1]) <= nowminute:
                setPoints = [int(entries[2]), int(entries[3])]
            else:
                break
        return setPoints

    def postJSONtoICM(self, _data):
            _communication_success = True
            _urlData = 'https://www.captouchwifi.com/icm/api2/call/'
            _data = json.dumps(_data)
            _data = _data.encode(encoding='utf_8')
            _request = urllib2.Request(_urlData)
            _request.add_header('Content-Type', 'application/json')

            try:
                _f = urllib2.urlopen(_request, _data)

                if (_f.getcode() == 200):
                    _response = _f.read().decode('utf-8')
                    #if self.debug:
                    #print "Received: \n" + _response
                    return json.loads(_response)
                else:
                    _communication_success = False
            except:
                raise


    def account_login(self,username,password,relogin=False):

            if not relogin:
                try:
                    with open(self.cookie_path ,'r') as cokiefile:
                                     cookie=cokiefile.read()
                                     return cookie
                                     # _response = self.postJSONtoICM({"action": "userLogin", "username": username, "password": password,"token": cookie})
                                     # if _response != 0:
                                     #     if _response["result"] == "success":
                                     #        return cookie
                                     #     else:
                                     #         pass
                                     # else:
                                     #     pass
                except IOError as er:
                    if er[0] == 2: #No such file or directory
                        pass

                login_success = True

            _responseJSON = self.postJSONtoICM({"action": "getToken", "clientType": "virginia tech"})

            if _responseJSON != 0:
                _token = _responseJSON["token"]


                _response = self.postJSONtoICM({"action": "userLogin", "username": username, "password": password, "token": _token})

                if _response != 0:
                    if _response["result"] == "success":
                        try:
                            with open(self.cookie_path,'w') as cokiefile:
                                cokiefile.write(_token)
                                cokiefile.truncate()
                        except IOError as er:
                                #print er
                                pass
                        return _token
                    else:
                        login_success = False
                else:
                    login_success = False
            else:
                login_success = False

            if login_success == False:
                raise Exception("classAPI_ICMThermostat: ERROR: Couldn't Login to ICM account")

    def account_logout(self, token):
            logout_success = False
            _response = self.postJSONtoICM({"action": "logout", "token": token})

            if _response != 0:
                if _response["result"] == "success":
                    logout_success = True
            return logout_success

    def discover(self,username, password,token=None):
            _token = self.account_login(username, password)
            # print _token
            device_list = list()
            if _token != 0:
                # _response=self.postJSONtoICM({"action": "thermostatGetDetail","thermostatKey": "BGQKEKRXBGFV","token": _token})
                _response = self.postJSONtoICM({"action": "getThermostats", "token": _token})

                if _response != 0:
                    for thermostat in _response["thermostats"]:
                        device_list.append({'address': thermostat["unique_key"], 'mac': thermostat["unique_key"],
                                            'model': thermostat["model_name"], 'vendor': self.API_info()[0]['vendor_name'],
                                            'nickname': thermostat["name"]})
                else:
                    raise Exception("Discovery of ICM Thermostats failed because there's no response for the token!")

            else:
                raise Exception("Discovery of ICM Thermostats failed because token is 0!")
            #print device_list
            #self.account_logout(_token)
            return device_list


# This main method will not be executed when this class is used as a module
def main():
    #Test code

    # Step1: create an object with initialized data from DeviceDiscovery Agent
    ICMThermostat = API(model='ICM100',agent_id='wifithermostat1',api='API_ICM',address='BGQKEKRXBGFV', username= 'mkuzlu', password= 'DRTeam@900')
    ICMThermostat.getDeviceStatus()
    #ICMThermostat.discover("mkuzlu","DRTeam@900")
    #ICMThermostat.setDeviceStatus({"thermostat_mode":"COOL","fan_mode":"AUTO", "cool_setpoint":65})
    #ICMThermostat.setDeviceStatus({"hold" : "NONE"})
    ICMThermostat.setDeviceStatus({"thermostat_mode":"HEAT","heat_setpoint":72, "hold" : "PERMANENT"})
    #ICMThermostat.setDeviceStatus({"thermostat_mode": "HEAT", "fan_mode": "ON", "heat_setpoint": 75})

    ICMThermostat.getDeviceStatus()

if __name__ == "__main__": main()
