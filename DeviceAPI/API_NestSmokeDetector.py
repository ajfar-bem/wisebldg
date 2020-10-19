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

#__author__ = "Rajarshi Roy"
#__credits__ = "Rajarshi Roy"
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2017-07-24 12:04:50"
#__lastUpdated__ = "2017-7-7 11:23:33"
'''

'''This API class is for an agent that want to discover/communicate/monitor Nest IP Cam'''
import json
import requests
from BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY

debug = True

url = "https://developer-api.nest.com/"


class API(baseAPI):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.config = kwargs

    def API_info(self):
        return [{'device_model': 'Smoke Detector', 'vendor_name': 'Nest', 'communication': 'WiFi', 'support_oauth': True,
                 'device_type_id': 4, 'api_name': 'API_NestSmokeDetector', 'html_template': 'sensors/Nest_smoke_detector.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable': False, 'is_cloud_device': True,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_ipcam.html'} ]

    def dashboard_view(self):
        return {"top":BEMOSS_ONTOLOGY.CO_LEVEL_FINAL.NAME, "center":{"type": "image", "value": 'smoke.png'},
        "bottom": BEMOSS_ONTOLOGY.SMOKE_STATUS.NAME}

    def ontology(self):
        return {'battery_status':BEMOSS_ONTOLOGY.BATTERY_STATUS,
                'co_state':BEMOSS_ONTOLOGY.CO_LEVEL,
                'smoke':BEMOSS_ONTOLOGY.SMOKE_STATUS,
                'co_status_capital':BEMOSS_ONTOLOGY.CO_LEVEL_FINAL}


    def discover(self,username,password,token):

        responses = list()
        try:
            headers = {'Authorization': 'Bearer {0}'.format(token),
                       'Content-Type': 'application/json'}
            self.initial_response = requests.get(
                "https://firebase-apiserver09-tah01-iad01.dapi.production.nest.com:9553/", headers=headers,
                allow_redirects=False)
            json_file = self.initial_response.text
            json_response = json.loads(json_file)

            device_ids = json_response['devices']['smoke_co_alarms'].keys()
            for device_id in device_ids:
                device_id = str(device_id)
                mac_address =device_id
                model_name = 'Smoke Detector'
                #address= device_id

                responses.append({'address': "https://firebase-apiserver09-tah01-iad01.dapi.production.nest.com:9553/", 'mac': mac_address,
                                        'model': model_name, 'vendor': "Nest"})
            return responses

        except Exception as e:
            print (e)
            return responses

    def getDataFromDevice(self):
        activity = {}
        try:
            if not hasattr(self, "response"):
                token = self.config["token"]
                headers = {'Authorization': 'Bearer {0}'.format(token),
                           'Content-Type': 'application/json'}
                self.initial_response = requests.get(
                    self.config["address"], headers=headers,
                    allow_redirects=False)
            self.response = self.initial_response.text
            json_response = json.loads(self.response)
            device_ids = json_response['devices']['smoke_co_alarms'].keys()
            for device_id_ in device_ids:
                device_id = ''.join(device_id_)  # for converting the list to string
                if device_id ==self.config["mac_address"]:
                    battery_status = json_response['devices']['smoke_co_alarms'][device_id]['battery_health']  # battery status
                    battery=battery_status.upper()
                    co_status=json_response['devices']['smoke_co_alarms'][device_id]['co_alarm_state'].upper() # co state
                    co_status_final ='CO: '+co_status
                    smoke_state = json_response['devices']['smoke_co_alarms'][device_id]['smoke_alarm_state'].upper()  # smoke state
                    activity = { 'battery_status': battery, 'co_state': co_status,'smoke': smoke_state,'co_status_capital':co_status_final}
                    print (activity)
                    return activity
        except Exception as e:
            print (e)
            return activity



# This main method will not be executed when this class is used as a module
def main():
    # Test code

    # Step1: create an object with initialized data from DeviceDiscovery Agent
    IPCam = API(model='Office Detector', agent_id='basicagent', api='API_NestSmokeDetector', address='http://192.168.10.133:8900',
                username="royraj987@gmail.com", password="Countduku123!",mac_address="TPWbssSc")
    #J=IPCam.discover()
    #print J
    #J1 = IPCam.getDataFromDevice()
    #print J1


    #t = IPCam.setDeviceStatus({"status":"ON"})
    #print t


if __name__ == "__main__": main()