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
import urllib2
import json
from BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY

debug=True
class API(baseAPI):

    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)
        self.set_variable('offline_count', 0)
        self.set_variable('connection_renew_interval', 6000)  # nothing to renew, right now

        if 'username' in kwargs.keys():
            self.USERNAME = kwargs['username']
            self.PASSWORD = kwargs['password']

    def API_info(self):
        return [{'device_model': 'VTmodel', 'vendor_name': 'Tumalow Energy Ingenuity', 'communication': 'WiFi', 'support_oauth' : False,
                 'device_type_id': 6, 'api_name': 'API_BatteryStorage', 'html_template': 'der/batterystorage.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable' : False, 'is_cloud_device': False,
                  'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_der.html'},]

    def dashboard_view(self):
        if self.get_variable(BEMOSS_ONTOLOGY.STATUS.NAME) == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON:
            return {"top": BEMOSS_ONTOLOGY.STATUS.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.BATTERY.NAME},
            "bottom": BEMOSS_ONTOLOGY.POWER.NAME, "image":"Battery.png"}
        else:
            return {"top": BEMOSS_ONTOLOGY.STATUS.NAME, "center": {"type": "number", "value": BEMOSS_ONTOLOGY.BATTERY.NAME},
            "bottom": BEMOSS_ONTOLOGY.POWER.NAME,"image":"Battery.png"}

    def ontology(self):
        return {"status": BEMOSS_ONTOLOGY.STATUS, "output": BEMOSS_ONTOLOGY.POWER, "soc": BEMOSS_ONTOLOGY.BATTERY}

    def discover(self):
        responses = list()
        _urlData = 'http://38.68.251.227:39999/current/status/VaTech/1021Prince/d687f78d-8327-44aa-ae28-1e00bbbbc174'
        try:
            _deviceUrl = urllib2.urlopen(_urlData, timeout=20)
            if _deviceUrl.getcode() == 200:
                responses.append({'address': "http://38.68.251.227:39999", 'mac': "12345",
                                            'model': "VTmodel", 'vendor': 'Tumalow Energy Ingenuity'})
                return responses
            else:
                return responses
        except:
            return responses


    def renewConnection(self):
        pass


    # 2. Attributes from Attributes table
    '''
    Attributes:
     ------------------------------------------------------------------------------------------
    status            GET    POST      Battery storage ON/OFF status
    output            GET    POST      Voltage output
    soc               GET    POST      State of charge

     ------------------------------------------------------------------------------------------
    '''

    # 3. Capabilites (methods) from Capabilities table
    '''
    API3 available methods:
    1. getDataFromDevice() GET

    '''
    # ----------------------------------------------------------------------
    # getDeviceStatus(), getDeviceStatusJson(data), printDeviceStatus()
    def getDataFromDevice(self):


        _urlData = self.config['address']+'/current/status/VaTech/1021Prince/d687f78d-8327-44aa-ae28-1e00bbbbc174'
        try:
            _deviceUrl = urllib2.urlopen(_urlData, timeout=20)
            if _deviceUrl.getcode() == 200:
                jsonResult = _deviceUrl.read().decode("utf-8")
                _theJSON=dict()
                _theJSON = json.loads(jsonResult)
                if self._debug: print _theJSON
                devicedata = {"output": float(_theJSON["output"]), "soc": (float(_theJSON["soc"]))*(100.0/12) }
                if _theJSON["status"] == "operational":
                    devicedata["status"] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON
                else:
                    devicedata["status"] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF

                print devicedata
                return devicedata

            else:
                return None
        except Exception as er:
            raise

# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    BatteryStorage = API(model='Tumalow Energy Ingenuity', type='BatteryStorage', api='classAPI_BatteryStorage', address="http://38.68.251.227:39999",
                         agent_id='BatteryStorage')
    print("{0}agent is initialzed for {1} using API={2} at {3}".format(BatteryStorage.get_variable('type'),
                                                                       BatteryStorage.get_variable('model'),
                                                                       BatteryStorage.get_variable('api'),
                                                                       BatteryStorage.get_variable('address')))

    #BatteryStorage.getDeviceStatus()
    BatteryStorage.discover()


if __name__ == "__main__": main()