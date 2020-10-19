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

import importlib
import json
import logging
import sys

import settings
from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent


# Step1: Agent Initialization

agent_id = None
# 1. @params agent

# @paths
PROJECT_DIR = settings.PROJECT_DIR
Agents_Launch_DIR = settings.Agents_Launch_DIR

class ApprovalHelperAgent(BEMOSSAgent):

    def __init__(self, *args, **kwargs):
        super(ApprovalHelperAgent, self).__init__(*args, **kwargs)
        sys.path.append(PROJECT_DIR)
        db_host = settings.DATABASES['default']['HOST']
        db_port = settings.DATABASES['default']['PORT']
        db_database = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        self.subscribe('device_config', self.send_authorization_code)
        self.subscribe('get_device_username',self.get_device_username)
        self.run()

    def get_device_username(self,dbcon, sender, topic, message):
        print "ApprovalHelperAgent got\nTopic: {topic}".format(topic=topic)
        print "Message: {message}\n".format(message=message)
        messagejson = message
        agent_id = messagejson['agent_id']
        #topic: to/approvalhelperagent/get_devie_username/from/<entity>/<optional: republished>
        topic_list = topic.split('/')
        self.return_entity = sender
        try:
            dbcon.execute("SELECT device_model, device_type_id, address, config FROM device_info WHERE agent_id=%s",(agent_id,))
            _device_info = dbcon.fetchone()
            device_model = _device_info[0]
            device_type_id = _device_info[1]
            address = _device_info[2]
            self.device_config = _device_info[3]
            username=self.device_config.get("username") #
            password=self.device_config.get("password")#
            if self.is_gateway_device(dbcon,agent_id):
                gateway_id = self.getgateway_id(dbcon, agent_id)
                self.bemoss_publish("gatewayagent","gateway_device_authorize_"+str(gateway_id),agent_id)
            else:
                dbcon.execute("SELECT api_name FROM supported_devices WHERE device_model=%s", (device_model,))  #
                api_name = dbcon.fetchone()[0]
                apiLib = importlib.import_module("DeviceAPI." + api_name)
                DeviceAPI = apiLib.API(model=device_model, device_type=device_type_id, api=api_name,
                                       address=address,
                                       username=username, password=password, agent_id=agent_id)

                username = DeviceAPI.query_username()

                self.device_config["username"]= username
                self.update_authorization_code(dbcon,agent_id)
        except Exception as er:
            print er
            print('Username not acquired.')

    def update_authorization_code(self,dbcon,agent_id):
            reply = dict()
            if self.device_config:
                dbcon.execute("UPDATE device_info SET config=%s WHERE agent_id=%s",
                                 (json.dumps(self.device_config),agent_id))
                dbcon.commit()
                reply['flag'] = 1
                reply['agent_id'] = agent_id

            else:
                reply['flag'] = 0

        # _launch_file = os.path.join(Agents_Launch_DIR, hue_id+".launch.json")
        # f = open(_launch_file, 'r')
        # data = json.load(f)
        # ip_addr = data['address'].replace(":80", "")
        # try:
        #     hue_hub_name = self.query_hue_hub(ip_addr)
        #     f.close()
        #     reply = dict()
        #     if hue_hub_name:
        #
        #         dbcon.execute("UPDATE device_info SET username=%s WHERE agent_id=%s",
        #                          (hue_hub_name, hue_id))
        #         dbcon.commit()
        #         reply['flag'] = 1
        #         reply['mac'] = hue_id[4:].lower()
        #     else:
        #         reply['flag'] = 0

            message_reply = json.dumps(reply)
            message_reply = message_reply.encode(encoding='utf_8')
            self.bemoss_publish(target=self.return_entity,topic='get_device_username_response',message=message_reply)

    def send_authorization_code(self, dbcon, sender, topic, message):

        for agent_id,username in message.items():
            self.device_config=self.getdevice_config(dbcon,agent_id)
            self.device_config['username']=username
            self.update_authorization_code(dbcon,agent_id)







    # def query_hue_hub(self, ip_addr):
    #     # newdeveloper is for the old version of Hue hub, might no longer be useful in future version.
    #     url = ip_addr+'/api/newdeveloper'
    #     req = requests.get(url)
    #     result = json.loads(req.content)
    #     message = json.dumps(result)
    #     message = message.encode(encoding='utf_8')
    #
    #     substring = "unauthorized user"
    #     no_name = substring in message
    #
    #     if no_name:
    #         cnt = 60
    #         while cnt > 0:
    #             body = {"devicetype":"my_hue_app#bemoss"}
    #             url = ip_addr+'/api'
    #
    #             r = requests.post(url, json.dumps(body))
    #             print r.content
    #             substring = "link button not pressed"
    #             if substring in r.content:
    #                 time.sleep(0.5)
    #                 cnt -= 1
    #                 print cnt
    #             else:
    #                 exp = '\"username\":\"(.*?)\"'
    #                 pattern = re.compile(exp, re.S)
    #                 result = re.findall(pattern, r.content)
    #                 hub_name = result[0]
    #                 break
    #     else:
    #         hub_name = 'newdeveloper'
    #
    #     return hub_name


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    print "This agent cannot be run as script."

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
