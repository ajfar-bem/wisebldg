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

#__author__ = "Mengmeng Cai"
#__credits__ = ""
#__version__ = "3.5"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2016-11-01"
#__lastUpdated__ = "2016-11-01"
'''

'''This API class is for an agent that want to communicate/monitor/control
devices that compatible with WeMo Socket'''

from DeviceAPI.BaseAPI_Thermostat import BaseAPI_Thermsostat
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import requests
import json
import time



class API(BaseAPI_Thermsostat):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)


    def API_info(self):
        return [{'device_model': 'Virtual', 'vendor_name': 'BEMOSS', 'communication': 'WiFi',
                 'device_type_id': 1, 'api_name': 'API_VirtualThermostat', 'html_template': 'thermostat/thermostat.html',
                 'agent_type': 'BasicAgent', 'identifiable': True, 'authorizable': False, 'is_cloud_device': False, 'support_oauth': False,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True, 'chart_template': 'charts/thermostat.html'},
                ]


    def dashboard_view(self):
        if self.get_variable(BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME) == BEMOSS_ONTOLOGY.THERMOSTAT_MODE.POSSIBLE_VALUES.OFF:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": None, "image":"Thermostat.png"}
        else:
            return {"top": BEMOSS_ONTOLOGY.THERMOSTAT_MODE.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.TEMPERATURE.NAME},
            "bottom": BEMOSS_ONTOLOGY.SETPOINT.NAME, "image":"Thermostat.png"}

    def ontology(self):
        return {"thermostat_mode": BEMOSS_ONTOLOGY.THERMOSTAT_MODE, "thermostat_state": BEMOSS_ONTOLOGY.THERMOSTAT_STATE,
                "fan_mode": BEMOSS_ONTOLOGY.FAN_MODE, "fan_state": BEMOSS_ONTOLOGY.FAN_STATE,
                "cool_setpoint": BEMOSS_ONTOLOGY.COOL_SETPOINT, "heat_setpoint": BEMOSS_ONTOLOGY.HEAT_SETPOINT,
                'setpoint': BEMOSS_ONTOLOGY.SETPOINT, "temperature": BEMOSS_ONTOLOGY.TEMPERATURE,
                "anti_tampering": BEMOSS_ONTOLOGY.ANTI_TAMPERING}

    def getDataFromDevice(self):
        url = self.config['address']
        #url = "https://zdplzczoh8.execute-api.us-east-1.amazonaws.com/beta/DeviceData?device_id="+self.config['agent_id']
        #time.sleep(100)
        response = requests.get(url, timeout=30)
        return json.loads(response.content)

    def setDeviceData(self, postmsg):
        setDeviceDataResult = True
        url = self.config['address']
        # step2: send message to change status of the device
        # url = "https://zdplzczoh8.execute-api.us-east-1.amazonaws.com/beta/DeviceData?device_id=" + self.config[
        #     'agent_id']

        try:
            result = requests.post(url=url,json=postmsg)
        except:
            setDeviceDataResult = False
            raise

        return setDeviceDataResult

    def discover(self,username,password,token):
        return []

def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    VT = API(model='Nest', agent_id='WEMO', api='API', username='nest.bemoss@gmail.com',
               password='VTbemoss2017!', mac_address='fake17584BA76AB1')

    #print(VT.getDeviceStatus())
    #print(VT.variables)
    postmsg = {'temperature':30}
    print(VT.setDeviceStatus(postmsg))
    print(VT.getDeviceStatus())
    print(VT.variables)
    print"Done"

if __name__ == "__main__": main()