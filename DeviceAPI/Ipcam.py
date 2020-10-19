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

'''This API class is for an agent that want to discover/communicate/monitor Foscam IP Cam'''

import urllib,urllib2
import json
from BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
import time
from xml.dom import minidom

debug=True
class API(baseAPI):

    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)
        if 'username' in kwargs.keys():
            self.username = kwargs['username']
            self.password = kwargs['password']

    def API_info(self):
        return [{'device_model': 'FI9853EP', 'vendor_name': 'Foscam', 'communication': 'WiFi',
                 'device_type_id': 7, 'api_name': 'API_Ipcam', 'html_template': 'others/ipcam.html',              #TODO device type id
                 'agent_type': 'BasicAgent', 'identifiable': False, 'authorizable' : False, 'is_cloud_device': True,
                  'schedule_weekday_period': 4,'schedule_weekend_period': 4, 'allow_schedule_period_delete': True,
                 'chart_template': 'charts/charts_ipcam.html'},]

    def dashboard_view(self):
        return {"center": {"type": "number", "value": BEMOSS_ONTOLOGY.CONTRAST.NAME},
                "bottom": BEMOSS_ONTOLOGY.BRIGHTNESS.NAME}

    def ontology(self):
        return {"brightness": BEMOSS_ONTOLOGY.BRIGHTNESS, "contrast": BEMOSS_ONTOLOGY.CONTRAST, "hue": BEMOSS_ONTOLOGY.HUE,"saturation": BEMOSS_ONTOLOGY.SATURATION,
               "Stream":BEMOSS_ONTOLOGY.STREAM }

    def discover(self,username, password,token,address,model): #TODO needs fixing
        responses = list()
        cmd="getDevInfo"

        _url=self.Return_url(address, username,password,cmd)
        print _url
        try:
            _deviceUrl = urllib2.urlopen(_url, timeout=20)
            if _deviceUrl.getcode() == 200:
                xmldoc = minidom.parse(_deviceUrl)
                #print xmldoc.toxml()

                for element in xmldoc.getElementsByTagName('mac'):
                    mac=element.firstChild.nodeValue
                    continue
                responses.append({'address': address, 'mac': mac,
                                                'model': model, 'vendor': "foscam"})
                return responses
            else:
                return responses
        except Exception as e:
            print e
            return responses


    def renewConnection(self):
        pass



    def Return_url(self,address, username, password, cmd, params=""):

        try:
            local_address = 'http://'+address.split(',')[0]

            if not params:

                parameters={"usr":username,"pwd":password,"cmd":cmd,}
                encoded_params=urllib.urlencode(parameters)
                if parameters["cmd"]=="GetMJStream":
                    url = local_address+"/cgi-bin/CGIStream.cgi?"+ encoded_params
                else:
                    url = local_address + '/cgi-bin/CGIProxy.fcgi?'+encoded_params

                return url
            else:
                    parameters = {"usr": username, "pwd": password, "cmd": cmd,params[0]:params[1]}
                    encoded_params = urllib.urlencode(parameters)

                    url = local_address + '/cgi-bin/CGIProxy.fcgi?' + encoded_params
                    return url
        except Exception as er:
            print er
            return None

    def getDataFromDevice(self):

        returndata={}
        cmdlist=["getImageSetting"]
        for cmd in cmdlist:
            try:
                address = self.config["address"]
                try:
                    _url = self.Return_url(address,self.username, self.password, cmd)
                    print _url
                    _deviceUrl = urllib2.urlopen(_url, timeout=20)
                except:
                    continue
                if _deviceUrl.getcode() == 200:
                    xmldoc = minidom.parse(_deviceUrl)
                    print xmldoc.toxml()
                    for point in self.ontology().keys():
                        for element in xmldoc.getElementsByTagName(point):
                            returndata[str(point)] = float(element.firstChild.nodeValue)
            except Exception as er:
                raise
                #return returndata
        returndata["Stream"] = "http_stream"
        print returndata
        return returndata

    def setDeviceStatus(self, postmsg):

        del postmsg["agent_id"]
        zippedlist=postmsg.items()
        for cmd,value in zippedlist:
            try:
                if cmd == "setContrast":
                    data = "constrast"
                else:
                    data=cmd[3:].lower()
                pair=data,value
                address = self.config["address"]
                _url = self.Return_url(address,self.username, self.password, cmd, params=pair)
                print _url
                if _url==None:
                    return False
                _deviceUrl = urllib2.urlopen(_url, timeout=20)
                if _deviceUrl.getcode() == 200:
                    continue
            except Exception as er:
                print er
                return False
        return True

# This main method will not be executed when this class is used as a module
def main():
    #Test code

    # Step1: create an object with initialized data from DeviceDiscovery Agent
    IPCam = API(model='Foscam',agent_id='basicagent',api='API_Ipcam',address='http://192.168.10.42:8899', username= 'aribemoss', password= 'ari900')
    #J=IPCam.discover("mkuzlu","ari900ari900")
    #print J

    #j=IPCam.setDeviceStatus({'setBrightness': 50, 'setSaturation': 50, 'setHue': 50, 'setContrast': 50, 'agent_id': 'FI98_00626E6B9F23'})

    t=IPCam.getDeviceStatus()
    print t


if __name__ == "__main__": main()