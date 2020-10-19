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

'''This API class is for an agent that want to discover/communicate/monitor/control
prolon Vav '''
import socket
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from bemoss_lib.protocols.Modbus import connection
import csv
import os
debug = True
_Timeout=15

class API(baseAPI):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.device_supports_auto = True
        if 'address' in kwargs.keys():
            address_parts = kwargs["address"].split(':')
            self.address = address_parts[0]
            self.slave_id =int(address_parts[1])
        self._debug = True

    def API_info(self):

        return [{'device_model': "Network Analyser", 'vendor_name': "ENTES AS", 'communication': 'Modbus',
                 'device_type_id': 5, 'api_name': 'API_ModPowerMeter', 'html_template': 'powermeter/powermeter.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable' : False, 'is_cloud_device': False,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_powermeter.html'},
                ]

    def dashboard_view(self):
        return {"top": BEMOSS_ONTOLOGY.FREQUENCY.NAME,
                "center": {"type": "number", "value": BEMOSS_ONTOLOGY.POWER.NAME, "unit": 'W'},
                "bottom": BEMOSS_ONTOLOGY.VOLTAGE.NAME,"image":"powermeter.png"}

    def ontology(self):
        return {"energy_sum":BEMOSS_ONTOLOGY.ENERGY,"power_sum":BEMOSS_ONTOLOGY.POWER,"power_a":BEMOSS_ONTOLOGY.POWER_L1, "power_b":BEMOSS_ONTOLOGY.POWER_L2,"power_c":BEMOSS_ONTOLOGY.POWER_L3,
            "voltage":BEMOSS_ONTOLOGY.VOLTAGE,"voltage_a":BEMOSS_ONTOLOGY.VOLTAGE_L1,"voltage_b":BEMOSS_ONTOLOGY.VOLTAGE_L2,"voltage_c":BEMOSS_ONTOLOGY.VOLTAGE_L3,"current":BEMOSS_ONTOLOGY.CURRENT,
           "power_factor_a":BEMOSS_ONTOLOGY.POWERFACTOR_L1, "current_a":BEMOSS_ONTOLOGY.CURRENT_L1,"current_b":BEMOSS_ONTOLOGY.CURRENT_L2, "current_c":BEMOSS_ONTOLOGY.CURRENT_L3,
                "power_factor_b":BEMOSS_ONTOLOGY.POWERFACTOR_L2,"power_factor_c":BEMOSS_ONTOLOGY.POWERFACTOR_L3,"frequency":BEMOSS_ONTOLOGY.FREQUENCY,"reac_power":BEMOSS_ONTOLOGY.REACTIVE_POWER,
               "appar_power":BEMOSS_ONTOLOGY.APPARANT_POWER, "powerfactor": BEMOSS_ONTOLOGY.POWERFACTOR ,'reac_power_a':BEMOSS_ONTOLOGY.REACTIVE_POWER_L1,'reac_power_b':BEMOSS_ONTOLOGY.REACTIVE_POWER_L2,
        'reac_power_c':BEMOSS_ONTOLOGY.REACTIVE_POWER_L3,'appar_power_a':BEMOSS_ONTOLOGY.APPARANT_POWER_L1, 'appar_power_b':BEMOSS_ONTOLOGY.APPARANT_POWER_L2,
                'appar_power_c':BEMOSS_ONTOLOGY.APPARANT_POWER_L3}

    def discover(self):
        retry=2

        try:
            device_list = list()
            ip="78.188.64.34"
            _socket = None
            while retry>0:
                try:
                    _socket = socket.create_connection((ip, 502), _Timeout)
                    break
                except socket.error:
                    if _socket:
                        _socket.close()
                    _socket = None
                    retry=retry-1
            if _socket is not None:
                _socket.close()
                slave_id = 1
                client = connection(ip, port=502)
                client.connect()
                result = client.read_device_info(slave_id, object_id=0x01)
                if result is None:
                    result = client.read_device_info(slave_id, object_id=0x00)
                deviceInfo=result.information
                mac = deviceInfo[1]
                model=deviceInfo[4]
                vendor=deviceInfo[0]
                device_list.append({'address': ip + ':' + str(slave_id), 'mac': mac,
                                    'model':model, 'vendor': vendor})
                print device_list
                return device_list
        except Exception as e:
            print e
            return device_list

    def getDataFromDevice(self):

            try:
                Current=list()
                Voltage=list()
                client = connection(self.address, port=502)
                client.connect()
                device_data=dict()
                ratios=client.read_holding_registers(74, 5, unit=self.slave_id)
                CT=ratios.registers[0]
                if CT==0:
                    CT=5
                PT=0.1*ratios.registers[1]
                if PT==0:
                    PT=1
                Pf=ratios.registers[3]
                Powerfactor=0.001*self.getSignedNumber(Pf)
                config_path = os.path.dirname(os.path.abspath(__file__))
                config_path = config_path + "/Modbusdata/powermeter.csv"
                with open(os.path.join(config_path), 'rU') as infile:
                    reader = csv.DictReader(infile)
                    data = {}
                    for row in reader:
                        for header, value in row.items():
                            try:
                                data[header].append(value)
                            except KeyError:
                                data[header] = [value]
                Address= data["Address"]
                Address = map(int, Address)
                Currentlist=data["Current"]
                Description=data["Description"]
                Multiplier=data["Multiplier"]
                Dimension = data["Dimension"]
                Multiplier = map(float, Multiplier)
                Voltagelist=data["Potential"]
                for item in Currentlist:
                    if item=="CT":
                        item=CT
                    Current.append(item)
                    Current = map(int, Current)
                for element in Voltagelist:
                    if element=="PT":
                        element=PT
                    Voltage.append(element)
                    Voltage = map(int, Voltage)
                info=zip(Address,Current,Description,Multiplier,Voltage,Dimension)
                result = client.read_holding_registers(0, 31, unit=self.slave_id)
                for key in self.ontology().keys():
                    #for parameter in info:
                        for add,curr,descip,multi,vol,dimen in info:
                            if key==descip:
                                value=result.registers[add]
                                if dimen=="Signed Int":
                                    value=self.getSignedNumber(value)
                                device_data[descip]=float(curr*vol*multi*(int(value)))
                                break
                device_data["powerfactor"] = Powerfactor
                client.close()
                print device_data
                return device_data

            except Exception as er:
                print "classAPI_ModPowerMeter: ERROR: Reading Modbus registers at getDeviceStatus:"
                print er
                raise

    def getSignedNumber(self,number):
        mask = (2 ** 16) - 1
        if number & (1 << (16 - 1)):
            return number | ~mask
        else:
            return number & mask


def main():
    #Utilization: test methods
    #Step1: create an object with initialized data from DeviceDiscovery Agent
    #requirements for instantiation1. model, 2.type, 3.api, 4. address,
    Network_Analyser = API(model='M1000',type='PowerMeter',api='API_ModPowerMeter',address='78.188.64.34:1')

    #Network_Analyser.getDeviceStatus()

    Network_Analyser.discover()

if __name__ == "__main__": main()