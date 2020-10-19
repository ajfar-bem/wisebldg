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

#__author__ =  "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''
import sys
import numpy as np
import logging
from bemoss_lib.utils import db_helper
from bemoss_lib.utils.catcherror import catcherror
import time
import json
import settings
from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent

_log = logging.getLogger(__name__)


class IlluminanceBasedLightingControl(BEMOSSAgent):

    def __init__(self, *args, **kwargs):

        super(IlluminanceBasedLightingControl, self).__init__(*args,**kwargs)
        self.variables = kwargs
        self.app_id = self.agent_id
        self.update_para(self.dbcon,'all')
        # monitor time should be larger or equal to device monitor time.
        self.monitor_time = int(settings.DEVICES['device_monitor_time'])
        self.calibrate_topic = 'calibrate'
        self.update_target_topic = 'update_target'
        self.firsttime = True
        self.setup()
        self.run()

    def setup(self,):
        self.runPeriodically(self.light_tracking,self.monitor_time)
        self.subscribe(topic=self.calibrate_topic,callback=self.calibrate)
        self.subscribe(topic=self.update_target_topic,callback=self.update_target)

    def update_para(self, dbcon, var=None):
        # multiple lightings can be controlled and multiple sensor readings can be combined.
        dbcon.execute("SELECT app_data FROM application_running WHERE app_agent_id=%s", (self.app_id,))
        app_data = dbcon.fetchone()[0]
        if 'target' in app_data.keys():
            self.target_illuminance = app_data['target']
        if 'sensitivity' in app_data.keys():
            self.impact = app_data['sensitivity']
        if var == 'all':
            self.lightings = []
            self.sensor = []
            for light in app_data['lightings']:
                dbcon.execute("SELECT agent_id FROM device_info WHERE nickname=%s", (light,))
                self.lightings.append(dbcon.fetchone()[0])
            for sensor in app_data['lsensors']:
                dbcon.execute("SELECT agent_id FROM device_info WHERE nickname=%s", (sensor,))
                self.sensor.append(dbcon.fetchone()[0])

    def calibrate(self, dbcon, sender, topic, message):
        '''
        This function will conduct a calibration to find out the approximate relation between brightness and illuminance
        since it varies by installation cases. This relation will be used in later controlling process.
        :return: No return for this function, calculated relation is stored in a self variable.
        '''
        print 'start calibration...'
        dbcon.execute("SELECT app_data FROM application_running WHERE app_agent_id=%s", (self.app_id,))
        app_data = dbcon.fetchone()[0]
        app_data.update({'calibrating': True})
        dbcon.execute("UPDATE application_running SET app_data=%s WHERE app_agent_id=%s",
                            (json.dumps(app_data), self.app_id,))
        dbcon.commit()
        X = np.array([[1, 10], [1, 40], [1, 70], [1, 100]])
        y = []
        for brightness in X[:,1]:
            print 'Tesing with brightness ' + str(brightness) + '%:'
            message = {'brightness': brightness}
            current_brightness = self.get_brightness(dbcon)
            # Light control occasionally will not be successful, the loop here will make sure the desired brightness is acquired.
            while current_brightness != brightness:
                self.light_controlling(message)
                time.sleep(10)
                current_brightness = self.get_brightness(dbcon)
            time.sleep(self.monitor_time)
            illuminance = self.illuminance_measuring(dbcon)
            print 'The illuminance at brightness ' + str(brightness) + '% is ' + str(illuminance) + ' Lux'

            y.append([illuminance])
        y = np.array(y)
        reg_para = np.matmul(np.linalg.inv(np.matmul(X.transpose(), X)), np.matmul(X.transpose(), y))
        # self.impact shows the impact of brightness on illuminance, unit: Lux/1%
        self.impact = reg_para[1][0]
        print 'calibration result is ' + str(self.impact) + ' Lux/1%'
        dbcon.execute("SELECT app_data FROM application_running WHERE app_agent_id=%s", (self.app_id,))
        app_data = dbcon.fetchone()[0]
        if 'calibrating' in app_data:
            app_data.pop('calibrating')

        app_data.update({'sensitivity': self.impact, 'max_illuminance':illuminance})
        dbcon.execute("UPDATE application_running SET app_data=%s WHERE app_agent_id=%s",
                            (json.dumps(app_data), self.app_id,))
        dbcon.commit()

    def update_target(self, dbcon, sender, topic, message):
        message = json.loads(message)
        self.target_illuminance = message['target']
        dbcon.execute("SELECT app_data FROM application_running WHERE app_agent_id=%s", (self.app_id,))
        app_data = dbcon.fetchone()[0]
        app_data.update({'target': self.target_illuminance})
        dbcon.execute("UPDATE application_running SET app_data=%s WHERE app_agent_id=%s",
                            (json.dumps(app_data),self.app_id,))
        dbcon.commit()


    def light_tracking(self, dbcon):
        # if self.firsttime:
        #     self.firsttime = False
        #     self.calibrate()
        self.update_para(dbcon)

        dbcon.execute("UPDATE application_running SET status=%s WHERE app_agent_id=%s",
                            ("running", self.app_id,))
        dbcon.commit()

        try:
            illuminance = self.illuminance_measuring(dbcon)
            needed_luminance = self.target_illuminance - illuminance
            current_bri = self.get_brightness(dbcon)
            if needed_luminance > 30 or needed_luminance < -30:
                brightness_needed = current_bri + int(needed_luminance / self.impact)
                if brightness_needed < 0:
                    message = {'brightness': 0.0}
                elif brightness_needed > 100:
                    message = {'brightness': 100.0}
                else:
                    message = {'brightness': float(brightness_needed)}
                message.update({'user': 'Illuminance based control', 'status': 'ON'})
                self.light_controlling(message)
        except AttributeError:
            print 'Have not calibrate yet.'


    @catcherror('Error at illuminance measuring at illuminance based control')
    def illuminance_measuring(self,dbcon):
        illuminance_readings = []
        for light_sensor in self.sensor:
            dbcon.execute("SELECT data FROM devicedata WHERE agent_id=%s", (light_sensor,))
            if dbcon.rowcount != 0:
                illuminance_readings.append(dbcon.fetchone()[0]['illumination'])
        illuminance_avr = np.mean(illuminance_readings)
        return illuminance_avr

    @catcherror('Get brightness failed at illuminance based control')
    def get_brightness(self,dbcon):
        dbcon.execute("SELECT data FROM devicedata WHERE agent_id=%s", (self.lightings[0],))
        if dbcon.rowcount != 0:
            brightness = dbcon.fetchone()[0]['brightness']
            return brightness

    @catcherror('Lightings have not been selected in iblc app.')
    def light_controlling(self, message):
        for light in self.lightings:
            headers = {}
            topic = 'update'
            self.bemoss_publish(target=light,topic=topic, message=message)


if __name__ == '__main__':
    print "Cannot run as script"