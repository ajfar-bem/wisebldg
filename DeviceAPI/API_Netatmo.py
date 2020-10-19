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
import requests
import settings
from urlparse import urlparse

from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY

debug = True

class API(baseAPI):

    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)
        self._debug = True
        self.cookie_path = os.path.expanduser(settings.PROJECT_DIR + '/.temp/.Netatmocookie.txt')
        if 'username' in kwargs.keys():
            self.username = kwargs['username']
            self.password = kwargs['password']


    def API_info(self):
        return [{'device_model': 'Netatmo Weather Station', 'vendor_name': 'Netatmo', 'communication': 'WiFi',
                'device_type_id': 4,'api_name': 'API_Netatmo','html_template':'sensors/weather_sensor.html', 'support_oauth': False,
                'agent_type':'BasicAgent','identifiable': False, 'authorizable' : False, 'is_cloud_device': True,
                'schedule_weekday_period': 4,'schedule_weekend_period': 4, 'allow_schedule_period_delete': True, 'chart_template': 'charts/charts_weather_sensor.html'},
                ]

    def dashboard_view(self):

        return {"top": BEMOSS_ONTOLOGY.OUTSIDE_TEMPERATURE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
        "bottom": BEMOSS_ONTOLOGY.CO2.NAME, "image":"WeatherSensor.png"}

    def ontology(self):
        return {"Noise":BEMOSS_ONTOLOGY.NOISE,"Temperature":BEMOSS_ONTOLOGY.TEMPERATURE,'Humidity':BEMOSS_ONTOLOGY.RELATIVE_HUMIDITY,
                'Pressure':BEMOSS_ONTOLOGY.PRESSURE,"CO2":BEMOSS_ONTOLOGY.CO2,'max_temp':BEMOSS_ONTOLOGY.MAX_TEMPERATURE,
                'min_temp':BEMOSS_ONTOLOGY.MIN_TEMPERATURE}

    def renewConnection(self):
        pass

    def login(self):
        # Step1: Get access token
        # My API (POST https://api.netatmo.net/oauth2/token)
        try:
            r = requests.post(
                url="https://api.netatmo.net/oauth2/token",
                headers={
                    "Host": "api.netatmo.net", "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8 ",
                },
                data={
                    "client_id": "54defa2c495a886d4c12ca24",
                    "username": self.username,
                    "password": self.password,
                    "scope": "read_station",
                    "client_secret": "aHdiNF8saAUmYjZQDp8uCvhnPHpwywGc",
                    "grant_type": "password",
                },
                verify=False
            )
            # print('Response HTTP Status Code : {status_code}'.format(status_code=r.status_code))
            # print('Response HTTP Response Body : {content}'.format(content=r.content))

            if r.status_code == 200:  # 200 means successfully
                self.getAccessTokenJson(r.content)  # convert string data to JSON object
                # My API (3) (GET https://api.netatmo.net/api/devicelist)
            else:
                raise Exception(" Received an error from server, cannot retrieve results {}".format(r.status_code))
        except requests.exceptions.RequestException as e:
            raise

    def getAccessTokenJson(self, data):
        # Use the json module to load the string data into a dictionary
        _theJSON = json.loads(data)
        try:
            self.set_variable("access_token", _theJSON["access_token"])
            self.set_variable("refresh_token", _theJSON["access_token"])
            self.set_variable("scope", _theJSON["scope"][0])
            self.set_variable("expire_in", _theJSON["expire_in"])
        except:
            raise

    def getDeviceList(self):
        try:
            r = requests.get(
                url="https://api.netatmo.net/api/devicelist",
                params={
                    "access_token": self.get_variable("access_token"),
                },
                verify=False
            )
            data = json.loads(r.content)
            return data['body']['devices']+data['body']['modules']
            # self.printDeviceStatus()
        except requests.exceptions.RequestException as e:
            raise

    # GET Open the URL and read the data
    def getDataFromDevice(self):

        try:
            r = requests.post(
                url="https://api.netatmo.net/oauth2/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8 ",
                },
                data={
                    "client_id": "54defa2c495a886d4c12ca24",
                    "username": self.username,
                    "password": self.password,
                    "scope": "read_station",
                    "client_secret": "aHdiNF8saAUmYjZQDp8uCvhnPHpwywGc",
                    "grant_type": "password",
                },
                verify=False
            )
            # print "{0} Agent is querying its current status (status:{1}) at {2} please wait ...".format(
            #     self.variables.get('agent_id', None),
            #     r.status_code,
            #     datetime.datetime.now())
            if r.status_code == 200:  # 200 means successfully
                self.getAccessTokenJson(r.content)  # convert string data to JSON object
                # My API (3) (GET https://api.netatmo.net/api/devicelist)
                try:
                    r = requests.get(
                        url="https://api.netatmo.net/api/devicelist",
                        params={
                            "access_token": self.get_variable("access_token"),
                        },
                        verify=False
                    )
                    devicedata = self.getDeviceStatusJson(r.content)
                    return devicedata

                except requests.exceptions.RequestException as e:
                    raise
            else:
                raise Exception(" Received an error from server, cannot retrieve results {}".format(r.status_code))
            # Check the connectivity

        except requests.exceptions.RequestException as e:
            raise

    def getDeviceStatusJson(self, _data):
            # Use the json module to load the string data into a dictionary
            # 1. temperature
            _theJSON = json.loads(_data)
            devicedata = dict()
            device_index = 0
            module_index = 0
            i=0
            for device in _theJSON["body"]["devices"] + _theJSON["body"]["modules"]:
                if device['_id'] != self.config['address']:
                    continue

                for var in self.ontology().keys():
                    if var in device['dashboard_data']:
                        if var in ['Temperature','min_temp','max_temp']:
                            devicedata[var] = device['dashboard_data'][var] *  9.0 / 5 + 32
                        else:
                            devicedata[var] = device['dashboard_data'][var]
                    else:
                        devicedata[var] = None

            return devicedata


    def discover(self,username,password,token=None):
        self.username = username
        self.password = password
        self.login()
        devices = self.getDeviceList()
        device_list = list()
        i = 1
        for device in devices:
            nickname = ""
            if 'station_name' in device:
                #this is the main module
                nickname = device['station_name']
            elif 'main_device' in device:
                for d in devices:
                    if d['_id'] == device['main_device']:
                        nickname = d['station_name']+'_'+device['module_name']
            if not nickname:
                nickname = "Netatmo" + str(i)
                i += 1

            device_list.append({'address': device['_id'], 'mac': device['_id'].replace(':', ''), 'model': self.API_info()[0]['device_model'],
                                'vendor': self.API_info()[0]['vendor_name'], 'nickname': nickname})

        return device_list


# This main method will not be executed when this class is used as a module
def main():
    #Test code

    Netatmo = API(model='Weather Station', agent_id='netatmo1', api='API1',address = '70:ee:50:04:f4:0e'
                  ,username='aribemoss@gmail.com',password='DRTeam@900')
    print("{0} agent is initialzed for {1} using API={2} at {3}".format(Netatmo.get_variable('agent_id'),
                                                                        Netatmo.get_variable('model'),
                                                                        Netatmo.get_variable('api'),
                                                                        Netatmo.get_variable('address')))
    # Step2: read current thermostat status
    devices = Netatmo.discover()
    print devices
    data = Netatmo.getDataFromDevice()
    print data

if __name__ == "__main__": main()
