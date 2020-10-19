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
#__created__ = "2016-10-11"
#__lastUpdated__ = "2016-11-01"
'''

'''This API class is for an agent that want to communicate/monitor/control
devices that compatible with WeMo plugload'''

import re
import requests
from xml.dom import minidom
import time
import json
import datetime
import urllib2
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from bemoss_lib.protocols.discovery.SSDP import SSDP
import abc
import pprint

class baseAPI_Vera(baseAPI):

    def __init__(self,**kwargs):
        super(baseAPI_Vera, self).__init__(**kwargs)
        self._debug = True

    # @abc.abstractmethod
    def API_info(self):
        return

    # @abc.abstractmethod
    def dashboard_view(self):
        return

    # @abc.abstractmethod
    def ontology(self):
        return

    def discover(self):
        group = ("239.255.255.250", 1900)
        message = "\r\n".join([
            'M-SEARCH * HTTP/1.1',
            'HOST: {0}:{1}',
            'MAN: "ssdp:discover"',
            'ST: {st}', 'MX: 3', '', ''])
        service = "upnp:rootdevice"
        message = message.format(*group, st=service)
        SSDPobject = SSDP(message)
        responses = SSDPobject.request()
        if self._debug: print responses
        discovered_devices = list()
        addresslist = list()
        for response in responses:
            if (':49451/luaupnp.xml' in response or '/luaupnp.xml' in response) and (response not in addresslist):
                ip_addr = response[0:21]
                getDevicesUrl = ip_addr+':3480/data_request?id=lu_sdata'
                devicesResponse = urllib2.urlopen(getDevicesUrl)
                if devicesResponse.getcode() == 200:
                    content = json.loads(devicesResponse.read())
                    devices = content['devices']
                    category = dict()
                    for item in content['categories']:
                        category[item['id']] = item['name']
                    for device in devices:
                        address = ip_addr
                        model = category.get(device['category'],'Unknown').replace('/','_')
                        # end point device mac_address is unavailable from Vera hub,
                        # create fake mac for control purpose using the hub's serial number and device id
                        serialNo = content['serial_number']
                        mac_address = str(serialNo)+'vera'+str(device['id'])
                        discovered_devices.append(
                            {'address': address, 'mac': mac_address, 'model': model,
                             'vendor': 'Vera Control, Ltd.'})

        if self._debug == True:
            pprint.pprint(discovered_devices)
        return discovered_devices

    def getDataFromDevice(self):
        # to be overwrite by the device API
        return

    def requireData(self):
        try:
            getDevicesUrl = self.config['address'] + ':3480/data_request?id=lu_sdata'
            devicesResponse = urllib2.urlopen(getDevicesUrl)
            if devicesResponse.getcode() == 200:
                content = json.loads(devicesResponse.read())
                return content
        except NameError:
            print "Hub IP unknown in function requireData"
            # raise error for outer try block in baseAPI
            raise NameError

    def renewConnection(self):
        self.discover()

    def identifyDevice(self):
        identifyDeviceResult = False
        try:
            self.toggleDeviceStatus()
            print(self.config["model"]+" is being identified with starting status "+str(self.get_variable('status')))
            self.timeDelay(5)
            self.toggleDeviceStatus()
            print("Identification for "+self.config["model"]+" is done with status "+str(self.get_variable('status')))
            identifyDeviceResult = True
        except:
            raise
        return identifyDeviceResult

    #GET current status and POST toggled status
    def toggleDeviceStatus(self):
        if self.getDataFromDevice()['status'] == "ON":
            self.setDeviceStatus({"status":"OFF"})
        else:
            self.setDeviceStatus({"status":"ON"})

    def timeDelay(self, time_iden):  # specify time_iden for how long to delay the process
        t0 = time.time()
        self.seconds = time_iden
        while time.time() - t0 <= time_iden:
            self.seconds = self.seconds - 1
            print("wait: {} sec".format(self.seconds))
            time.sleep(1)

    def preidentify_message(self):
        identifyDeviceResult = False
        print(" {0}Agent for {1} is identifying itself by doing colorloop. Please observe your lights"
              .format(self.config.get('agent_id', None), self.config.get('model', None)))
        self.devicewasoff = 0
        if self.get_variable('status') == "OFF":
            self.devicewasoff = 1
            message = {"status": "ON"}
            return message
        else:
            return {"status": "OFF"}

    def postidentify_message(self):
        if self.devicewasoff:
            return {"status": "OFF"}
        else:
            message = {"status": "ON"}
            return message
# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    VeraDevice = baseAPI_Vera(model='Thermostat', api='API_Vera', mac_address = '50008574vera6', address='http://192.168.10.204')
    VeraDevice.discover()
    # print VeraDevice.getDeviceStatus()

if __name__ == "__main__": main()
