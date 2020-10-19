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
devices that compatible with Radio Thermostat Wi-Fi USNAP Module API Version 1.3 March 22, 2012
http://www.radiothermostat.com/documents/rtcoawifiapiv1_3.pdf'''
from bemoss_lib.protocols.Modbus import connection
import urllib2
import json
import requests
import csv
import os
import datetime
from urlparse import urlparse
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
Scale_factors={"Accurrent":0.01,"Acvoltage":0.01 ,"Acpower":1.0,"Frequency":0.01,"ApparantPower":1.0,"Energy":1,"ReactivePower":0.01, "Powerfactor":0.0001,"Dccurrent":0.02,"Dcvoltage":0.01,"Dcpower":1.0,
               "set_power":0.01,"set_pf":0.1,"set_reac":0.01}
class API(baseAPI):
    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)
        self.set_variable('Area_array', 40.88)
        self._debug = False
        self.slave_id=1
        self.address=self.config["address"]

    def API_info(self):
        return [{'device_model' : 'Fronius Primo 6.0-1 208-240', 'vendor_name' : 'Fronius', 'communication' : 'WiFi',
                'device_type_id' : 6,'api_name': 'API_Fronius','html_template':'der/solar.html',
                'agent_type':'BasicAgent','identifiable' : False, 'authorizable': False, 'is_cloud_device' : False,
                'schedule_weekday_period' : 4,'schedule_weekend_period' : 4, 'allow_schedule_period_delete' : False,
                'chart_template': 'charts/charts_solar.html'}]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "meter", "value": BEMOSS_ONTOLOGY.POWER_AC.NAME, "unit": 'W'},
                "bottom": BEMOSS_ONTOLOGY.VOLTAGE_AC.NAME,"image":"PV.png"}

    def ontology(self):
        return {"Vdc":BEMOSS_ONTOLOGY.VOLTAGE_DC, "Idc":BEMOSS_ONTOLOGY.CURRENT_DC,
                "Vac":BEMOSS_ONTOLOGY.VOLTAGE_AC, "Iac":BEMOSS_ONTOLOGY.CURRENT_AC,
                "Pac":BEMOSS_ONTOLOGY.POWER_AC, "Pdc":BEMOSS_ONTOLOGY.POWER_DC,
                "Irradiance_array":BEMOSS_ONTOLOGY.ARRAY_IRRADIANCE, "Irradiance_horizontal":BEMOSS_ONTOLOGY.HORIZONTAL_IRRADIANCE,
                "Temp_ambient":BEMOSS_ONTOLOGY.AMBIENT_TEMPERATURE, "Temp_module":BEMOSS_ONTOLOGY.MODULE_TEMPERATURE,
                "Wind_velocity":BEMOSS_ONTOLOGY.WIND_VELOCITY, "Energy_total":BEMOSS_ONTOLOGY.ENERGY_TOTAL,
                "Energy_day":BEMOSS_ONTOLOGY.ENERGY_DAY, "Power_incident":BEMOSS_ONTOLOGY.INCIDENT_POWER,
                "Efficiency_inverter":BEMOSS_ONTOLOGY.INVERTER_EFFICIENCY,
                "Efficiency_solar":BEMOSS_ONTOLOGY.SOLAR_EFFICIENCY,
                "Efficiency_total": BEMOSS_ONTOLOGY.TOTAL_EFFICIENCY, "CO2_saved":BEMOSS_ONTOLOGY.CO2_SAVED,
                "set_power": BEMOSS_ONTOLOGY.POWER_LIMIT,"set_pf":BEMOSS_ONTOLOGY.PFLIMIT,"set_reac": BEMOSS_ONTOLOGY.REACTIVE_POWER_LIMIT,
                "power_control":BEMOSS_ONTOLOGY.POWER_CONTROL,"pf_control":BEMOSS_ONTOLOGY.PF_CONTROL,"reac_control":BEMOSS_ONTOLOGY.REAC_CONTROL,
                "powerfactor": BEMOSS_ONTOLOGY.POWERFACTOR,
                }

    def discover(self,address,model,token=None):
        discovered_devices = list()
        device_address=address
        # TODO: Remove Hardcoded address, create a page on UI for user to input relevant information.
        discovered_devices.append({'address': device_address, 'mac': '0040AD28612F', 'model': model,
                                      'vendor': 'Fronius'})
        return discovered_devices

    def postJSONtosolar(self, _urlData):
        _communication_success=True
        try:
            _f = requests.get(_urlData, timeout=10)

            if (_f.status_code == 200):
                content = _f.content.replace('\xb0', '')
                content = content.replace('\xb2', '')
                _response = json.loads(content)
                return _response['Body']['Data']
            else:
                _communication_success=False
        except Exception as er:
            _communication_success=False
            raise
            #raise Exception('Communication failure with solar '+str(er))

    def getSignedNumber(self, number):
            mask = (2 ** 16) - 1
            if number & (1 << (16 - 1)):
                return number | ~mask
            else:
                return number & mask
    # GET Open the URL and read the data
    def getDataFromDevice(self):

        _urlInverter = 'http://'+self.address + '/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData'
        _urlMeteor = 'http://'+self.config["address"] + '/solar_api/v1/GetSensorRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=NowSensorData'
        _responseInverter = self.postJSONtosolar(_urlInverter)
        _responseMeteor = self.postJSONtosolar(_urlMeteor)

        if (_responseInverter != 0) & (_responseMeteor != 0):
            return self.getDeviceStatusJson(_responseInverter, _responseMeteor)  # convert string data to JSON object
        else:
            raise Exception("classAPI_FroniusSolar: ERROR: getdevicestatus couldn't get data")

    def getDeviceStatusJson(self, _response1, _response2):
        # Use the json module to load the string data into a dictionary
        device_data = dict()

        conv_dict = {'UDC': 'Vdc', 'IDC': 'Idc', 'UAC': 'Vac', 'IAC': 'Iac', 'PAC': 'Pac',
                     '2': 'Irradiance_array', '1': 'Temp_ambient', '0': 'Temp_module',
                     '4': 'Wind_velocity', 'TOTAL_ENERGY': 'Energy_total', 'DAY_ENERGY': 'Energy_day'}

        _response1.update(_response2)
        for parameter in _response1.keys():
            if parameter in conv_dict.keys():
                device_data[conv_dict[parameter]] = float(_response1[parameter]['Value'])

        for var in ['Vdc','Vac','Iac','Idc','Irradiance_array']:
            if var not in device_data:
                device_data[var] = 0



        device_data['Energy_total'] = float('%.2f' % (device_data['Energy_total'] / 1000000.0))
        # emission factors used: 7.03 × 10-4 metric tons CO2 / kWh
        # https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references
        device_data['CO2_saved'] = float('%.2f' % (device_data['Energy_total'] * 0.703 * 2204.62))
        device_data['Energy_day'] = float('%.2f' % (device_data['Energy_day'] / 1000.0))
        device_data['Power_incident'] = float('%.2f' % (device_data['Irradiance_array'] * self.get_variable('Area_array')))

        device_data['Pdc'] = float('%.2f' % (device_data['Vdc'] * device_data['Idc']))
        if device_data['Power_incident'] <= 0.1:
            device_data['Efficiency_solar'] = 0.0
            device_data['Efficiency_inverter'] = 0.0
            device_data['Efficiency_total'] = 0.0
        else:
            device_data['Efficiency_solar'] = float('%.2f' % ((device_data['Pdc'] / device_data['Power_incident']) * 100))
            if device_data['Pdc'] <= 0.1:
                device_data['Efficiency_inverter'] = 0.0
            else:
                device_data['Efficiency_inverter'] = float('%.2f' % ((device_data['Pac'] / device_data['Pdc']) * 100))
                device_data['Efficiency_total'] = float('%.2f' % ((device_data['Efficiency_solar'] * device_data['Efficiency_inverter']) / 100))
        client = connection(self.address, port=502)
        name = "inverter"
        return_data = dict()
        client.connect()
        if not hasattr(self,"data"):
            config_path = os.path.dirname(os.path.abspath(__file__))
            config_path = config_path + "/Modbusdata/" + name + ".csv"
            with open(os.path.join(config_path), 'rU') as infile:
                reader = csv.DictReader(infile)
                data = {}
                for row in reader:
                    for header, value in row.items():
                        try:
                            data[header].append(value)
                        except KeyError:
                            data[header] = [value]
            self.data=data
        device_count = self.data["Type"]
        device_map = self.duplicates_indices(device_count)
        for device, values in device_map.iteritems():

            if device == "configvalues":
                config_data = self.collectdata(client, values, 40232, 18)
                for k, v in config_data.iteritems():
                    device_data[k]=v

        #print device_data
        return device_data

    def collectdata(self,client,values,start,stop):

        data=self.data
        device_data=dict()
        result = client.read_holding_registers(start,stop , unit=self.slave_id)
        for value in values:
            value = int(value)
            variable = data["Description"][value]
            if variable in self.ontology().keys():

                temp_value = result.registers[int(data["Address"][value])]
                if data["Dimension"][value] == "uint16":
                    temp_value = self.getSignedNumber(temp_value)
                if data["NeedsScale"][value]=='1':
                    scale = Scale_factors[data["MultiplierType"][value]]
                    final_value=temp_value*scale
                else:
                    final_value=temp_value
                if type(final_value)==int or type(final_value)==str:
                    device_data[variable] = final_value
                else:
                    device_data[variable] = round(final_value, 2)
        result = client.read_holding_registers(40091, 1, unit=self.slave_id)
        temp_value = result.registers[0]
        temp_value = self.getSignedNumber(temp_value)
        scale = 0.0001
        power_factor = round(temp_value * scale,2)
        device_data["powerfactor"]=power_factor
        client.close()
        return device_data

    def setDeviceData(self, postmsg):
        try:
            client = connection(self.address,port=502)
            client.connect()
            if BEMOSS_ONTOLOGY.POWER_LIMIT.NAME in postmsg.keys():
                result2 = client.write_register(40236, 1, unit=self.slave_id)
                result1=client.write_register(40232,postmsg.get('power_limit')*100,unit=self.slave_id)

            if BEMOSS_ONTOLOGY.PFLIMIT.NAME in postmsg.keys():
                result3=client.write_register(40237,postmsg.get('pf_limit')*10,unit=self.slave_id)
                result4=client.write_register(40241, 1, unit=self.slave_id)
            if BEMOSS_ONTOLOGY.REACTIVE_POWER_LIMIT.NAME in postmsg.keys():
                client.write_register(40243,int((postmsg.get('set_reac'))*100),unit=self.slave_id)
                client.write_register(40249, 1, unit=self.slave_id)
            client.close()
            return True
        except Exception as e:
            raise


# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    FroniusSolar = API(model='FroniusSolar', agent_id='solarpvagent1', api='API', address='38.68.237.248')
    FroniusSolar.getDeviceStatus()

if __name__ == "__main__": main()
