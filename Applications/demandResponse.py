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
import logging
from bemoss_lib.utils.catcherror import catcherror
import time
import datetime
import copy
from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from oadr2 import poll, event, schedule, database
from lxml import etree

import pytz


_log = logging.getLogger(__name__)


class DemandResponse(BEMOSSAgent):

    def __init__(self, *args, **kwargs):

        super(DemandResponse, self).__init__(*args,**kwargs)
        self.variables = kwargs
        self.app_id = self.agent_id
        self.start = None
        self.end = None
        self.dev_control = None
        self.previous_state = None
        self.prepared = False
        self.active = False
        # self.update_para(self.dbcon)
        # self.periodic_check(self.dbcon)
        self.monitor_time = 20
        self.info = {'lighting': BEMOSS_ONTOLOGY.BRIGHTNESS.NAME,
                     'plugload': BEMOSS_ONTOLOGY.STATUS.NAME,
                     'hvac': BEMOSS_ONTOLOGY.COOL_SETPOINT.NAME}
        self.openadr = True
        if self.openadr:
            # TODO: generalize the configuration below
            self.oadr_client = poll.OpenADR2(
                vtn_base_uri="http://192.168.10.69:8080/oadr2-vtn-groovy/",
                vtn_poll_interval=15,
                event_config={
                    "ven_id": 'ven1',
                    "vtn_ids": "ENOCtestVTN1",
                    "event_callback": self.oadr_event
                },
                control_opts={
                    "signal_changed_callback": self.signal_changed_callback,
                    "control_loop_interval": 30
                }
            )
            self.event_db = database.DBHandler()

        self.setup()
        self.run()

    def setup(self,):
        if self.openadr:
            self.runPeriodically(self.oadr_periodic_helper, self.monitor_time)
        else:
            self.runPeriodically(self.periodic_check,self.monitor_time)

    def signal_changed_callback(self, old_level, new_level):
        pass

    def oadr_periodic_helper(self, dbcon):
        if not self.active:
            print 'OADR helper function running.'
            self.update_para(dbcon)
            self.backup_previous_data(dbcon)

    def oadr_event(self, updated={}, canceled={}):
        current_event_state = self.get_event_state()
        if current_event_state == 'active' and self.active is False:
            print 'Demand Response Event Starts Now!'
            self.active = True
            self.device_control('activate')
        if current_event_state != 'active' and self.active is True:
            print 'Demand Response Event Ends Now!'
            self.active = False
            self.device_control('recovery')


    def get_event_state(self):
        active_event = None
        active_events = self.event_db.get_active_events()

        for event_id in active_events.iterkeys():
            event_data = self.get_event(event_id)

            e_start = event.get_active_period_start(event_data).replace(tzinfo=pytz.utc)
            now = datetime.datetime.now(pytz.utc)

            if e_start < now:
                active_event = event_data

        return ("active" if active_event is not None else "inactive")


    def get_event(self, e_id):
        evt = self.event_db.get_event(e_id)
        if evt is not None:
            evt = etree.XML(evt)
        return evt


    def periodic_check(self, dbcon):

        self.update_para(dbcon)
        if self.start > datetime.datetime.now():
            if self.start < datetime.datetime.now()+datetime.timedelta(minutes=3) and self.prepared is False:
                self.backup_previous_data(dbcon)
        elif datetime.datetime.now() < self.end and not self.active:
            self.device_control(status='activate')
            self.active = True
        elif datetime.datetime.now() > self.end and self.active:
            self.device_control(status='recovery')
            self.active = False
            self.prepared = False
        else:
            pass

    def update_para(self, dbcon, var=None):
        # multiple lightings can be controlled and multiple sensor readings can be combined.
        dbcon.execute("SELECT app_data FROM application_running WHERE app_agent_id=%s", (self.app_id,))
        app_data = dbcon.fetchone()[0]
        try:
            self.start = datetime.datetime.strptime(app_data['start'], '%Y-%m-%d %H:%M:%S')
            self.end = datetime.datetime.strptime(app_data['end'], '%Y-%m-%d %H:%M:%S')
            self.dev_control = app_data['devSelected']
        except KeyError:
            print 'One or more application configuration has not been defined.'

    def backup_previous_data(self, dbcon):
        self.previous_state = copy.deepcopy(self.dev_control)
        for dtype in self.info.keys():
            for dev in self.previous_state[dtype].keys():
                dbcon.execute("SELECT data FROM devicedata WHERE agent_id=%s", (dev,))
                if dbcon.rowcount != 0:
                    self.previous_state[dtype][dev] = dbcon.fetchone()[0][self.info[dtype]]
        self.prepared = True

    @catcherror('Error at device control at demand response')
    def device_control(self, status):
        if status == 'activate':
            control_data = self.dev_control
        else:
            control_data = self.previous_state

        for dtype in self.info.keys():
            for dev in control_data[dtype].keys():
                topic = 'update'
                message = {self.info[dtype]: control_data[dtype][dev]}
                self.bemoss_publish(target=dev, topic=topic, message=message)
                time.sleep(1)


if __name__ == '__main__':
    test = DemandResponse()
    print "Cannot run as script"