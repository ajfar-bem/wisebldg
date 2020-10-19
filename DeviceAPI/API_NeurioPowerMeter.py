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

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''

'''This API class is for an agent that want to communicate/monitor/control
Neurio single phase power meter devices'''

import json
import time
import neurio
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY

class customized_token_provider(neurio.TokenProvider):

    '''
    This is a TokenProvider class that Neurio library needed to access the token.
    This class allows us use the library using the token we acquired instead of
    providing username and password.
    '''
    def __init__(self, token):
        self.token = token
        print token
        print type(token)

    def get_token(self):
        return self.token

class API(baseAPI):
    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)


        if 'username' in kwargs.keys():
            self.USERNAME = kwargs['username']
            self.PASSWORD = kwargs['password']
            self.address = kwargs.get('address', None)

            self.login(self.USERNAME, self.PASSWORD)
            try:
                user_info = self.Neurio.get_user_information()
                for idx in range(len(user_info['locations'][0]['sensors'])):
                    try:
                        if user_info['locations'][0]['sensors'][idx]['ipAddress'] == self.address:
                            self.sensorId = user_info['locations'][0]['sensors'][idx]['sensorId']
                    except Exception as er:
                        print er
                        print "Error in Neurio API init get sensor Id."
            except:
                print "Error occured in classAPI_NeurioPowerMeter initialization"

        self._debug = True

    def login(self, token):
        try:
            print 'trying to log in...'
            # self.token = neurio.TokenProvider(username, password)
            token = customized_token_provider(token)
            self.Neurio = neurio.Client(token_provider=token)
        except Exception as er:
            print er
            self.Neurio = None
            print('\nLog in failed, please check your credentials!')
            raise

    def API_info(self):
        return [{'device_model': 'HomeEnergyMonitor', 'vendor_name': 'Neurio', 'communication': 'WiFi', 'support_oauth': True,
                'device_type_id': 5,'api_name': 'API_NeurioPowerMeter','html_template': 'powermeter/powermeter1ph.html',
                'agent_type':'BasicAgent','identifiable': False, 'authorizable': False, 'is_cloud_device': True,
                'schedule_weekday_period': 4,'schedule_weekend_period': 4, 'allow_schedule_period_delete': False,
                'chart_template': 'charts/charts_powermeter_neurio.html'}
                ]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "meter", "value": BEMOSS_ONTOLOGY.POWER.NAME, "unit": 'W'},
                "bottom": None,"image":"powermeter.png"}

    def ontology(self):
        return {"power":BEMOSS_ONTOLOGY.POWER, "energy":BEMOSS_ONTOLOGY.ENERGY}

    def discover(self, token, username=None, password=None):
        self.login(token)
        discovered_devices = list()

        try:
            user_info = self.Neurio.get_user_information()
            for sensor in user_info['locations'][0]['sensors']:
                ip_addr = sensor['ipAddress'].encode('utf8')
                mac_addr = sensor['sensorId'].encode('utf8')
                discovered_devices.append({'address': ip_addr, 'mac': mac_addr, 'model': 'HomeEnergyMonitor',
                                           'vendor': 'Neurio'})
        except:
            print "Neurio get user information failed"

        if self._debug:
            print discovered_devices
        return discovered_devices

    def renewConnection(self):
        new_token = None
        # Need to refresh token
        self.login(new_token)
        pass

    # GET Open the URL and read the data
    def getDataFromDevice(self):
        data = self.Neurio.get_samples_live_last(self.sensorId)
        devicedata = {'power': data['consumptionPower']}
        energy = data['consumptionEnergy']/(3600.0*1000.0)
        devicedata['energy'] = float("{0:.2f}".format(energy))
        return devicedata

# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    token = 'AIOO-2ktf59depUK8UeN9qEGpmFQjvZoNZT9ARjCQ9oowlKcuw41fc3dyUnzh-2fCU_oIm-Oa9ifpulS2j2tfLg' \
            '__OpnOGUXuS7qqQoPWlj8i-AKE0FcLbpuhnNbdLhH-QbiBCfAxx5ip_-a3J3W4eWX79FOyK3MjqmLkLSK2A6c1JEMS' \
            'xsBFco9wOO0McvlbTj6Yezm-lkaGFSKaHuoIluR8f0rQDPodFCbmJynj4YlZZKlOD0__CwNAcWOaNmyEre4u1h-AAXG'
    # Neurio = API(username=None, password=None, token=token)
    Neurio = API()
    Neurio.discover(token=token)
    # Neurio.getDeviceStatus()

if __name__ == "__main__": main()
