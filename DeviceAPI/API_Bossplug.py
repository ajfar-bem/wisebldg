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
#__created__ = "2016-11-01"
#__lastUpdated__ = "2016-11-01"
'''

'''This API class is for an agent that want to communicate/monitor/control
devices that compatible with Boss plugload'''

from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import requests
import settings
import os
import json
from requests.auth import HTTPBasicAuth

BASE = "https://account.bosscontrols.com"
PORTALS = "/api/portals/v1"
ACCOUNTS = "/accounts/"
USERS = "/users/"
USER_PORTALS = "/portals/"
DEVICES="/devices/"
id="1866586558"
DATA_SOURCE="/data-sources/"
MISC="/json"
#myresponse=requests.get('https://account.bosscontrols.com/api/portals/v1/accounts/mkuzlu@vt.edu', auth=HTTPBasicAuth(username, password))


class API(baseAPI):

    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)

        self.device_supports_auto = False
        self.set_variable('offline_count', 0)
        self.set_variable('connection_renew_interval', 6000)  # nothing to renew, right now
        self.param_details = os.path.expanduser(settings.PROJECT_DIR + '/DeviceAPI/Device_details/boss.json')
        if 'username' in kwargs.keys():
            self.username = kwargs['username']
            self.password = kwargs['password']



    def API_info(self):
        return [{'device_model': 'Smart Plug', 'vendor_name': 'BOSS', 'communication': 'Wifi', 'support_oauth' : False,
                 'device_type_id': 3, 'api_name': 'API_Bossplug', 'html_template': 'plugload/plugload.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable': False, 'is_cloud_device': True,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,'chart_template': 'charts/charts_wtplug.html'}]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "image", "value": 'smartplug.png'},
                "bottom": BEMOSS_ONTOLOGY.STATUS.NAME, "image":"smartplug.png"}


    def ontology(self):
        return {"json_relay_req": BEMOSS_ONTOLOGY.STATUS,
                "avg_pwr_5min": BEMOSS_ONTOLOGY.POWER}

    def discover(self,username,password,token=None):

        devicelist = list()
        try:

            id_url=BASE+PORTALS+ACCOUNTS+username
            id_result = requests.get(id_url,auth=HTTPBasicAuth(username, password))  #'https://account.bosscontrols.com/api/portals/v1/accounts/mkuzlu@vt.edu'
            if id_result.status_code==200:
                id=id_result.json()["id"]
                portal_url=BASE+ PORTALS+ USERS +str(id)+ USER_PORTALS
                portal_result = requests.get(portal_url, auth=HTTPBasicAuth(username, password))
                if portal_result.status_code == 200:
                    portal_id=portal_result.json()[0]["PortalID"]
                    portalinfo_url=BASE +PORTALS +USER_PORTALS+str(portal_id)
                    portalinfo_result = requests.get(portalinfo_url, auth=HTTPBasicAuth(username, password))
                    if portalinfo_result.status_code==200:
                        portalinfo=portalinfo_result.json()["devices"]
                        for rid in portalinfo:
                            device_info_url=BASE+ PORTALS+ DEVICES+rid
                            device_info = requests.get(device_info_url, auth=HTTPBasicAuth(username, password))
                            if device_info.status_code == 200:
                                device_details = device_info.json()
                                vendor="BOSS"
                                model = str(device_details["model"])
                                mac=str(device_details["sn"])
                                mac=mac.replace("-","")
                                devicelist.append({'address': rid, 'mac': mac,'model': "Smart Plug", 'vendor': vendor})
                            else:
                                #print ("Device info for given rid not found")
                                pass
                        return devicelist
                    else:
                        #print ("portal info couldn't be found")
                        pass
                else:
                    #print ("portal ID couldn't be found")
                    pass
            else:
                # print ("User ID couldn't be found")
                pass
        except Exception as e:
            #print (e)
            return devicelist


    def getDataFromDevice(self):
        devicedata = {}

        device_variables=["json_relay_req", "avg_pwr_5min"]
        if not hasattr(self,"querydict") or not self.querydict:
            self.first_time=True
            self.querydict=self.getrids(device_variables)
        if self.querydict=={}:
            return devicedata
        for value,rid in self.querydict.iteritems():
            queryurl=BASE+PORTALS+DATA_SOURCE+ rid+MISC#'/data'
            result = requests.get(queryurl, auth=HTTPBasicAuth(self.username, self.password), timeout=20)
            if result.status_code == 200:
                #print result.json()
                param_value = result.json()[0][1]
                try:
                    str_param=str(param_value)
                    json_acceptable_string = str_param.replace("'", "\"")
                    json_param=json.loads(json_acceptable_string)
                    param_value = str(json_param.values()[0]).upper()
                except Exception as e:
                    pass
                devicedata[value]=param_value
        #print (devicedata)
        return devicedata

    def setDeviceStatus(self, postmsg):
        setDeviceStatusResult = True
        send_data=dict()
        try:
            device_variables = ["json_relay_req",]
            querydict = self.getrids(device_variables)
            if querydict == {}:
                setDeviceStatusResult=False
                return setDeviceStatusResult
            value=postmsg["status"].lower()
            send_data["state"]=value
            for value, rid in querydict.iteritems():
                queryurl = BASE + PORTALS + DATA_SOURCE + rid + MISC
                result = requests.post(queryurl, json=send_data, auth=HTTPBasicAuth(self.username, self.password), timeout=20)
                if result.status_code != 201:
                    setDeviceStatusResult = False

        except Exception as er:
            raise
            setDeviceStatusResult = False
        return setDeviceStatusResult

    def getrids(self,device_variables):
        querydict = dict()
        try:
            # try:
            #     with open(self.param_details ,'r') as cokiefile:
            #         read_data=json.load(cokiefile)
            #         if len(read_data)!=0:
            #             for params, rid in read_data.iteritems():
            #                 if params in device_variables:
            #                     querydict[str(params)]=rid
            #             if querydict !={}:
            #                 return querydict
            #             else:
            #                 pass
            #         else:
            #             pass
            # except IOError as er:
            #     if er[0] == 2:  # No such file or directory
            #         pass
            device_info_url = BASE + PORTALS + DEVICES + self.config["address"]
            device_info = requests.get(device_info_url, auth=HTTPBasicAuth(self.username, self.password))
            if device_info.status_code == 200:
                device_details = device_info.json()
                for rid, params in device_details["info"]["aliases"].iteritems():
                    if params[0] in device_variables:
                        querydict[str(params[0])] = rid
                with open(self.param_details, 'w') as f:
                        json.dump(querydict, f)
                return querydict
            else:
                return querydict
        except Exception as e:
            #print e
            return querydict

    def identifyDevice(self):
        identifyDeviceResult = False

        self.toggleDeviceStatus()
        # print(self.get_variable("model") + " is being identified with starting status " + str(
        #     self.get_variable('status')))
        self.timeDelay(15)
        self.toggleDeviceStatus()
        # print("Identification for " + self.get_variable("model") + " is done with status " + str(
        #     self.get_variable('status')))
        identifyDeviceResult = True

        return identifyDeviceResult

    def toggleDeviceStatus(self):
        if self.getDataFromDevice()['json_relay_req'] == "OFF":
            self.setDeviceStatus({"status":"ON"})
        else:
            self.setDeviceStatus({"status":"OFF"})

# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    VeraDevice = API(model='On/Off Switch', api='API_Boss', address="aade9351ffabbf725879474c9db766dee7e102f8",username="mkuzlu@vt.edu",password="Ari900_Ari900")
    #print VeraDevice.discover("mkuzlu@vt.edu","Ari900_Ari900")
    VeraDevice.getDataFromDevice()
    # VeraDevice.setDeviceStatus({'status': 'on'})
    #VeraDevice.getDataFromDevice()
   # VeraDevice.identifyDevice()#

if __name__ == "__main__": main()
