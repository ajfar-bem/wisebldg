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
from HTMLParser import HTMLParser
import requests
import base64
from BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY

debug = True


class API(baseAPI):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.device_supports_auto = False
        self.set_variable('connection_renew_interval', 6000)  # nothing to renew, right now

        if 'username' in kwargs.keys():
            self.username = kwargs['username']
            self.password = kwargs['password']


    def API_info(self):

        return [{'device_model': "WattNode MODBUS WNC-3Y-208-MB", 'vendor_name': "Continental Control System", 'communication':  "Cloud",
                 'device_type_id': 5, 'api_name': 'API_AcquiSuite',
                 'html_template': 'powermeter/powermeter.html', 'support_oauth' : False,
                 'agent_type': 'BasicAgent', 'identifiable': False,'authorizable' : False, 'is_cloud_device': True,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_powermeter.html'}, ]

    def dashboard_view(self):
        return {"top": BEMOSS_ONTOLOGY.FREQUENCY.NAME,
                "center": {"type": "number", "value": BEMOSS_ONTOLOGY.POWER.NAME, "unit": 'W'},
                "bottom": BEMOSS_ONTOLOGY.VOLTAGE.NAME,
                "image":"powermeter.png"}


    def ontology(self):
        pass

        return {"energy_sum":BEMOSS_ONTOLOGY.ENERGY,
            "power_sum":BEMOSS_ONTOLOGY.POWER,
            "power_a":BEMOSS_ONTOLOGY.POWER_L1,
            "power_b":BEMOSS_ONTOLOGY.POWER_L2,
            "power_c":BEMOSS_ONTOLOGY.POWER_L3,
            "voltage_avg":BEMOSS_ONTOLOGY.VOLTAGE,
            "voltage_a":BEMOSS_ONTOLOGY.VOLTAGE_L1,
            "voltage_b":BEMOSS_ONTOLOGY.VOLTAGE_L2,
            "voltage_c":BEMOSS_ONTOLOGY.VOLTAGE_L3,
            "frequency":BEMOSS_ONTOLOGY.FREQUENCY,
            "power_factor_avg":BEMOSS_ONTOLOGY.POWERFACTOR,
            "power_factor_a":BEMOSS_ONTOLOGY.POWERFACTOR_L1,
            "power_factor_b":BEMOSS_ONTOLOGY.POWERFACTOR_L2,
            "power_factor_c":BEMOSS_ONTOLOGY.POWERFACTOR_L3,
            "current_a":BEMOSS_ONTOLOGY.CURRENT_L1,
            "current_b":BEMOSS_ONTOLOGY.CURRENT_L2,
            "current_c":BEMOSS_ONTOLOGY.CURRENT_L3,

        }
        # method1: GET Open the URL and read the data
    def login(self):
        # Step1: Get access token
        # My API (POST https://api.netatmo.net/oauth2/token)
        try:
            r = requests.get(
                url="http://38.68.251.229/setup/devlist.cgi",
                params={
                    "GATEWAY": "127.0.0.1",
                    "SETUP": "XML",
                    "ts_cache": "1429386291329",
                },

                headers={
                    "Authorization": "Basic dXNlcjpiZW1vc3M5MDBWVA==",
                },
            )
            # print('Response HTTP Status Code : {status_code}'.format(status_code=r.status_code))
            # print('Response HTTP Response Body : {content}'.format(content=r.content))
            if r.status_code == 200:  # 200 means successfully
                self.getDeviceInfoXML(r.content)
            else:
                raise Exception("Bad response")
        except requests.exceptions.RequestException as e:
            raise

    def getDeviceInfoXML(self, data):
        # Use the dom module to load xml data into a dictionary
        try:
            parser = MyHTMLParser()
            parser.initialize()
            parser.feed(data)
            # TODO FIX this for all devices
            self.set_variable("address", parser.devices['address'])
            self.set_variable("name", parser.devices['name'])
            self.set_variable("mac_address", parser.devices['serial'])
        except:
            raise

    def discover(self,username,password,token=None):
        self.model=self.API_info()[0]['device_model']
        self.vendor=self.API_info()[0]['vendor_name']

        r = requests.get(
            url="http://38.68.251.229/setup/devlist.cgi",
            params={
                "GATEWAY": "127.0.0.1",
                "SETUP": "XML",
                "ts_cache": "1429386291329",
            },

            headers={
                "Authorization":"Basic "+str(base64.b64encode(str(username)+':'+str(password))),
            },
        )
        # print('Response HTTP Status Code : {status_code}'.format(status_code=r.status_code))
        # print('Response HTTP Response Body : {content}'.format(content=r.content))

        if r.status_code == 200:  # 200 means successfully
            parser = MyHTMLParser()
            parser.initialize()
            parser.feed(r.content)
        else:
            #print "ERROR AcquiSuite"
            return []


        device_list = list()
        for i in range(len(parser.devices['address'])):
            device_list.append(
                {'address': parser.devices['address'][i], 'mac': parser.devices['serial'][i], 'model': self.model, 'vendor': self.vendor,
                 'nickname': parser.devices['name'][i]})
        return device_list

    def getDataFromDevice(self):
        # try:
        r = requests.get(
            # TODO Fix url later to use data from discovery
            # url=self.get_variable('address'),
            url='http://38.68.251.229/setup/loggersetup.cgi',
            params={
                "ADDRESS": self.variables['address'],
            },
            headers={
                "Authorization": "Basic dXNlcjphbHBoYTAyUkQ4IyM=",
            },
        )
        #print 'Response status code: {}'.format(r.status_code)
        # print 'Response HTTP body: {}'.format(r.content)
        devicedata=dict()
        parser = MyHTMLParser()
        parser.feed(r.content)
        devicedata["energy_sum"] =float((parser.energy_sum).split()[0])
        devicedata["power_sum"] = float((parser.power_sum).split()[0])
        devicedata["power_a"] = float((parser.power_a).split()[0])
        devicedata["power_b"] = float((parser.power_b).split()[0])
        devicedata["power_c"] = float((parser.power_c).split()[0])
        devicedata["voltage_avg"] = float((parser.voltage_avg).split()[0])
        devicedata["voltage_a"] = float((parser.voltage_a).split()[0])
        devicedata["voltage_b"] = float((parser.voltage_b).split()[0])
        devicedata["voltage_c"] = float((parser.voltage_c).split()[0])
        devicedata["voltage_avg_ll"] = float((parser.voltage_avg_ll).split()[0])
        devicedata["voltage_ab"] = float((parser.voltage_ab).split()[0])
        devicedata["voltage_bc"] = float((parser.voltage_bc).split()[0])
        devicedata["voltage_ac"] = float((parser.voltage_ac).split()[0])
        devicedata["frequency"] = float((parser.frequency).split()[0])
        devicedata["energy_a_net"] = float((parser.energy_a_net).split()[0])
        devicedata["energy_b_net"] = float((parser.energy_b_net).split()[0])
        devicedata["energy_c_net"] = float((parser.energy_c_net).split()[0])
        devicedata["energy_pos_a"] = float((parser.energy_pos_a).split()[0])
        devicedata["energy_pos_b"] = float((parser.energy_pos_b).split()[0])
        devicedata["energy_pos_c"] = float((parser.energy_pos_c).split()[0])
        devicedata["energy_neg_sum"] = float((parser.energy_neg_sum).split()[0])
        devicedata["energy_neg_sum_nr"] = float((parser.energy_neg_sum_nr).split()[0])
        devicedata["energy_neg_a"] = float((parser.energy_neg_a).split()[0])
        devicedata["energy_neg_b"] = float((parser.energy_neg_b).split()[0])
        devicedata["energy_neg_c"] = float((parser.energy_neg_c).split()[0])
        devicedata["energy_reactive_sum"] = float((parser.energy_reactive_sum).split()[0])
        devicedata["energy_reactive_a"] = float((parser.energy_reactive_a).split()[0])
        devicedata["energy_reactive_b"] = float((parser.energy_reactive_b).split()[0])
        devicedata["energy_reactive_c"] = float((parser.energy_reactive_c).split()[0])
        devicedata["energy_apparent_sum"] = float((parser.energy_apparent_sum).split()[0])
        devicedata["energy_apparent_a"] = float((parser.energy_apparent_a).split()[0])
        devicedata["energy_apparent_b"] = float((parser.energy_apparent_b).split()[0])
        devicedata["energy_apparent_c"] = float((parser.energy_apparent_c).split()[0])
        devicedata["power_factor_avg"] = float((parser.power_factor_avg).split()[0])
        devicedata["power_factor_a"] = float((parser.power_factor_a).split()[0])
        devicedata["power_factor_b"] = float((parser.power_factor_b).split()[0])
        devicedata["power_factor_c"] = float((parser.power_factor_c).split()[0])
        devicedata["power_reactive_sum"] = float((parser.power_reactive_sum).split()[0])
        devicedata["power_reactive_a"] = float((parser.power_reactive_a).split()[0])
        devicedata["power_reactive_b"] = float((parser.power_reactive_b).split()[0])
        devicedata["power_reactive_c"] = float((parser.power_reactive_c).split()[0])
        devicedata["power_apparent_sum"] = float((parser.power_apparent_sum).split()[0])
        devicedata["power_apparent_a"] = float((parser.power_apparent_a).split()[0])
        devicedata["power_apparent_b"] = float((parser.power_apparent_b).split()[0])
        devicedata["power_apparent_c"] = float((parser.power_apparent_c).split()[0])
        devicedata["current_a"] = float((parser.current_a).split()[0])
        devicedata["current_b"] = float((parser.current_b).split()[0])
        devicedata["current_c"] = float((parser.current_c).split()[0])
        devicedata["demand"] = float((parser.demand).split()[0])
        devicedata["demand_min"] = float((parser.demand_min).split()[0])
        devicedata["demand_max"] = float((parser.demand_max).split()[0])
        devicedata["demand_apparent"] = float((parser.demand_apparent).split()[0])
        devicedata["demand_a"] = float((parser.demand_a).split()[0])
        devicedata["demand_b"] = ((parser.demand_b).split()[0])
        devicedata["demand_c"] = float((parser.demand_c).split()[0])
        # #print("printing agent's knowledge")
        # for k, v in self.variables.items():
        #     print (k, v)
        return devicedata
        # except Exception as e:
        #     print ('HTTP Request failed')
        #     raise e
        #     return None

            # def printDeviceStatus(self):
            #     print "energy sum: {} kWh".format(self.get_variable("energy_sum"))

class MyHTMLParser(HTMLParser):
    flag = False
    data_point = ''
    numdevices = 0

    def initialize(self):
        self.devices = dict(address=[], parentaddress=[], name=[], status=[],
                            type=[], serial=[], firmware=[], devclass=[], nport=[],
                            comparam=[], pktsent=[], pktreceived=[], pkterror=[],
                            pktsuccessrate=[], pktrtt=[], nstatus=[], ndeverror=[],
                            strdeverr=[])
        for k in self.devices:
            self.devices[k] = list()

    def handle_starttag(self, tag, attrs):

        if tag == 'td':
            # print "Encountered a start tag:", tag
            # print attrs
            # print 'len(attrs): {}'.format(len(attrs))
            # if len(attrs)>2:
                # print 'type(attrs[3]): {}'.format(type(attrs[3]))
                # print  'attrs[3]: {}'.format(attrs[3])
                # print 'type(attrs[3][1]): {}'.format(type(attrs[3][1]))
                # print  'attrs[3][1]: {}'.format(attrs[3][1])
            if len(attrs)<4:
                return
            if len(attrs)>2 and attrs[3][1] == "P0V":
                self.flag = True
                self.data_point = "energy_sum"
            elif len(attrs)>2 and attrs[3][1] == "P4V":
                self.flag = True
                self.data_point = "power_sum"
            elif len(attrs)>2 and attrs[3][1] == "P5V":
                self.flag = True
                self.data_point = "power_a"
            elif len(attrs)>2 and attrs[3][1] == "P6V":
                self.flag = True
                self.data_point = "power_b"
            elif len(attrs)>2 and attrs[3][1] == "P7V":
                self.flag = True
                self.data_point = "power_c"
            elif len(attrs)>2 and attrs[3][1] == "P8V":
                self.flag = True
                self.data_point = "voltage_avg"
            elif len(attrs)>2 and attrs[3][1] == "P9V":
                self.flag = True
                self.data_point = "voltage_a"
            elif len(attrs)>2 and attrs[3][1] == "P10V":
                self.flag = True
                self.data_point = "voltage_b"
            elif len(attrs)>2 and attrs[3][1] == "P11V":
                self.flag = True
                self.data_point = "voltage_c"
            elif len(attrs)>2 and attrs[3][1] == "P12V":
                self.flag = True
                self.data_point = "voltage_avg_ll"
            elif len(attrs)>2 and attrs[3][1] == "P13V":
                self.flag = True
                self.data_point = "voltage_ab"
            elif len(attrs)>2 and attrs[3][1] == "P14V":
                self.flag = True
                self.data_point = "voltage_bc"
            elif len(attrs)>2 and attrs[3][1] == "P15V":
                self.flag = True
                self.data_point = "voltage_ac"
            elif len(attrs)>2 and attrs[3][1] == "P16V":
                self.flag = True
                self.data_point = "frequency"
            elif len(attrs)>2 and attrs[3][1] == "P17V":
                self.flag = True
                self.data_point = "energy_a_net"
            elif len(attrs)>2 and attrs[3][1] == "P18V":
                self.flag = True
                self.data_point = "energy_b_net"
            elif len(attrs)>2 and attrs[3][1] == "P19V":
                self.flag = True
                self.data_point = "energy_c_net"
            elif len(attrs)>2 and attrs[3][1] == "P20V":
                self.flag = True
                self.data_point = "energy_pos_a"
            elif len(attrs)>2 and attrs[3][1] == "P21V":
                self.flag = True
                self.data_point = "energy_pos_b"
            elif len(attrs)>2 and attrs[3][1] == "P22V":
                self.flag = True
                self.data_point = "energy_pos_c"
            elif len(attrs)>2 and attrs[3][1] == "P23V":
                self.flag = True
                self.data_point = "energy_neg_sum"
            elif len(attrs)>2 and attrs[3][1] == "P24V":
                self.flag = True
                self.data_point = "energy_neg_sum_nr"
            elif len(attrs)>2 and attrs[3][1] == "P25V":
                self.flag = True
                self.data_point = "energy_neg_a"
            elif len(attrs)>2 and attrs[3][1] == "P26V":
                self.flag = True
                self.data_point = "energy_neg_b"
            elif len(attrs)>2 and attrs[3][1] == "P27V":
                self.flag = True
                self.data_point = "energy_neg_c"
            elif len(attrs)>2 and attrs[3][1] == "P28V":
                self.flag = True
                self.data_point = "energy_reactive_sum"
            elif len(attrs)>2 and attrs[3][1] == "P29V":
                self.flag = True
                self.data_point = "energy_reactive_a"
            elif len(attrs)>2 and attrs[3][1] == "P30V":
                self.flag = True
                self.data_point = "energy_reactive_b"
            elif len(attrs)>2 and attrs[3][1] == "P31V":
                self.flag = True
                self.data_point = "energy_reactive_c"
            elif len(attrs)>2 and attrs[3][1] == "P32V":
                self.flag = True
                self.data_point = "energy_apparent_sum"
            elif len(attrs)>2 and attrs[3][1] == "P33V":
                self.flag = True
                self.data_point = "energy_apparent_a"
            elif len(attrs)>2 and attrs[3][1] == "P34V":
                self.flag = True
                self.data_point = "energy_apparent_b"
            elif len(attrs)>2 and attrs[3][1] == "P35V":
                self.flag = True
                self.data_point = "energy_apparent_c"
            elif len(attrs)>2 and attrs[3][1] == "P36V":
                self.flag = True
                self.data_point = "power_factor_avg"
            elif len(attrs)>2 and attrs[3][1] == "P37V":
                self.flag = True
                self.data_point = "power_factor_a"
            elif len(attrs)>2 and attrs[3][1] == "P38V":
                self.flag = True
                self.data_point = "power_factor_b"
            elif len(attrs)>2 and attrs[3][1] == "P39V":
                self.flag = True
                self.data_point = "power_factor_c"
            elif len(attrs)>2 and attrs[3][1] == "P40V":
                self.flag = True
                self.data_point = "power_reactive_sum"
            elif len(attrs)>2 and attrs[3][1] == "P41V":
                self.flag = True
                self.data_point = "power_reactive_a"
            elif len(attrs)>2 and attrs[3][1] == "P42V":
                self.flag = True
                self.data_point = "power_reactive_b"
            elif len(attrs)>2 and attrs[3][1] == "P43V":
                self.flag = True
                self.data_point = "power_reactive_c"
            elif len(attrs)>2 and attrs[3][1] == "P44V":
                self.flag = True
                self.data_point = "power_apparent_sum"
            elif len(attrs)>2 and attrs[3][1] == "P45V":
                self.flag = True
                self.data_point = "power_apparent_a"
            elif len(attrs)>2 and attrs[3][1] == "P46V":
                self.flag = True
                self.data_point = "power_apparent_b"
            elif len(attrs)>2 and attrs[3][1] == "P47V":
                self.flag = True
                self.data_point = "power_apparent_c"
            elif len(attrs)>2 and attrs[3][1] == "P48V":
                self.flag = True
                self.data_point = "current_a"
            elif len(attrs)>2 and attrs[3][1] == "P49V":
                self.flag = True
                self.data_point = "current_b"
            elif len(attrs)>2 and attrs[3][1] == "P50V":
                self.flag = True
                self.data_point = "current_c"
            elif len(attrs)>2 and attrs[3][1] == "P51V":
                self.flag = True
                self.data_point = "demand"
            elif len(attrs)>2 and attrs[3][1] == "P52V":
                self.flag = True
                self.data_point = "demand_min"
            elif len(attrs)>2 and attrs[3][1] == "P53V":
                self.flag = True
                self.data_point = "demand_max"
            elif len(attrs)>2 and attrs[3][1] == "P54V":
                self.flag = True
                self.data_point = "demand_apparent"
            elif len(attrs)>2 and attrs[3][1] == "P55V":
                self.flag = True
                self.data_point = "demand_a"
            elif len(attrs)>2 and attrs[3][1] == "P56V":
                self.flag = True
                self.data_point = "demand_b"
            elif len(attrs)>2 and attrs[3][1] == "P57V":
                self.flag = True
                self.data_point = "demand_c"
            else:
                pass
        if tag == 'numdevices':
            self.flag = True
            self.data_point = "numdevices"
        if tag == 'device':
            # print attrs
            self.devices['address'].append(attrs[0][1])
            self.devices['parentaddress'].append(attrs[1][1])
            self.devices['name'].append(attrs[2][1])
            self.devices['status'].append(attrs[3][1])
            self.devices['type'].append(attrs[4][1])
            self.devices['serial'].append(attrs[5][1])
            self.devices['firmware'].append(attrs[6][1])
            self.devices['devclass'].append(attrs[7][1])
            self.devices['nport'].append(attrs[8][1])
            self.devices['comparam'].append(attrs[9][1])
            self.devices['pktsent'].append(attrs[10][1])
            self.devices['pktreceived'].append(attrs[11][1])
            self.devices['pkterror'].append(attrs[12][1])
            self.devices['pktsuccessrate'].append(attrs[13][1])
            self.devices['pktrtt'].append(attrs[14][1])
            self.devices['nstatus'].append(attrs[15][1])
            self.devices['ndeverror'].append(attrs[16][1])
            self.devices['strdeverr'].append(attrs[17][1])


                    # def handle_endtag(self, tag):
        # print "Encountered an end tag:", tag

    def handle_data(self, data):
        # print "Encountered some data : ", data
        # print "self.flag: {} datapoint: {}".format(self.flag, self.data_point)
        if self.flag is True and self.data_point == "numdevices":
            self.numdevices = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_sum":
            self.energy_sum = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_sum":
            self.power_sum = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_a":
            self.power_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_b":
            self.power_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_c":
            self.power_c = data
            self.flag = False
        elif self.flag == True and self.data_point == "voltage_avg":
            self.voltage_avg = data
            self.flag = False
        elif self.flag == True and self.data_point == "voltage_a":
            self.voltage_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "voltage_b":
            self.voltage_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "voltage_c":
            self.voltage_c = data
            self.flag = False
        elif self.flag == True and self.data_point == "voltage_avg_ll":
            self.voltage_avg_ll = data
            self.flag = False
        elif self.flag == True and self.data_point == "voltage_ab":
            self.voltage_ab = data
            self.flag = False
        elif self.flag == True and self.data_point == "voltage_bc":
            self.voltage_bc = data
            self.flag = False
        elif self.flag == True and self.data_point == "voltage_ac":
            self.voltage_ac = data
            self.flag = False
        elif self.flag == True and self.data_point == "frequency":
            self.frequency = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_a_net":
            self.energy_a_net = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_b_net":
            self.energy_b_net = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_c_net":
            self.energy_c_net = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_pos_a":
            self.energy_pos_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_pos_b":
            self.energy_pos_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_pos_c":
            self.energy_pos_c = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_neg_sum":
            self.energy_neg_sum = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_neg_sum_nr":
            self.energy_neg_sum_nr = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_neg_a":
            self.energy_neg_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_neg_b":
            self.energy_neg_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_neg_c":
            self.energy_neg_c = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_reactive_sum":
            self.energy_reactive_sum = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_reactive_a":
            self.energy_reactive_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_reactive_b":
            self.energy_reactive_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_reactive_c":
            self.energy_reactive_c = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_apparent_sum":
            self.energy_apparent_sum = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_apparent_a":
            self.energy_apparent_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_apparent_b":
            self.energy_apparent_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "energy_apparent_c":
            self.energy_apparent_c = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_factor_avg":
            self.power_factor_avg = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_factor_a":
            self.power_factor_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_factor_b":
            self.power_factor_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_factor_c":
            self.power_factor_c = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_reactive_sum":
            self.power_reactive_sum = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_reactive_a":
            self.power_reactive_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_reactive_b":
            self.power_reactive_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_reactive_c":
            self.power_reactive_c = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_apparent_sum":
            self.power_apparent_sum = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_apparent_a":
            self.power_apparent_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_apparent_b":
            self.power_apparent_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "power_apparent_c":
            self.power_apparent_c = data
            self.flag = False
        elif self.flag == True and self.data_point == "current_a":
            self.current_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "current_b":
            self.current_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "current_c":
            self.current_c = data
            self.flag = False
        elif self.flag == True and self.data_point == "demand":
            self.demand = data
            self.flag = False
        elif self.flag == True and self.data_point == "demand_min":
            self.demand_min = data
            self.flag = False
        elif self.flag == True and self.data_point == "demand_max":
            self.demand_max = data
            self.flag = False
        elif self.flag == True and self.data_point == "demand_apparent":
            self.demand_apparent = data
            self.flag = False
        elif self.flag == True and self.data_point == "demand_a":
            self.demand_a = data
            self.flag = False
        elif self.flag == True and self.data_point == "demand_b":
            self.demand_b = data
            self.flag = False
        elif self.flag == True and self.data_point == "demand_c":
            self.demand_c = data
            self.flag = False
        else:
            pass


# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    AcquiSuite = API(model='A8810', agent_id='datalogger1', api='API', address='1')
    print("{0} agent is initialzed for {1} using API={2} at {3}".format(AcquiSuite.get_variable('agent_id'),
                                                                        AcquiSuite.get_variable('model'),
                                                                        AcquiSuite.get_variable('api'),
                                                                        AcquiSuite.get_variable('address')))
    # Step2: read current thermostat status
    AcquiSuite.discover('user','alpha02RD8##')
    #AcquiSuite.discover()

if __name__ == "__main__": main()