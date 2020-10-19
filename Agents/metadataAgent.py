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

import sys
from collections import deque

from bemoss_lib.databases.cassandraAPI import cassandraDB
from bemoss_lib.utils import date_converter

__version__ = '3.0'

from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils import db_helper


class MetadataAgent(BEMOSSAgent):
    def __init__(self, *args, **kwargs):
        super(MetadataAgent, self).__init__(*args,**kwargs)
        self.insert_message_queue = deque()
        self.actual_dbcon = db_helper.actual_db_connection()
        self.subscribe('dbrpc',self.processCommand)
        self.run()

    def extract_pipe(self,reduced_pipe):
        rebuild_func = reduced_pipe[0]
        return rebuild_func(*reduced_pipe[1])

    def processCommand(self,dbcon, sender,topic,message):
        return_pipe = self.extract_pipe(message["reduced_return_pipe"])
        message = message["actual_message"]
        command = message['command']
        if command=='fetchone':
            try:
                self.actual_dbcon.execute(*message['args'],**message['kwargs'])
            except Exception as er:
                rowcount = -1 #negative for error
                result = "Exception: " + str(er)
            else:
                rowcount = self.actual_dbcon.rowcount
                result = self.actual_dbcon.fetchone()
            return_pipe.send((result, rowcount))
        elif command=='fetchall':
            try:
                self.actual_dbcon.execute(*message['args'], **message['kwargs'])
            except Exception as er:
                rowcount = -1 #negative for error
                result = "Exception: " + str(er)
            else:
                rowcount = self.actual_dbcon.rowcount
                result = self.actual_dbcon.fetchall()
            return_pipe.send((result, rowcount))
        elif command == 'rowcount':
            try:
                self.actual_dbcon.execute(*message['args'], **message['kwargs'])
            except Exception as er:
                rowcount = -1 #negative for error
                result = "Exception: " + str(er)
            else:
                rowcount = self.actual_dbcon.rowcount
                result = None
            return_pipe.send((result, rowcount))
        elif command == "commit":
            try:
                self.actual_dbcon.execute(*message['args'], **message['kwargs'])
                self.actual_dbcon.commit()
            except Exception as er:
                rowcount = -1  # negative for error
                result = "Exception: " + str(er)
            else:
                rowcount = 0  # negative for error
                result = True

            return_pipe.send((result, rowcount))


def main(argv=sys.argv):
    print "This agent cannot be run as script."


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
