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
Fronius inverter '''
import socket
import json
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.protocols.Modbus import connection
from collections import defaultdict, Counter
import numpy as np
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import csv
import os
#rom DeviceAPI import ModbusAPI
debug = True
_Timeout=1
import requests
Scale_factors={"Accurrent":0.01,"Acvoltage":0.01 ,"Acpower":1.0,"Frequency":0.01,"ApparantPower":1.0,"Energy":1,"ReactivePower":0.01, "Powerfactor":0.0001,"Dccurrent":0.02,"Dcvoltage":0.01,"Dcpower":1.0,
               "set_power":0.01,"set_pf":0.1,"set_reac":0.01}

operation_mode={1:"Off",
2:"In operation (no feed-in)",
3: "Run-up phase",
4:" Normal operation",
5: "Power reduction",
6: "Switch-off phase",
7: "Error exists",
8: "Standby"}


class API(baseAPI):

    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.set_variable('connection_renew_interval', 6000)
        self.device_supports_auto = True
        if 'address' in self.variables.keys():
            address_parts = self.config["address"].split(':')
            self.address = address_parts[0]
            self.slave_id =int(address_parts[1])
        self._debug = True



    def API_info(self):

        return [{'device_model': "IG150V", 'vendor_name': "Fronius", 'communication': 'Modbus',
                 'device_type_id': 6, 'api_name': 'FroniusInverter', 'html_template': 'others/inverter.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable' : False, 'is_cloud_device': False,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_solar.html'},
                ]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "meter", "value": BEMOSS_ONTOLOGY.POWER_AC.NAME, "unit": 'W'},
                "bottom": None}

    def ontology(self):
        return {"power_ac":BEMOSS_ONTOLOGY.POWER_AC,"voltage_ac":BEMOSS_ONTOLOGY.VOLTAGE_AC,"current_ac":BEMOSS_ONTOLOGY.CURRENT_AC,
               "frequency":BEMOSS_ONTOLOGY.FREQUENCY, "powerfactor": BEMOSS_ONTOLOGY.POWERFACTOR ,'reac_power':BEMOSS_ONTOLOGY.REACTIVE_POWER,'appar_power':BEMOSS_ONTOLOGY.APPARANT_POWER,
                "current_dc":BEMOSS_ONTOLOGY.CURRENT_DC,"voltage_dc":BEMOSS_ONTOLOGY.VOLTAGE_DC,"power_dc":BEMOSS_ONTOLOGY.POWER_DC,"set_power":BEMOSS_ONTOLOGY.POWER_LIMIT,
                "set_pf":BEMOSS_ONTOLOGY.PFLIMIT,"set_reac": BEMOSS_ONTOLOGY.REACTIVE_POWER_LIMIT,"power_control":BEMOSS_ONTOLOGY.POWER_CONTROL,"pf_control":BEMOSS_ONTOLOGY.PF_CONTROL,"reac_control":BEMOSS_ONTOLOGY.REAC_CONTROL,
                "efficiency":BEMOSS_ONTOLOGY.SOLAR_EFFICIENCY,"operation_mode":BEMOSS_ONTOLOGY.OPERATION_MODE, "Irradiance_array":BEMOSS_ONTOLOGY.ARRAY_IRRADIANCE, "Power_incident":BEMOSS_ONTOLOGY.INCIDENT_POWER,
               "Vdc":BEMOSS_ONTOLOGY.VOLTAGE_DC, "Idc":BEMOSS_ONTOLOGY.CURRENT_DC,"Vac":BEMOSS_ONTOLOGY.VOLTAGE_AC, "Iac":BEMOSS_ONTOLOGY.CURRENT_AC,"Pac":BEMOSS_ONTOLOGY.POWER_AC, "Pdc":BEMOSS_ONTOLOGY.POWER_DC,
                "Irradiance_horizontal":BEMOSS_ONTOLOGY.HORIZONTAL_IRRADIANCE, "Temp_ambient":BEMOSS_ONTOLOGY.AMBIENT_TEMPERATURE, "Temp_module":BEMOSS_ONTOLOGY.MODULE_TEMPERATURE,
                "Wind_velocity":BEMOSS_ONTOLOGY.WIND_VELOCITY, "Energy_total":BEMOSS_ONTOLOGY.ENERGY_TOTAL,"Energy_day":BEMOSS_ONTOLOGY.ENERGY_DAY, "efficiency_inverter":BEMOSS_ONTOLOGY.INVERTER_EFFICIENCY,
                "efficiency_solar":BEMOSS_ONTOLOGY.SOLAR_EFFICIENCY,"efficiency_total": BEMOSS_ONTOLOGY.TOTAL_EFFICIENCY, "CO2_saved":BEMOSS_ONTOLOGY.CO2_SAVED,"Area_array":BEMOSS_ONTOLOGY.ARRAY_AREA
                }

    def discover(self,address,model,token=None):
        retry=5
        device_list = list()
        try:
            device_list = list()
            ip=address                #"38.68.237.248"
            _socket = None
            while retry>0:
                #print retry
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
                client = connection(ip, port=502)
                client.connect()
                possible_slave_ids = [1]
                for slave_id in possible_slave_ids:
                    result3 = client.read_holding_registers(40003, 1, unit=slave_id)
                    if result3 is not None:
                        device_list.append({'address': ip + ':' + str(slave_id), 'mac': "23342",
                                         'model':model, 'vendor': "Fronius"})
                    print device_list
            return device_list
        except Exception as e:
            print e
            return device_list


    def getDataFromDevice(self):

            try:

                name="old_inverter"
                result=self.getData(name)
                return result

            except Exception as er:
                print "classAPI_froniusInverter: ERROR: Reading Modbus registers at getDeviceStatus:"
                print er

                return None

    def getData(self,name):
        try:
            device_data = list()
            try:
                client = connection(self.address, port=502)
                return_data=dict()
                client.connect()
                config_path = os.path.dirname(os.path.abspath(__file__))
                config_path = config_path + "/Modbusdata/"+ name+".csv"
                with open(os.path.join(config_path), 'rU') as infile:
                    reader = csv.DictReader(infile)
                    data = {}
                    for row in reader:
                        for header, value in row.items():
                            try:
                                data[header].append(value)
                            except KeyError:
                                data[header] = [value]
                device_count = data["Type"]
                device_map = self.duplicates_indices(device_count)
                for device, values in device_map.iteritems():
                    if device=="acvalues":
                        ac_data=self.collectdata(client,data,values,40071,40)
                       # if(ac_data["power_ac"]>3*ac_data["voltage_ac"]*ac_data["current_ac"]):
                            #constant=float(ac_data["power_ac"])/ac_data["appar_power"]
                            #ac_data["power_dc"] = round(ac_data["power_dc"]/10, 2)
                            #ac_data["appar_power"]=round(ac_data["voltage_ac"]*ac_data["current_ac"],2)
                           # ac_data["power_ac"] = round(ac_data["voltage_ac"] * ac_data["current_ac"]*constant,2)
                        device_data.append(ac_data)
                    if device == "dcvalues":
                        dc_data = self.collectdata(client, data, values, 40272, 9)
                        device_data.append(dc_data)
                    if device == "configvalues":
                        config_data = self.collectdata(client, data, values, 40232, 18)
                        device_data.append(config_data)
            except Exception as e:
                print e

            getweatherdata=self.getweatherdata()
            device_data.append(getweatherdata)
            for d in device_data:
                for k, v in d.iteritems():
                    return_data[k]=v
           # return_data["voltage_dc"]=round(float(return_data["power_dc"])/return_data["current_dc"],2)
            if return_data["power_dc"]!=0 and return_data['Power_incident']!=0:
                return_data["efficiency_inverter"]=round(100*float(return_data["power_ac"])/return_data["power_dc"],2)
                return_data['efficiency_solar'] = float('%.2f' % ((return_data['power_dc'] / return_data['Power_incident']) * 100))
                return_data['efficiency_total'] = float('%.2f' % ((return_data['efficiency_solar'] * return_data['efficiency_inverter']) / 100))
                if (return_data["appar_power"] > 2 * return_data["power_ac"]):
                    return_data["appar_power"]=round(float(return_data["appar_power"])/10,2)
            print return_data
            return return_data
        except Exception as e:
            print e
            client.close()
            return None

    def collectdata(self,client,data,values,start,stop):

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
                elif variable=="operation_mode":
                    final_value=operation_mode[temp_value]
                else:
                    final_value=temp_value
                if type(final_value)==int or type(final_value)==str:
                    device_data[variable] = final_value
                else:
                    device_data[variable] = round(final_value, 2)
        client.close()
        return device_data


    def postJSONtosolar(self, _urlData):
        _communication_success=True
        try:
            _f = requests.get(_urlData, timeout=10)

            if (_f.status_code == 200):
                _response = json.loads(_f.content)
                return _response['Body']['Data']
            else:
                _communication_success=False
        except:
            _communication_success=False

        if _communication_success==False:
            print ("classAPI_FroniusSolar: ERROR: Couldn't communicate to server")
            return 0

    # GET Open the URL and read the data
    def getweatherdata(self):
        try:
            _urlInverter = 'http://'+self.address + '/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=CommonInverterData'
            _urlMeteor = 'http://'+self.address + '/solar_api/v1/GetSensorRealtimeData.cgi?Scope=Device&DeviceId=1&DataCollection=NowSensorData'
            _responseInverter = self.postJSONtosolar(_urlInverter)
            _responseMeteor = self.postJSONtosolar(_urlMeteor)

            if (_responseInverter != 0) & (_responseMeteor != 0):
                return self.getDeviceStatusJson(_responseInverter, _responseMeteor)  # convert string data to JSON object
            else:
                print ("classAPI_FroniusSolar: ERROR: getdevicestatus couldn't get data")
                return {}

        except Exception as er:
            print ("classAPI_FroniusSolar: ERROR: getdevicestatus couldn't get data")
            print "Error Occured while getting device status: " + str(er)
            return {}

    def getDeviceStatusJson(self, _response1, _response2):
        # Use the json module to load the string data into a dictionary
        device_data = dict()

        conv_dict = {'IDC': 'current_dc', 'UDC': 'voltage_dc','PAC': 'power_ac',
                     '2': 'Irradiance_array', '1': 'Temp_ambient', '0': 'Temp_module',
                     '4': 'Wind_velocity', 'TOTAL_ENERGY': 'Energy_total', 'DAY_ENERGY': 'Energy_day'}

        _response1.update(_response2)
        for parameter in _response1.keys():
            if parameter in conv_dict.keys():
                device_data[conv_dict[parameter]] = float(_response1[parameter]['Value'])

        device_data['Energy_total'] = float('%.2f' % (device_data['Energy_total'] / 1000000.0))
        # emission factors used: 7.03 × 10-4 metric tons CO2 / kWh
        # https://www.epa.gov/energy/ghg-equivalencies-calculator-calculations-and-references
        device_data['CO2_saved'] = float('%.2f' % (device_data['Energy_total'] * 0.703 * 2204.62))
        device_data['Energy_day'] = float('%.2f' % (device_data['Energy_day'] / 1000.0))
        device_data['Area_array'] = 40.88
        device_data['power_dc'] = float('%.2f' % (device_data['current_dc'] * device_data['voltage_dc']))
        device_data['Power_incident'] = float('%.2f' % (device_data['Irradiance_array'] *device_data['Area_array'] ))
        return device_data

    def getSignedNumber(self,number):
        mask = (2 ** 16) - 1
        if number & (1 << (16 - 1)):
            return number | ~mask
        else:
            return number & mask

    def setDeviceData(self, postmsg):
        try:
            client = connection(self.address,port=502)
            client.connect()
            if BEMOSS_ONTOLOGY.POWER_LIMIT.NAME in postmsg.keys():
                result1=client.write_register(40232,postmsg.get('power_limit')*100,unit=self.slave_id)
               # result2=client.write_register(40236, 1, unit=self.slave_id)
            if BEMOSS_ONTOLOGY.PFLIMIT.NAME in postmsg.keys():
                result3=client.write_register(40237,postmsg.get('pf_limit')*10,unit=self.slave_id)
                result4=client.write_register(40241, 1, unit=self.slave_id)
            if BEMOSS_ONTOLOGY.REACTIVE_POWER_LIMIT.NAME in postmsg.keys():
                client.write_register(40243,int((postmsg.get('set_reac'))*100),unit=self.slave_id)
                client.write_register(40249, 1, unit=self.slave_id)
            client.close()
            return True
        except Exception as e:
            print e
            try:
                client.close()
                return False
            except:
                print('Modbus TCP client was not built successfully at the beginning')
                return False

def main():
    #Utilization: test methods
    #Step1: create an object with initialized data from DeviceDiscovery Agent
    #requirements for instantiation1. model, 2.type, 3.api, 4. address,
    Network_Analyser = API(type='PowerMeter',address='38.68.237.248:1')
    #v_c_scale=Network_Analyser.getSignedNumber(65534)
    #print v_c_scale
    #Network_Analyser.discover()
    #Network_Analyser.getweatherdata()
    #Network_Analyser.setDeviceData({'power_limit':100,'pf_limit':96})
    Network_Analyser.getDataFromDevice()
    #Network_Analyser.getDataFromDevice()
#'set_reac':20
    #
# result=[2738, 2738, 65535, 65535, 65534, 65535, 65535, 65535, 21180, 65535, 65535, 65534, 5762, 0, 5998, 65534, 5762, 0, 600, 65534, 55536, 65534, 62, 11374, 0, 65535, 32768, 65535, 32768, 5997, 0, 32768, 32768, 32768, 32768, 32768, 4, 4]
# result = client.read_holding_registers(40272, 3, unit=self.slave_id)
if __name__ == "__main__": main()