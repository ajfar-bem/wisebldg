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
debug = True
from HTMLParser import HTMLParser


class API(baseAPI):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.device_supports_auto = True
        #self.address=address
        self._debug = True

    def API_info(self):

        return [{'device_model': "E30xx", 'vendor_name': "eGauge Systems, LLC", 'communication': 'WiFi',
                 'device_type_id': 5, 'api_name': 'API_energyhousePM', 'html_template': 'powermeter/powermeter_EH.html',
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable' : False, 'is_cloud_device': False,
                 'schedule_weekday_period': 4, 'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_EnergyHouse.html'},
                ]

    def dashboard_view(self):
        return {"top": None,
                "center": {"type": "number", "value": BEMOSS_ONTOLOGY.POWER.NAME, "unit": 'W'},
                "bottom": None,"image":"powermeter.png"}

    def ontology(self):
        return {"Minisplits 4":BEMOSS_ONTOLOGY.POWER_AC,"Minisplits 1":BEMOSS_ONTOLOGY.POWER_L1,"Minisplits 2":BEMOSS_ONTOLOGY.POWER_L2,"Minisplits 3":BEMOSS_ONTOLOGY.POWER_L3,
"Total Usage":BEMOSS_ONTOLOGY.POWER}


    def discover(self):

        responses = list()
        try:
            r = requests.get(
                url="http://egauge2738.egaug.es")
            if r.status_code == 200:
                responses.append({'address': "http://egauge2738.egaug.es", 'mac': "2738",
                                  'model': "E30xx", 'vendor': 'eGauge Systems, LLC'})
                print responses
                return responses
            else:
                return responses
        except:
            return responses

    def getDataFromDevice(self):
        try:
            devicedata={}
            r = requests.get(
                url=self.config["address"]+"/cgi-bin/egauge?inst",
                params="tot"
                )

            if r.status_code == 200:  # 200 means successfully
                devicedata=self.getDeviceInfoXML(r.content)
                return devicedata
        except Exception as e:
            print e
            raise


    def getDeviceInfoXML(self, data):
        # Use the dom module to load xml data into a dictionary
        try:
            returndata={}
            print data
            parser = MyHTMLParser()

            parser.feed(data)
            #Pf=float(parser.Power)/float(parser.ApparantPower)
            #Pf=round(Pf, 2)
            #setattr(parser, "PowerFactor", Pf)
            for key in self.ontology().keys():
                    returndata[key] = float(getattr(parser,key))
            print returndata
            return returndata
        except Exception as e:
            print e
            raise

class MyHTMLParser(HTMLParser,API):


    flag = False
    data_point = ''


    def handle_starttag(self, tag, attrs):

        if tag == 'r':
            print attrs
            if attrs[0][1] == "P":
                for key in self.ontology().keys():

                        if len(attrs) > 1 and attrs[1][1] == key:
                            self.flag = True
                            self.data_point = key
                            continue
            if attrs[0][0] == "rt":
                if attrs[1][0] == "t":
                    for key in self.ontology().keys():

                        if len(attrs) > 1 and attrs[2][1] == key:
                            self.flag = True
                            self.data_point = key
                            if attrs[2][0] == "n":
                                name = attrs[2][1]
                                self.name = name[:14]
                            break

    def handle_data(self, data):

        for key in self.ontology().keys():
            if self.flag == True and self.data_point == key and self.lasttag=="i":
                data = float(data) / 1000
                setattr(self,key,abs(round(data,2)))
                self.flag = False



def main():

    Power_meter = API(model='Egauge',type='PowerMeter',api='API_eGaugePM',address='http://egauge2738.egaug.es')

    Power_meter.getDeviceStatus()

    #Power_meter.discover()

if __name__ == "__main__": main()