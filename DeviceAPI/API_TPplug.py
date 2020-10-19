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

#__author__ ="Ashraful Haque"
#__credits__ = ""
#__version__ = "Plus"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2018-07-24"
#__lastUpdated__ = "2018-07-31"
'''

'''This API class is for an agent that want to communicate/monitor/control
devices that compatible with TPLink plugload'''

from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import requests
import settings
import os
import json
from requests.auth import HTTPBasicAuth

BASE = 'https://wap.tplinkcloud.com'



class API(baseAPI):

    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)

        self.device_supports_auto = False
        self.set_variable('offline_count', 0)
        self.set_variable('connection_renew_interval', 6000)  
        
        if 'username' in self.config.keys():
            self.username = self.config['username']
            self.password = self.config['password']
            self.device_id=self.config['address']

    def API_info(self):
        return [{'device_model': 'TP Smart Plug', 'vendor_name': 'TPlink', 'communication': 'Wifi', 'support_oauth' : False,
                 'device_type_id': 3, 'api_name': 'API_TPplug', 'html_template': 'plugload/plugload.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable': False, 'is_cloud_device': True,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,'chart_template': 'charts/charts_wtplug.html'}]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "image", "value": 'smartplug.png'},
                "bottom": BEMOSS_ONTOLOGY.STATUS.NAME, "image":"smartplug.png"}


    def ontology(self):
        return {"relay_state": BEMOSS_ONTOLOGY.STATUS,
                "power": BEMOSS_ONTOLOGY.POWER}

    def discover(self,username,password,token=None):

        devicelist = list()
        try:

            id_url= BASE
            params={
                     "method": "login",
                     "params": {
                    "appType": "Kasa_Android",
                    "cloudUserName": username,
                    "cloudPassword": password,
                    "terminalUUID": "MY_UUID_v4"
                     }
                    }

            response_auth = requests.post(id_url,json=params)
            response_j=response_auth.json()
            api_token=response_j['result']['token']
            url = id_url+'?token='+api_token

            params = {"method":"getDeviceList"}
            response_list = requests.post(url,json=params)
            response_list=response_list.json()
            num_device=response_list['result']['deviceList']
            vendor="TPlink"
            for device in response_list['result']['deviceList']:
                device_sort = str(device['deviceName'])
                if device_sort == 'Wi-Fi Smart Plug With Energy Monitoring':
                    device_id = str(device['deviceId'])
                    mac = str(device['deviceMac'])
                    devicelist.append({'address': device_id, 'mac': mac, 'model': "TP Smart Plug", 'vendor': vendor})
            #print (devicelist)
        except Exception as e:
            raise
        return devicelist


    def getDataFromDevice(self):

        devicedata = {}

        try:

            id_url= BASE
            params={
                     "method": "login",
                     "params": {
                    "appType": "Kasa_Android",
                    "cloudUserName": self.username,
                    "cloudPassword": self.password,
                    "terminalUUID": "MY_UUID_v4"
                     }
                    }
            device_id=self.config['address']
            response_auth = requests.post(id_url,json=params)
            response_j=response_auth.json()
            api_token=response_j['result']['token']



            url_endpoint = id_url + '?token=' + api_token
            params_api_endpoint = {"method": "getDeviceList"}
            response_api_endpoint=requests.post(url_endpoint,json=params_api_endpoint)
            response_json_api_endpoint = response_api_endpoint.json()
            api_endpoint= response_json_api_endpoint['result']['deviceList'][0]['appServerUrl']





            url = api_endpoint+'?token='+api_token
            sys_data={"system":{"get_sysinfo":"null"},"emeter":{"get_realtime":"null"}}
            params =  {"method":"passthrough", "params": {"deviceId": device_id, "requestData":json.dumps(sys_data)}}
            response = requests.post(url,json=params)
            response_test=response.json()
            responseDataJson1 = json.loads(response_test['result']['responseData'])
            relay_state=responseDataJson1['system']['get_sysinfo']['relay_state']
            if relay_state==1:
                status=BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON
            else:
                status=BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF
            power=responseDataJson1['emeter']['get_realtime']['power']

        except Exception as e:
            raise

        devicedata ={'relay_state':status, 'power':power}
        return devicedata

    def setDeviceStatus(self, postmsg):
        setDeviceStatusResult = True

         # Data conversion before passing to the device
        _data = json.dumps(postmsg)
        _data = json.loads(_data)

        if _data[BEMOSS_ONTOLOGY.STATUS.NAME] == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF:
            newstatus = 0
        else:
            newstatus = 1
        id_url= BASE
        params={
                     "method": "login",
                     "params": {
                    "appType": "Kasa_Android",
                    "cloudUserName": self.username,
                    "cloudPassword": self.password,
                    "terminalUUID": "MY_UUID_v4"
                     }
                    }
        response_auth = requests.post(id_url,json=params)
        response_j=response_auth.json()
        api_token=response_j['result']['token']

        url_endpoint = id_url + '?token=' + api_token
        params_api_endpoint = {"method": "getDeviceList"}
        response_api_endpoint = requests.post(url_endpoint, json=params_api_endpoint)
        response_json_api_endpoint = response_api_endpoint.json()
        api_endpoint = response_json_api_endpoint['result']['deviceList'][0]['appServerUrl']

        url = api_endpoint+'?token='+api_token
        sys_data={"system":{"set_relay_state":{"state":newstatus}}}
        params =  {"method":"passthrough", "params": {"deviceId":self.device_id, "requestData":json.dumps(sys_data) }}

        try:
            response = requests.post(url,json=params)
        except:
            raise

        return setDeviceStatusResult


    def identifyDevice(self):
        identifyDeviceResult = False
        try:

            self.toggleDeviceStatus()
            print(self.get_variable("model") + " is being identified with starting status " + str(
                self.get_variable('status')))
            self.timeDelay(15)
            self.toggleDeviceStatus()
            print("Identification for " + self.get_variable("model") + " is done with status " + str(
                self.get_variable('status')))
            identifyDeviceResult = True
        except:
            raise
        return identifyDeviceResult

    def toggleDeviceStatus(self):
        if self.getDataFromDevice()['status'] == "OFF":
            self.setDeviceStatus({"status":"ON"})
        else:
            self.setDeviceStatus({"status":"OFF"})

# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    VeraDevice = API(model='kasa plug', api='API_TPplug',address="800634C4A488A4fA2AC0AA868244014A1878FEDE",username="fmatiq@yahoo.com",password="Amena2011")
    #print VeraDevice.discover("mkuzlu@vt.edu","Ari900_Ari900")
    VeraDevice.discover("fmatiq@yahoo.com","Amena2011")
    # VeraDevice.setDeviceStatus({'status': 'on'})
    VeraDevice.getDataFromDevice()
   # VeraDevice.identifyDevice()#

if __name__ == "__main__": main()
