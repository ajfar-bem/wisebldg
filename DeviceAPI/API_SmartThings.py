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

#__author__ = "Aditya Nugur"
#__credits__ = ""
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2016-10-17 12:04:50"
#__lastUpdated__ = "2016-10-18 11:23:33"
'''

'''This API class is for an agent that want to discover/communicate/monitor Tumalow energy ingenuity battery storage'''
import time
import requests
import json
from pprint import  pprint
from bemoss_lib.utils import db_helper
from BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY

debug=True
class API(baseAPI):

    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)
        self.uri = None
        self.base_url = None

        if 'token' in kwargs.keys():
            self.access_token = kwargs['token']
            self.getAppEndpoints(kwargs['token'])
        if 'nickname' in kwargs.keys():
            self.nickname = kwargs['nickname']
        if 'mac_address' in kwargs.keys():
            self.mac_address = kwargs['mac_address']

    def API_info(self):
        return [{'device_model': 'STenableSwitch', 'vendor_name': 'SmartThings', 'communication': 'WiFi', 'support_oauth': True,
                 'device_type_id': 3, 'api_name': 'API_SmartThings', 'html_template': 'plugload/plugload.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable': False, 'is_cloud_device': True,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True, 'chart_template': 'charts/charts_plugload.html'},
                {'device_model': 'STenablePowerSwitch', 'vendor_name': 'SmartThings', 'communication': 'WiFi',
                 'support_oauth': True,
                 'device_type_id': 3, 'api_name': 'API_SmartThings', 'html_template': 'plugload/plugload.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable': False, 'is_cloud_device': True,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_wtplug.html'},
                {'device_model': 'STenableDimmer', 'vendor_name': 'SmartThings', 'communication': 'WiFi',
                 'support_oauth': True,
                 'device_type_id': 3, 'api_name': 'API_SmartThings', 'html_template': 'lighting/lighting.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable': False, 'is_cloud_device': True,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_lighting.html'}
                ]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "image", "value": 'LightSW.png'},
                "bottom": BEMOSS_ONTOLOGY.STATUS.NAME, "image": "LightSW.png"}

    def ontology(self):
        return {"status": BEMOSS_ONTOLOGY.STATUS, "power": BEMOSS_ONTOLOGY.POWER,
                "brightness": BEMOSS_ONTOLOGY.BRIGHTNESS}

    def discover(self, username, password, token):
        self.getAppEndpoints(token)
        responses = list()
        header = {'Authorization': 'Bearer ' + token}
        url = self.uri + '/discover'
        r = requests.get(url, headers=header)
        try:
            if r.status_code == 200:
                device = {'switch': [], 'powermeter': [], 'dimmer': []}
                for item in json.loads(r.content):
                    device[item['type']].append((item['id'], item['name']))
                added_device = []
                for dimmer in device['dimmer']:
                    added_device.append(dimmer[0])
                    responses.append({'address': None, 'vendor': 'SmartThings',
                                      'mac': dimmer[0].replace('-', ''),
                                      'model': "STenableDimmer", 'nickname': dimmer[1]
                                      })
                for powermeter in device['powermeter']:
                    if powermeter[0] not in added_device:
                        added_device.append(powermeter[0])
                        responses.append({'address': None, 'vendor': 'SmartThings',
                                          'mac': powermeter[0].replace('-', ''),
                                          'model': "STenablePowerSwitch", 'nickname': powermeter[1]
                                          })
                for switch in device['switch']:
                    if switch[0] not in added_device:
                        added_device.append(switch[0])
                        responses.append({'address': None, 'vendor': 'SmartThings',
                                          'mac': switch[0].replace('-', ''),
                                          'model': "STenableSwitch", 'nickname': switch[1]
                                          })
                return responses
            else:
                return responses
        except:
            return responses


    def renewConnection(self):
        pass

    def getAppEndpoints(self, access_token):
        get_endpoint_url = 'https://graph.api.smartthings.com/api/smartapps/endpoints'
        headers = {'Authorization': 'Bearer ' + access_token}
        headers.update({'Content-Type': 'application/json'})
        response = requests.get(get_endpoint_url, headers=headers)
        endpoint_info = json.loads(response.content)[0]
        self.uri = endpoint_info['uri']
        # self.uri = 'https://graph.api.smartthings.com/api/smartapps/installations/468648eb-e879-45da-bcca-d7ce79280228'
        self.base_url = endpoint_info['base_url']

    def getDataFromDevice(self):
        header = {'Authorization': 'Bearer ' + self.access_token}
        switch_url = self.uri + '/switches'
        power_url = self.uri + '/powermeters'
        dimmer_url = self.uri + '/dimmers'
        devicedata = dict()

        r = requests.get(switch_url, headers=header)
        for item in json.loads(r.content):
            if item['id'].replace('-', '') == self.mac_address:
                status = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON if item['value'] == 'on' else BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF
                devicedata['status'] = status
                break
        r = requests.get(dimmer_url, headers=header)
        for item in json.loads(r.content):
            if item['id'].replace('-', '') == self.mac_address:
                devicedata['brightness'] = item['value']
                break
        r = requests.get(power_url, headers=header)
        for item in json.loads(r.content):
            if item['id'].replace('-', '') == self.mac_address:
                devicedata['power'] = item['value']
                break
        return devicedata


    def setDeviceData(self, postmsg):
        setDeviceStatusResult = True
        _data = json.dumps(postmsg)
        _data = json.loads(_data)

        seriel_no = self.mac_address[0:8] + '-' + self.mac_address[8:12] + '-' \
                   + self.mac_address[12:16] + '-' + self.mac_address[16:20] + \
                   '-' + self.mac_address[20:]

        if _data[BEMOSS_ONTOLOGY.STATUS.NAME] == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF:
            status = 'off'
        elif _data[BEMOSS_ONTOLOGY.STATUS.NAME] == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON:
            status = 'on'
        control_url = self.uri+ '/switches/' + status + '_' + seriel_no
        header = {'Authorization': 'Bearer ' + self.access_token}
        try:
            r = requests.put(control_url, headers=header)
        except:
            raise

        if BEMOSS_ONTOLOGY.BRIGHTNESS.NAME in _data.keys() and status == 'on':
            brightness = int(_data[BEMOSS_ONTOLOGY.BRIGHTNESS.NAME])
            control_url = self.uri+ '/dimmers/' + str(brightness) + '_' + seriel_no
            header = {'Authorization': 'Bearer ' + self.access_token}
            try:
                r = requests.put(control_url, headers=header)
            except:
                raise

        return setDeviceStatusResult

# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    SmartThings = API(agent_id='testagent', token = 'b3a26f5d-7d07-46df-9f12-e278e7db82db')

    #BatteryStorage.getDeviceStatus()
    # SmartThings.getAppEndpoints('b3a26f5d-7d07-46df-9f12-e278e7db82db')
    # pprint(SmartThings.discover(None, None, 'b3a26f5d-7d07-46df-9f12-e278e7db82db'))
    # SmartThings.nickname = 'Switch2'
    SmartThings.mac_address = '98fa6201fff740339614970646337f5b'
    print SmartThings.getDataFromDevice()
    # SmartThings.setDeviceData({'status':'OFF', 'brightness':60})

if __name__ == "__main__": main()