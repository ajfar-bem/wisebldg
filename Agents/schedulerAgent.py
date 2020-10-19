# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright (c) 2015, Battelle Memorial Institute
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.
#

# This material was prepared as an account of work sponsored by an
# agency of the United States Government.  Neither the United States
# Government nor the United States Department of Energy, nor Battelle,
# nor any of their employees, nor any jurisdiction or organization
# that has cooperated in the development of these materials, makes
# any warranty, express or implied, or assumes any legal liability
# or responsibility for the accuracy, completeness, or usefulness or
# any information, apparatus, product, software, or process disclosed,
# or represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or
# service by trade name, trademark, manufacturer, or otherwise does
# not necessarily constitute or imply its endorsement, recommendation,
# r favoring by the United States Government or any agency thereof,
# or Battelle Memorial Institute. The views and opinions of authors
# expressed herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY
# operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830

#}}}

from __future__ import absolute_import

import logging
import sys
import time
import uuid
from collections import deque

from bemoss_lib.databases.cassandraAPI import cassandraDB
from bemoss_lib.utils import date_converter
import datetime

_log = logging.getLogger(__name__)
__version__ = '3.0'

from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils import db_helper
from threading import Lock


weekdays = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

class SchedulerAgent(BEMOSSAgent):
    def __init__(self, *args, **kwargs):
        super(SchedulerAgent, self).__init__(*args,**kwargs)
        self.dblock = Lock()
        self.runPeriodically(self.check_schedules,60)
        self.subscribe(topic='triggerSchedule',callback=self.triggerSchedule)

        self.run()

    def check_schedules(self,dbcon):
        #scan through all the schedules to see if it is time to do something
        weekday_num = datetime.datetime.now().weekday()
        minutes = datetime.datetime.now().hour*60 + datetime.datetime.now().minute

        weekday = weekdays[weekday_num]
        schedules = []
        with self.dblock:
            dbcon.execute("SELECT agent_id, schedule FROM schedule_data")
        if dbcon.rowcount != 0:
            schedules = dbcon.fetchall()

        self.debugLog(__name__,payload="Checking schedules")
        for agent_id, schedule in schedules:
            try:
                everyday_schedule = schedule['schedulers']['everyday']
                todays_schedule = everyday_schedule[weekday]
                for transition in todays_schedule:
                    if int(transition.get('at')) == minutes: #transition time matches with current minute
                        control_dict = self.get_control_msg(transition,agent_id)
                        self.infoLog(__name__, payload=control_dict,header="scheduleragent/"+agent_id)
                        self.bemoss_publish(target='basicagent', topic='update', message=control_dict)
            except KeyError, TypeError:
                continue

    def get_control_msg(self,sch,agent_id):
        control_dict = {}
        for key, val in sch.items():
            if key not in ['at', 'id', 'nickname']:
                control_dict[key] = val
        control_dict['agent_id'] = agent_id
        return control_dict

    def triggerSchedule(self,dbcon,sender,topic,message):
        agent_id = message['agent_id']
        schedule = {}
        with self.dblock:
            dbcon.execute("SELECT schedule FROM schedule_data where agent_id=%s",(agent_id,))
        if dbcon.rowcount != 0:
            schedule = dbcon.fetchone()[0]

        everyday_schedule = schedule['schedulers']['everyday']
        weekday_num = datetime.datetime.now().weekday()
        minutes = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
        weekday = weekdays[weekday_num]
        todays_schedule = everyday_schedule[weekday]
        yesterday_num = weekday_num -1
        yesterday = weekdays[yesterday_num]
        control_dict = self.get_control_msg(everyday_schedule[yesterday][-1],agent_id)

        for transition in todays_schedule:
            if int(transition.get('at')) <= minutes: #transition time matches with current minute
                control_dict = self.get_control_msg(transition, agent_id)

        self.bemoss_publish(target='basicagent', topic='update', message=control_dict)
        self.bemoss_publish(target=sender,topic='triggerScheduleResponse',message=control_dict)

def main(argv=sys.argv):
    print "This agent cannot be run as script."


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
