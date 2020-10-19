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
devices that compatible with Vera Socket or plugload'''

from DeviceAPI.BaseAPI_Vera import baseAPI_Vera
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import urllib2
import json


class API(baseAPI_Vera):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.config = kwargs

    def API_info(self):
        return [{'device_model': 'On_Off Switch', 'vendor_name': 'Vera Control, Ltd.', 'communication': 'Zwave', 'support_oauth': False,
                 'device_type_id': 3, 'api_name': 'API_VeraPlugload', 'html_template': 'plugload/plugload.html',
                 'agent_type': 'BasicAgent', 'identifiable': True, 'authorizable': False, 'is_cloud_device': False,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,'chart_template': 'charts/charts_plugload.html'}]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "image", "value": 'vera_plugload.JPG'},
                "bottom": BEMOSS_ONTOLOGY.STATUS.NAME, "image":"vera_plugload.JPG"}

    def ontology(self):
        return {"status": BEMOSS_ONTOLOGY.STATUS}

    def getDataFromDevice(self):
        devicedata = dict()
        content = self.requireData()
        deviceVeraId = self.config['mac_address'].split('vera')[1]
        for device in content['devices']:
            if str(device['id']) == deviceVeraId:
                devicedata['status'] = BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON if device['status'] == '1' else BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF
        return devicedata

    def setDeviceStatus(self, postmsg):
        setDeviceStatusResult = True
        try:
            deviceVeraId = self.config['mac_address'].split('vera')[1]
            _data = json.dumps(postmsg)
            _data = json.loads(_data)
            status = '1' if _data['status'] == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON else '0'
            url = self.config['address'] + ':3480/data_request?id=lu_action&DeviceNum=' +\
                  deviceVeraId + '&serviceId=urn:upnp-org:serviceId:SwitchPower1&action=SetTarget&newTargetValue='+status
            _deviceUrl = urllib2.urlopen(url, timeout=20)
            if _deviceUrl.getcode()!=200:
                setDeviceStatusResult = False
        except Exception as er:
            print er
            setDeviceStatusResult = False
        return setDeviceStatusResult


# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    VeraDevice = API(model='On/Off Switch', api='API_Vera', mac_address = '50008574vera10', address='http://192.168.10.204')
    # VeraDevice.discover()
    # VeraDevice.setDeviceStatus({'status': 'OFF'})
    VeraDevice.identifyDevice()

if __name__ == "__main__": main()