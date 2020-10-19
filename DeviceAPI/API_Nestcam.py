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

#__author__ = "Rajarshi Roy and Aditya Nugur"
#__credits__ = ""
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2016-10-17 12:04:50"
#__lastUpdated__ = "2017-7-7 11:23:33"
'''

'''This API class is for an agent that want to discover/communicate/monitor Nest IP Cam'''
import json
import requests
from BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import settings
import os



debug = True

url = "https://developer-api.nest.com/"

class API(baseAPI):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.count=1
        self.config = kwargs
        if 'api_config' in kwargs.keys():
            self.device_config=kwargs['api_config']

    def API_info(self):
        return [{'device_model': 'Camera', 'vendor_name': 'Nest', 'communication': 'WiFi', 'support_oauth': True,
                 'device_type_id': 7, 'api_name': 'API_Nestcam', 'html_template': 'others/Nestcam.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable': False, 'is_cloud_device':True,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_ipcam.html'}]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "image", "value": 'nest.jpg'},
                "bottom":None}

    def ontology(self):
        return {'Website_of_last_event': BEMOSS_ONTOLOGY.STREAM, 'Website_of_image_of_last_event': BEMOSS_ONTOLOGY.EVENT_IMAGE_STREAM,
                'Website_of_animated_gif_of_last_event': BEMOSS_ONTOLOGY.ANIMATED_IMAGE_STREAM,'Start_time_of_event':BEMOSS_ONTOLOGY.TIME_START_OF_EVENT,'End_time_of_event':BEMOSS_ONTOLOGY.TIME_END_OF_EVENT,
                'Device_id':BEMOSS_ONTOLOGY.DEVICE_ID,'Time_for_last_change':BEMOSS_ONTOLOGY.TIME_FOR_LAST_CHANGE,'Snapshot':BEMOSS_ONTOLOGY.SNAPSHOT,'software_version':BEMOSS_ONTOLOGY.SOFTWARE,'Structure':BEMOSS_ONTOLOGY.STRUCTURE,
                'Public':BEMOSS_ONTOLOGY.PUBLIC_SHARING,'sound':BEMOSS_ONTOLOGY.SOUND,'motion':BEMOSS_ONTOLOGY.MOTION,'person':BEMOSS_ONTOLOGY.PERSON,'streaming':BEMOSS_ONTOLOGY.IS_STREAMING,'postal':BEMOSS_ONTOLOGY.POSTAL_CODE,
                'country':BEMOSS_ONTOLOGY.COUNTRY_CODE,'latitude':BEMOSS_ONTOLOGY.LATITUDE,'longitude':BEMOSS_ONTOLOGY.LONGITUDE}


    def discover(self,username,password,token):

        responses = list()
        try:
            headers = {'Authorization': 'Bearer {0}'.format(token),
                       'Content-Type': 'application/json'}
            self.initial_response = requests.get('https://firebase-apiserver35-tah01-iad01.dapi.production.nest.com:9553/', headers=headers, allow_redirects=False)
            if self.initial_response.status_code == 307:
                new_url = self.initial_response.headers['Location']
                self.initial_response = requests.get(new_url,headers=headers,allow_redirects=False)
            json_file = self.initial_response.text
            json_response = json.loads(json_file)
            device_ids = json_response['devices']['cameras'].keys()
            for device_id in device_ids:
                mac_address = str(device_id)[:8]
                public_share_url=json_response['devices']['cameras'][device_id]['public_share_url']
                model_name = 'Camera'
                public_url = public_share_url.split("/")
                config=str(device_id)
                embedded_url = public_url[0] + '//' + public_url[2] + '/' + 'embedded' + '/' + public_url[3] + '/' + public_url[4]
                responses.append({'address': embedded_url, 'mac': mac_address,
                                        'model': model_name, 'vendor': "Nest",'config':config})
            return responses
        except Exception as e:
            print (e)
            return responses

    def getDataFromDevice(self):
        activity = {}
        try:
            self.param_details = os.path.expanduser(settings.PROJECT_DIR + '/DeviceAPI/Device_details/camera_information'+self.config["mac_address"]+'.txt')
            if not hasattr(self,"response"):
                token = self.config["token"]
                headers = {'Authorization': 'Bearer {0}'.format(token),
                           'Content-Type': 'application/json'}
                self.initial_response = requests.get('https://firebase-apiserver35-tah01-iad01.dapi.production.nest.com:9553/',
                    headers=headers,allow_redirects=False)
            api_response_dict=dict()
            self.response = self.initial_response.text
            json_response = json.loads(self.response)
            device_ids = json_response['devices']['cameras'].keys()
            for device_id_ in device_ids:
                device_id = ''.join(device_id_)  # for converting the list to string
                if device_id ==self.device_config["config"]:
                    start_time = json_response['devices']['cameras'][device_id]['last_event'][
                    'start_time']  # to get the start time of the last event
                    try:
                        web_url = json_response['devices']['cameras'][device_id]['last_event'].get('web_url') # to get the URL of last event
                        image_url = json_response['devices']['cameras'][device_id]['last_event'].get('image_url') # to get the image of the last event
                        animated_image_url = json_response['devices']['cameras'][device_id]['last_event'].get('animated_image_url') # to get the animated gif of the last event
                        end_time = json_response['devices']['cameras'][device_id]['last_event']['end_time'] # to get the end time of the last event
                    except Exception as e:
                        end_time=start_time
                        print("Event ongoing..")

                    last_is_online_change=json_response['devices']['cameras'][device_id]['last_is_online_change']# to get the last time it was online
                    snapshot_url=json_response['devices']['cameras'][device_id]['snapshot_url'] # to get the snapshot of the camera right now
                    software_version = json_response['devices']['cameras'][device_id]['software_version']# to get the software version of camera
                    structure_id=json_response['devices']['cameras'][device_id]['structure_id'] # to get structure id
                    is_public_share_enabled=json_response['devices']['cameras'][device_id]['is_public_share_enabled'] #to see if public sharing is allowed to not
                    has_sound=json_response['devices']['cameras'][device_id]['last_event']['has_sound']#to see if sound is avaible for last event
                    has_motion = json_response['devices']['cameras'][device_id]['last_event']['has_motion'] # to check if there was motion
                    has_person = json_response['devices']['cameras'][device_id]['last_event']['has_person'] # to check if there was a person there
                    is_streaming= json_response['devices']['cameras'][device_id]['is_streaming']# to see if the device is streaming
                    structure=json_response['structures'].keys()

                    for x in structure:
                        n26=''.join(x)
                        postal=json_response['structures'][n26]['postal_code']
                        country_code = postal + ',' + json_response['structures'][n26]['country_code']
                        address = country_code
                        try:
                            api_key = "AIzaSyBB-ckFDhsDeHTCwG6gfUz-fugY3O3WzMk"
                            api_response = requests.get(
                                'https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}'.format(address,
                                                                                                               api_key))
                            api_response_dict = api_response.json()
                        except Exception as e:
                            print e
                            api_response_dict['status']="NOT OK"

                        if api_response_dict['status'] == 'OK':
                            latitude = api_response_dict['results'][0]['geometry']['location']['lat']
                            longitude = api_response_dict['results'][0]['geometry']['location']['lng']
                        else:
                            latitude='none'
                            longitude='none'
                        activity = {'Website_of_last_event': web_url, 'Website_of_image_of_last_event': image_url,
                                'Website_of_animated_gif_of_last_event': animated_image_url,'Start_time_of_event':start_time,'End_time_of_event':end_time,'Device_id':device_id,'Time_for_last_change':last_is_online_change,
                                'Snapshot':snapshot_url,'software_version':software_version,'Structure':structure_id,'Public':is_public_share_enabled,'sound':has_sound,'motion':has_motion,
                                    'person':has_person,'streaming':is_streaming,'country':country_code,'longitude':longitude,'latitude':latitude} #putting them into dictionary

            with open(self.param_details, 'w') as data:
                data.write(str('Device id: ' + activity['Device_id'] + '\n' + 'Structure id: ' + activity['Structure']  + '\n' +'Software version: ' + activity['software_version']+ '\n'+'Public share status: '+str(activity['Public'])+'\n'+'Streaming status:' +str(activity['streaming'])+'\n'+'Last time camera status changed: '+activity['Time_for_last_change']+'\n'+'Sound detected in last event: '+str(activity['sound'])+'\n'+'Motion detected in last event: '+str(activity['motion'])+'\n'+'Person detected in last event: '+str(activity['person'])+'\n'))
                data.close()

            return activity

        except Exception as e:
            print (e)
            return activity

    def setDeviceStatus(self, postmsg): #postmsg={"status":true}

        device_id = self.config["mac_address"]
        url2 ='https://developer-api.nest.com/devices/cameras/'+device_id
        status=postmsg["status"]
        if status=="ON":
            payload = "{\"is_streaming\": true}"
        else:
            payload = "{\"is_streaming\": false}"
        token = self.config["token"]
        headers = {'Authorization': 'Bearer {0}'.format(token),
                   'Content-Type': 'application/json'}
        initial_response = requests.put(url2, headers=headers, data=payload, allow_redirects=False)
        print(initial_response.text)
        if initial_response.status_code == 307:
            initial_response2 = requests.put(initial_response.headers['Location'], headers=headers,
                                             data=payload,
                                             allow_redirects=False)
            print(initial_response2.text)
        return True

# This main method will not be executed when this class is used as a module
def main():
    # Test code

    # Step1: create an object with initialized data from DeviceDiscovery Agent
    IPCam = API(model='Office Camera', agent_id='basicagent', api='API_Ipcam', address='http://192.168.10.132:8899',
                username="royraj987@gmail.com", password="Ari900_Ari900",mac_address="sgd_Uxlh")
    #J=IPCam.discover()
    #print J
    #J1 = IPCam.getDataFromDevice()
    #print J1


    #t = IPCam.setDeviceStatus({"status":"ON"})
    #print t


if __name__ == "__main__": main()