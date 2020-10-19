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
lighting devices that driven by Particle Photon and Particle relay shield'''

import json
import time
from spyrk import SparkCloud
from DeviceAPI.BaseAPI import baseAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY

class API(baseAPI):
    def __init__(self,**kwargs):
        super(API, self).__init__(**kwargs)

        if 'username' in kwargs.keys():
            self.USERNAME = kwargs['username']
            self.PASSWORD = kwargs['password']
            self.address = kwargs.get('address',None)

            self.login(self.USERNAME, self.PASSWORD)
            try:
                for dev in self.Particle.devices:
                    try:
                        if self.Particle.devices[dev].ip.encode('utf-8') == self.address:
                            self.device = dev
                    except:
                        print "One of the devices is not setup or online"
            except:
                print "Error occured in classAPI_Particle initialization"

        self._debug = False

    def login(self, username, password):
        try:
            print 'trying to connect to the cloud...'
            # Though Spark is now Particle, this python API still use Spark here.
            self.Particle = SparkCloud(username, password)
        except Exception as er:
            print er
            self.Particle = None
            print('\nLog in failed, please check your credentials!')

    def API_info(self):
        return [{'device_model' : 'Photon-Core', 'vendor_name' : 'Particle', 'communication' : 'WiFi',
                'device_type_id' : 2,'api_name': 'API_Particle','html_template':'lighting/lighting.html',
                'agent_type':'BasicAgent','identifiable' : True, 'authorizable' : False, 'is_cloud_device' : True,
                'schedule_weekday_period' : 4,'schedule_weekend_period' : 4, 'allow_schedule_period_delete' : False,
                'chart_template': 'charts/charts_lighting.html'}
                ]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "image", "value": 'sdb_on.png'},
                "bottom": BEMOSS_ONTOLOGY.BRIGHTNESS.NAME}

    def ontology(self):
        return {"status": BEMOSS_ONTOLOGY.STATUS, "brightness": BEMOSS_ONTOLOGY.BRIGHTNESS}

    def discover(self, username, password, token=None):
        self.login(username, password)
        discovered_devices = list()
        particle = self.Particle
        try:
            dev_list = self.list_dev()
            for idx in dev_list:
                try:
                    ip_addr = particle.devices[idx].ip.encode('utf8')
                    mac_addr = particle.devices[idx].mac.replace(":", "").encode('utf8')
                    nickname = idx.encode('utf8')
                    discovered_devices.append({'address': ip_addr, 'mac': mac_addr, 'model': 'Photon-Core',
                                               'vendor': 'Particle', 'nickname':nickname})
                except:
                    print "This device: " + str(idx) + " has not been setup or is offline."
        except:
            print "Particle get IP failed, try again"

        if self._debug:
            print discovered_devices
        return discovered_devices

    def list_dev(self):
        dev_list = list()
        particle = self.Particle
        for dev in particle.devices:
            dev_list.append(dev)
        return dev_list

    def renewConnection(self):
        self.login(self.USERNAME, self.PASSWORD)

    # GET Open the URL and read the data
    def getDataFromDevice(self):
        if self.Particle.devices[self.device].D0 == 1:
            devicedata = {'status': BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON}
            if self.Particle.devices[self.device].D1 == 1:
                devicedata['brightness'] = BEMOSS_ONTOLOGY.BRIGHTNESS.POSSIBLE_VALUES.MAX
            else:
                devicedata['brightness'] = 50
        else:
            devicedata = {'status': BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF,
                          'brightness': BEMOSS_ONTOLOGY.BRIGHTNESS.POSSIBLE_VALUES.MIN}
        return devicedata


    def setDeviceData(self, postmsg):
        is_success = True
        if self.isPostmsgValid(postmsg) == True:  # check if the data is valid
            _data = json.dumps(postmsg)
            _data = json.loads(_data)
            pin_status = {}

            if _data[BEMOSS_ONTOLOGY.STATUS.NAME] == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF:
                pin_status= {'D0': 'LOW', 'D1': 'LOW', 'D2': 'LOW', 'D3': 'LOW'}

            elif _data[BEMOSS_ONTOLOGY.STATUS.NAME] == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON:

                if _data.has_key(BEMOSS_ONTOLOGY.BRIGHTNESS.NAME):

                    if _data[BEMOSS_ONTOLOGY.BRIGHTNESS.NAME] > 50:
                        pin_status = {'D0': 'HIGH', 'D1': 'HIGH', 'D2': 'HIGH', 'D3': 'HIGH'}

                    elif _data[BEMOSS_ONTOLOGY.BRIGHTNESS.NAME] > 10:
                        pin_status = {'D0': 'HIGH', 'D1': 'LOW', 'D2': 'HIGH', 'D3': 'LOW'}
                    else:
                        pin_status = {'D0': 'LOW', 'D1': 'LOW', 'D2': 'LOW', 'D3': 'LOW'}
                else:
                    pin_status = {'D0': 'HIGH', 'D1': 'HIGH', 'D2': 'HIGH', 'D3': 'HIGH'}

            try:
                particle = self.Particle
                D0_set = particle.devices[self.device].digitalwrite('D0', pin_status['D0'])
                D1_set = particle.devices[self.device].digitalwrite('D1', pin_status['D1'])
                D2_set = particle.devices[self.device].digitalwrite('D2', pin_status['D2'])
                D3_set = particle.devices[self.device].digitalwrite('D3', pin_status['D3'])
                # Change the cloud variables
                result_D0 = particle.devices[self.device].setResult('D0', pin_status['D0'])
                result_D1 = particle.devices[self.device].setResult('D1', pin_status['D1'])
                result_D2 = particle.devices[self.device].setResult('D2', pin_status['D2'])
                result_D3 = particle.devices[self.device].setResult('D3', pin_status['D3'])

                if D0_set and D1_set and D2_set and D3_set:
                    is_success = True
                else:
                    is_success = False

            except:
                print("ERROR: classAPI_Particle failure! @ setDeviceStatus")
                is_success = False
        else:
            print("The POST message is invalid, check thermostat_mode, heat_setpoint, cool_coolsetpoint setting and try again\n")
            is_success = False
        return is_success

    def isPostmsgValid(self,postmsg):  # check validity of postmsg
        dataValidity = True
        # postmsg must have status
        if BEMOSS_ONTOLOGY.STATUS.NAME not in postmsg.keys():
            dataValidity = False
        # postmsg does not need to have brightness
        if BEMOSS_ONTOLOGY.BRIGHTNESS.NAME in postmsg.keys():
            if postmsg[BEMOSS_ONTOLOGY.BRIGHTNESS.NAME] > BEMOSS_ONTOLOGY.BRIGHTNESS.POSSIBLE_VALUES.MAX:
                dataValidity = False
            if postmsg[BEMOSS_ONTOLOGY.BRIGHTNESS.NAME] < BEMOSS_ONTOLOGY.BRIGHTNESS.POSSIBLE_VALUES.MIN:
                dataValidity = False
        return dataValidity

        # Identify Device by Toggling device status twice
    def identifyDevice(self):
        identifyDeviceResult = False
        try:
            self.getDeviceStatus()
            self.toggleDeviceStatus()
            print(self.config["address"] + " is being identified with starting status " + str(
                self.get_variable('status')))
            self.timeDelay(5)
            self.toggleDeviceStatus()
            print("Identification for " + self.config["address"] + " is done with status " + str(
                self.get_variable('status')))
            identifyDeviceResult = True
        except:
            print("ERROR: classAPI_Particle failure! @ identifyDevice")
        return identifyDeviceResult

    # ------------ Helper Methods -------------------------------------
    # GET current status and POST toggled status
    def toggleDeviceStatus(self):
        if self.get_variable(BEMOSS_ONTOLOGY.STATUS.NAME) == BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON:
            self.setDeviceStatus({BEMOSS_ONTOLOGY.STATUS.NAME: BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.OFF})
        else:
            self.setDeviceStatus({BEMOSS_ONTOLOGY.STATUS.NAME: BEMOSS_ONTOLOGY.STATUS.POSSIBLE_VALUES.ON})

    # time delay
    def timeDelay(self, time_iden):  # specify time_iden for how long to delay the process
        t0 = time.time()
        self.seconds = time_iden
        while time.time() - t0 <= time_iden:
            self.seconds = self.seconds - 1
            print("wait: {} sec".format(self.seconds))
            time.sleep(1)


# This main method will not be executed when this class is used as a module
def main():
    # Step1: create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    Particle = API(username='zxymark221@gmail.com', password='Zxy@ari900', model='Photon',agent_id='lighting1',api='API1',address='192.168.10.175')
    # Particle.setDeviceStatus({"status":"OFF"})
    # Particle.discover('zxymark221@gmail.com', 'Zxy@ari900')
    Particle.getDeviceStatus()
    #CT50Thermostat.identifyDevice()
    # scheduleData = {'Enabled': True, 'monday':[['Morning', 50, 83, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]], 'tuesday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'wednesday':[['Morning', 300 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'thursday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'friday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'saturday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],'sunday':[['Morning', 360 , 70, 80],['Day',480, 72, 82],['Evening',960, 71, 84],['Night',1000, 69, 72]],}
    # CT50Thermostat.setDeviceSchedule(scheduleData)

if __name__ == "__main__": main()
