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
#__created__ = "2016-12-05 12:04:50"
#__lastUpdated__ = "2016-12-05 11:23:33"
'''

'''This API class is for an agent that want to discover/communicate/monitor/
eGauge Powermeter '''

from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import requests
import urllib
import settings
debug = True
from HTMLParser import HTMLParser
import time
from xml.dom import minidom
attributes={}
attributesfreq={}
attributespow={}
attributesrea={}
attributesv={}
attributesi={}
db_table_supported_devices = settings.DATABASES['default']['TABLE_supported_devices']
attributest={}
attributespa={}
attributesh={}
attributesee={}
attributesi={}
attributess={}




class API(baseAPI):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.device_supports_auto = True
        #self.address=address
        self._debug = False

    def API_info(self):

        return [{'device_model': "EG30x787x", 'vendor_name': "Egauge", 'communication': 'WiFi',
                 'device_type_id': 5, 'api_name': 'API_eGaugePM', 'html_template': 'powermeter/powermeter.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable' : False, 'is_cloud_device': False,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_powermeter.html'},
                ]

    def dashboard_view(self):
        return {"top": None,
                "center": {"type": "number", "value": "power", "unit": 'W'},
                "bottom": None, "image":"powermeter.png"}

    def ontology(self):
        return {"Total Usage":BEMOSS_ONTOLOGY.ENERGY,"PowerSum":BEMOSS_ONTOLOGY.POWER,"PowerA":BEMOSS_ONTOLOGY.POWER_L1,"PowerB":BEMOSS_ONTOLOGY.POWER_L2,"PowerC":BEMOSS_ONTOLOGY.POWER_L3,
                "VoltageAvg":BEMOSS_ONTOLOGY.VOLTAGE,"VoltA":BEMOSS_ONTOLOGY.VOLTAGE_L1,"VoltB":BEMOSS_ONTOLOGY.VOLTAGE_L2,"VoltC":BEMOSS_ONTOLOGY.VOLTAGE_L3,
                "Freq":BEMOSS_ONTOLOGY.FREQUENCY,"PowerFactorAvg":BEMOSS_ONTOLOGY.POWERFACTOR,"PowerFactorA":BEMOSS_ONTOLOGY.POWERFACTOR_L1,
                "PowerFactorB":BEMOSS_ONTOLOGY.POWERFACTOR_L2,"PowerFactorC":BEMOSS_ONTOLOGY.POWERFACTOR_L3,"PowerSumReactive":BEMOSS_ONTOLOGY.REACTIVE_POWER,
                "CurrentA":BEMOSS_ONTOLOGY.CURRENT_L1,"CurrentB":BEMOSS_ONTOLOGY.CURRENT_L2,"CurrentC":BEMOSS_ONTOLOGY.CURRENT_L3  }

    def discover(self,address,model,token=None):

        responses = list()
        try:

            address='http://'+address+'/cgi-bin/egauge?inst'
            r = requests.get(
                url=address,
                params="tot"
            )
            device_data = self.getDeviceInfoXML(r.content)
            number_of_power_meters=len ([1 for s in device_data.keys() if s.startswith('PowerSum')])  #counting number of power meters; single power for each meter

            for i in range(1,number_of_power_meters+1):
                mac=address[13:]
                mac=mac.split(".")[0]+'_'+str(i)

                responses.append({'address': address+'_'+str(i), 'mac': mac,
                                  'model': model, 'vendor': 'Egauge'})

            return responses
        except Exception as e:
            #print e
            return responses

    def getDataFromDevice(self):
        full_address = self.config["address"]
        #remove the device Id appended at the end of the address by the discovery function
        split_address = full_address.split('_')
        meter_id = split_address[-1]
        correct_address = '_'.join(split_address[:-1])

        r = requests.get(
            url=correct_address,
            params="tot"
            )

        if r.status_code == 200:  # 200 means successfully
            devicedata=self.getDeviceInfoXML(r.content,meter_id=meter_id)

            #need to calculate: VoltageAvg, PowerFactorA, PowerFactorB, PowerFactorC, PowerFactorAvg, PowerSumReactive
            devicedata['VoltageAvg'] = (devicedata['VoltA'] + devicedata['VoltB'] + devicedata['VoltC'])/3.0

            PowerSumReactive = 0
            for mId in ['A','B','C']:
                ApparentPower = devicedata['Volt'+mId] * devicedata['Current'+mId]
                RealPower = devicedata['Power'+mId]
                PowerSumReactive +=  (ApparentPower**2-RealPower**2)**0.5 if ApparentPower> RealPower else 0
                devicedata['PowerFactor'+mId] = abs(RealPower/ApparentPower)

            devicedata['PowerFactorAvg'] = (devicedata['PowerFactorA'] + devicedata['PowerFactorB'] + devicedata['PowerFactorC'])/3.0
            devicedata['PowerSumReactive'] = PowerSumReactive

            return devicedata
        else:
            raise Exception('Bad status code response from server')



    def getDeviceInfoXML(self, data,meter_id=None):
        # Use the dom module to load xml data into a dictionary
        try:
            #print data
            xmldata = minidom.parseString(data)
            registers = xmldata.getElementsByTagName('r')
            device_data = dict()
            for reg in registers:
                val = reg.getElementsByTagName('i')[0]
                name = reg.attributes['n'].value

                if meter_id: #if filtering by meter_id is desired
                    split_name = name.split('_')
                    if len(split_name)>1 and split_name[-1] != meter_id: #if the register is for specific meter_id (it has a
                        # underscore ID in its name, and if the meter_id doesn't match passed meter id, ignore this register
                        continue
                    name = split_name[0]

                device_data[name] = float(val.firstChild.nodeValue)

            return device_data
        except Exception as e:
            raise


def main():
    Power_meter = API(model='Egauge',type='PowerMeter',api='API_eGaugePM',address='http://egauge32207.local/cgi-bin/egauge?inst_1')
    print(Power_meter.getDeviceStatus())
    Power_meter.discover(address='egauge32207.local',model='eGauge')
    print("dsfih")
    #Power_meter.discover('egauge32207.egaug.es',"egauge")

if __name__ == "__main__": main()
