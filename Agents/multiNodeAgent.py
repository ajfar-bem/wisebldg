from __future__ import absolute_import

import base64
import json
import logging
import re
import subprocess
import sys
from datetime import datetime

import pytz
import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator
import time
from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
from bemoss_lib.utils import db_helper
from bemoss_lib.utils.BEMOSS_globals import *

__version__ = '3.0'

STMS = '~*~' #Sender topic message separator

def jsonify(sender, topic, msg):
    """ json encode the message and prepend the topic """
    return STMS.join([sender,topic,json.dumps({'message':msg})])

def dejsonify(sender_topic_msg):
    """ Inverse of """
    sender, topic, msg = sender_topic_msg.split(STMS)
    msg = json.loads(msg)
    return sender,topic,msg


node_devices_table = settings.DATABASES['default']['TABLE_node_device']

class MultiNodeAgent(BEMOSSAgent):

    def __init__(self, *args, **kwargs):
        super(MultiNodeAgent, self).__init__(*args, **kwargs)
        self.multinode_status = dict()
        self.getMultinodeData()
        self.agent_id = 'multinodeagent'
        self.is_parent = False
        self.last_sync_with_parent = datetime(1991, 1, 1) #equivalent to -ve infinitive
        self.parent_node = None
        self.recently_online_node_list = []  # initialize to lists to empty
        self.recently_offline_node_list = []  # they will be filled as nodes are discovered to be online/offline
        self.setup()

        self.runPeriodically(self.send_heartbeat,20)
        self.runPeriodically(self.check_health,60,start_immediately=False)
        self.runPeriodically(self.sync_all_with_parent,600)
        self.subscribe('relay_message',self.relayDirectMessage)
        self.subscribe('update_multinode_data',self.updateMultinodeData)
        self.runContinuously(self.pollClients)
        self.run()


    def getMultinodeData(self):
        self.multinode_data = db_helper.get_multinode_data()

        self.nodelist_dict = {node['name']:node for node in self.multinode_data['known_nodes']}
        self.node_name_list = [node['name'] for node in self.multinode_data['known_nodes']]
        self.address_list = [node['address'] for node in self.multinode_data['known_nodes']]
        self.server_key_list = [node['server_key'] for node in self.multinode_data['known_nodes']]
        self.node_name = self.multinode_data['this_node']

        for index,node in enumerate(self.multinode_data['known_nodes']):
            if node['name'] == self.node_name:
                self.node_index = index
                break
        else:
            raise ValueError('"this_node:" entry on the multinode_data json file is invalid')


        for node_name in self.node_name_list: #initialize all nodes data
            if node_name not in self.multinode_status: #initialize new nodes. There could be already the node if this getMultiNode
                # data is being called later
                self.multinode_status[node_name] = dict()
                self.multinode_status[node_name]['health'] = -10 #initialized; never online/offline
                self.multinode_status[node_name]['last_sync_time'] = datetime(1991,1,1)
                self.multinode_status[node_name]['last_online_time'] = None
                self.multinode_status[node_name]['last_offline_time'] = None
                self.multinode_status[node_name]['last_scanned_time'] = None

    def setup(self):
        print "Setup"

        base_dir = settings.PROJECT_DIR + "/"
        public_keys_dir = os.path.abspath(os.path.join(base_dir, 'public_keys'))
        secret_keys_dir = os.path.abspath(os.path.join(base_dir, 'private_keys'))

        self.secret_keys_dir = secret_keys_dir
        self.public_keys_dir = public_keys_dir

        if not (os.path.exists(public_keys_dir) and
                    os.path.exists(secret_keys_dir)):
            logging.critical("Certificates are missing - run generate_certificates.py script first")
            sys.exit(1)

        ctx = zmq.Context.instance()
        self.ctx = ctx
        # Start an authenticator for this context.
        self.auth = ThreadAuthenticator(ctx)
        self.auth.start()
        self.configure_authenticator()

        server = ctx.socket(zmq.PUB)

        server_secret_key_filename = self.multinode_data['known_nodes'][self.node_index]['server_secret_key']
        server_secret_file = os.path.join(secret_keys_dir, server_secret_key_filename)
        server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
        server.curve_secretkey = server_secret
        server.curve_publickey = server_public
        server.curve_server = True  # must come before bind
        server.bind(self.multinode_data['known_nodes'][self.node_index]['address'])
        self.server = server
        self.configureClient()

    def configure_authenticator(self):
        self.auth.allow()
        # Tell authenticator to use the certificate in a directory
        self.auth.configure_curve(domain='*', location=self.public_keys_dir)


    def disperseMessage(self, sender, topic, message):
        for node_name in self.node_name_list:
            if node_name == self.node_name:
                continue
            self.server.send(jsonify(sender, node_name+'/republish/'+topic,message))

    def republishToParent(self,sender, topic,message):
        if self.is_parent:
            return #if I am parent, the message is already published
        for node_name in self.node_name_list:
            if self.multinode_status[node_name]['health'] == 2: #health = 2 is the parent node
                self.server.send(jsonify(sender, node_name+'/republish/'+topic,message))


    def sync_node_with_parent(self, node_name):
        if self.is_parent:
            print "Syncing " + node_name
            self.last_sync_with_parent = datetime.now()
            sync_date_string = self.last_sync_with_parent.strftime('%B %d, %Y, %H:%M:%S')
            # os.system('pg_dump bemossdb -f ' + self.self_database_dump_path)
            # with open(self.self_database_dump_path, 'r') as f:
            #     file_content = f.read()
            # msg = {'database_dump': base64.b64encode(file_content)}
            self.server.send(
                jsonify(self.node_name, node_name + '/sync-with-parent/' + sync_date_string + '/'+self.node_name, ""))


    def sync_all_with_parent(self,dbcon):

        if self.is_parent:
            self.last_sync_with_parent = datetime.now()
            sync_date_string = self.last_sync_with_parent.strftime('%B %d, %Y, %H:%M:%S')
            print "Syncing all nodes"
            for node_name in self.node_name_list:
                if node_name == self.node_name:
                    continue
                # os.system('pg_dump bemossdb -f ' + self.self_database_dump_path)
                # with open(self.self_database_dump_path, 'r') as f:
                #     file_content = f.read()
                # msg = {'database_dump': base64.b64encode(file_content)}
                self.server.send(
                    jsonify(self.node_name, node_name + '/sync-with-parent/' + sync_date_string + '/' + self.node_name, ""))


    def send_heartbeat(self,dbcon):
        #self.vip.pubsub.publish('pubsub', 'listener', None, {'message': 'Hello Listener'})
        #print 'publishing'
        print "Sending heartbeat"

        last_sync_string = self.last_sync_with_parent.strftime('%B %d, %Y, %H:%M:%S')
        self.server.send(jsonify(self.node_name,'heartbeat/' + self.node_name + '/' + str(self.is_parent) + '/' + last_sync_string,""))

    def extract_ip(self,addr):
        return re.search(r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})', addr).groups()[0]

    def getNodeId(self, node_name):

        for index, node in enumerate(self.multinode_data['known_nodes']):
            if node['name'] == node_name:
                node_index = index
                break
        else:
            raise ValueError('the node name: ' + node_name + ' is not found in multinode data')

        return node_index

    def getNodeName(self, node_id):
        return self.multinode_data['known_nodes'][node_id]['name']

    def handle_offline_nodes(self, dbcon, node_name_list):
        if self.is_parent:
            # start all the agents belonging to that node on this node
            command_group = []
            for node_name in node_name_list:
                node_id = self.getNodeId(node_name)
                #put the offline event into cassandra events log table, and also create notification
                self.EventRegister(dbcon, 'node-offline',reason='communication-error',source=node_name)
                # get a list of agents that were supposedly running in that offline node
                dbcon.execute("SELECT agent_id FROM " + node_devices_table + " WHERE assigned_node_id=%s",
                            (node_id,))

                if dbcon.rowcount:
                    agent_ids = dbcon.fetchall()

                    for agent_id in agent_ids:
                        message = dict()
                        message[STATUS_CHANGE.AGENT_ID] = agent_id[0]
                        message[STATUS_CHANGE.NODE] = str(self.node_index)
                        message[STATUS_CHANGE.AGENT_STATUS] = 'start'
                        message[STATUS_CHANGE.NODE_ASSIGNMENT_TYPE] = ZONE_ASSIGNMENT_TYPES.TEMPORARY
                        command_group += [message]
                        dbcon.execute("UPDATE " + node_devices_table + " SET current_node_id=(%s), date_move=(%s)"
                                                                             " WHERE agent_id=(%s)",
                                            (self.node_index, datetime.now(pytz.UTC), agent_id[0]))
                        dbcon.commit()
            print "moving agents from offline node to parent: " + str(node_name_list)
            print command_group
            if command_group:
                self.bemoss_publish(target='networkagent', topic='status_change', message=command_group)

    def handle_online_nodes(self, dbcon, node_name_list):
        if self.is_parent:
            # start all the agents belonging to that nodes back on them
            command_group = []
            for node_name in node_name_list:

                node_id = self.getNodeId(node_name)
                if self.node_index == node_id:
                    continue #don't handle self-online
                self.EventRegister(dbcon, 'node-online',reason='communication-restored',source=node_name)

                #get a list of agents that were supposed to be running in that online node
                dbcon.execute("SELECT agent_id FROM " + node_devices_table + " WHERE assigned_node_id=%s",
                                    (node_id,))
                if dbcon.rowcount:
                    agent_ids = dbcon.fetchall()
                    for agent_id in agent_ids:
                        message = dict()
                        message[STATUS_CHANGE.AGENT_ID] = agent_id[0]
                        message[STATUS_CHANGE.NODE_ASSIGNMENT_TYPE] = ZONE_ASSIGNMENT_TYPES.PERMANENT
                        message[STATUS_CHANGE.NODE] = str(self.node_index)
                        message[STATUS_CHANGE.AGENT_STATUS] = 'stop'  #stop in this node
                        command_group += [message]
                        message = dict(message) #create another copy
                        message[STATUS_CHANGE.NODE] = str(node_id)
                        message[STATUS_CHANGE.AGENT_STATUS] = 'start' #start in the target node
                        command_group += [message]
                        #immediately update the multnode device assignment table
                        dbcon.execute("UPDATE " + node_devices_table + " SET current_node_id=(%s), date_move=(%s)"
                                                                             " WHERE agent_id=(%s)", (node_id, datetime.now(pytz.UTC), agent_id[0]))
                        dbcon.commit()


            print "Moving agents back to the online node: " + str(node_name_list)
            print command_group

            if command_group:
                self.bemoss_publish(target='networkagent',topic='status_change',message=command_group)

    def updateParent(self,dbcon, parent_node_name):
        parent_ip = self.extract_ip(self.nodelist_dict[parent_node_name]['address'])
        write_new = False
        if not os.path.isfile(settings.MULTINODE_PARENT_IP_FILE):  # but parent file doesn't exists
            write_new = True
        else:
            with open(settings.MULTINODE_PARENT_IP_FILE, 'r') as f:
                read_ip = f.read()
            if read_ip != parent_ip:
                write_new = True
        if write_new:
            with open(settings.MULTINODE_PARENT_IP_FILE, 'w') as f:
                f.write(parent_ip)
            if dbcon:
                dbcon.close() #close old connection
            dbcon = db_helper.db_connection() #start new connection using new parent_ip
            self.updateMultinodeData(sender=self.name,topic='update_parent',message="")

    def check_health(self, dbcon):

        for node_name, node in self.multinode_status.items():
            if node['health'] > 0 : #initialize all online nodes to 0. If they are really online, they should change it
                #  back to 1 or 2 (parent) within 30 seconds throught the heartbeat.
                node['health'] = 0

        time.sleep(30)
        parent_node_name = None #initialize parent node
        online_node_exists = False
        for node_name, node in self.multinode_status.items():
            node['last_scanned_time'] = datetime.now()
            if node['health'] == 0:
                node['health'] = -1
                node['last_offline_time'] = datetime.now()
                self.recently_offline_node_list += [node_name]
            elif node['health'] == -1: #offline since long
                pass
            elif node['health'] == -10: #The node was initialized to -10, and never came online. Treat it as recently going
                # offline for this iteration so that the agents that were supposed to be running there can be migrated
                node['health'] = -1
                self.recently_offline_node_list += [node_name]
            elif node['health'] == 2: #there is some parent node present
                parent_node_name = node_name
            if node['health'] >0:
                online_node_exists = True #At-least one node (itself) should be online, if not some problem

        assert online_node_exists, "At least one node (current node) must be online"

        if not parent_node_name: #parent node doesn't exist
            #find a suitable node to elect a parent. The node with latest update from previous parent wins. If there is
            #tie, then the node coming earlier in the node-list on multinode data wins

            online_node_last_sync = dict() #only the online nodes, and their last-sync-times
            for node_name, node in self.multinode_status.items(): #copy only the online nodes
                if node['health'] > 0:
                    online_node_last_sync[node_name] = node['last_sync_time']

            latest_node = max(online_node_last_sync,key=online_node_last_sync.get)
            latest_sync_date = online_node_last_sync[latest_node]

            for node_name in self.node_name_list:
                if self.multinode_status[node_name]['health'] <= 0: #dead nodes can't be parents
                    continue
                if self.multinode_status[node_name]['last_sync_time'] == latest_sync_date: # this is the first node with the latest update from parent
                    #elligible parent found
                    self.updateParent(dbcon, node_name)

                    if node_name == self.node_name: # I am the node, so I get to become the parent
                        self.is_parent = True
                        print "I am the boss now, " + self.node_name
                        break
                    else: #I-am-not-the-first-node with latest update; somebody else is
                        self.is_parent = False
                        break
        else: #parent node exist
            self.updateParent(dbcon,parent_node_name)

        for node in self.multinode_data['known_nodes']:
            print node['name'] + ': ' + str(self.multinode_status[node['name']]['health'])

        if self.is_parent:
            #if this is a parent node, update the node_info table
            if dbcon is None: #if no database connection exists make connection
                dbcon = db_helper.db_connection()

            tbl_node_info =  settings.DATABASES['default']['TABLE_node_info']
            dbcon.execute('select node_id from '+ tbl_node_info)
            to_be_deleted_node_ids = dbcon.fetchall()
            for index, node in enumerate(self.multinode_data['known_nodes']):
                if (index,) in to_be_deleted_node_ids:
                    to_be_deleted_node_ids.remove((index,)) #don't remove this current node
                result = dbcon.execute('select * from ' + tbl_node_info + ' where node_id=%s',(index,))
                node_type = 'parent' if self.multinode_status[node['name']]['health'] == 2 else "child"
                node_status = "ONLINE" if self.multinode_status[node['name']]['health'] > 0 else "OFFLINE"
                ip_address = self.extract_ip(node['address'])
                last_scanned_time = self.multinode_status[node['name']]['last_online_time']
                last_offline_time = self.multinode_status[node['name']]['last_offline_time']
                last_sync_time = self.multinode_status[node['name']]['last_sync_time']

                var_list = "(node_id,node_name,node_type,node_status,ip_address,last_scanned_time,last_offline_time,last_sync_time)"
                value_placeholder_list = "(%s,%s,%s,%s,%s,%s,%s,%s)"
                actual_values_list = (index, node['name'],node_type, node_status, ip_address, last_scanned_time, last_offline_time, last_sync_time)

                if dbcon.rowcount == 0:
                    dbcon.execute("insert into " + tbl_node_info + " " + var_list +" VALUES" + value_placeholder_list, actual_values_list )
                else:
                    dbcon.execute(
                        "update " + tbl_node_info + " SET " + var_list + " = " + value_placeholder_list + " where node_id = %s",
                        actual_values_list+(index,))
            dbcon.commit()

            for id in to_be_deleted_node_ids:
                dbcon.execute('delete from accounts_userprofile_nodes where nodeinfo_id=%s',id) #delete entries in user-profile for the old node
                dbcon.commit()
                dbcon.execute('delete from ' + tbl_node_info + ' where node_id=%s',id) #delete the old nodes
                dbcon.commit()



            if self.recently_online_node_list: #Online nodes should be handled first because, the same node can first be
                #on both recently_online_node_list and recently_offline_node_list, when it goes offline shortly after
                #coming online
                self.handle_online_nodes(dbcon, self.recently_online_node_list)
                self.recently_online_node_list = []  # reset after handling
            if self.recently_offline_node_list:
                self.handle_offline_nodes(dbcon, self.recently_offline_node_list)
                self.recently_offline_node_list = []  # reset after handling


    def connect_client(self,node):
        server_public_file = os.path.join(self.public_keys_dir, node['server_key'])
        server_public, _ = zmq.auth.load_certificate(server_public_file)
        # The client must know the server's public key to make a CURVE connection.
        self.client.curve_serverkey = server_public
        self.client.setsockopt(zmq.SUBSCRIBE, 'heartbeat/')
        self.client.setsockopt(zmq.SUBSCRIBE, self.node_name)
        self.client.connect(node['address'])

    def disconnect_client(self,node):
        self.client.disconnect(node['address'])


    def configureClient(self):
        print "Starting to receive Heart-beat"
        client = self.ctx.socket(zmq.SUB)
        # We need two certificates, one for the client and one for
        # the server. The client must know the server's public key
        # to make a CURVE connection.

        client_secret_key_filename = self.multinode_data['known_nodes'][self.node_index]['client_secret_key']
        client_secret_file = os.path.join(self.secret_keys_dir,client_secret_key_filename)
        client_public, client_secret = zmq.auth.load_certificate(client_secret_file)
        client.curve_secretkey = client_secret
        client.curve_publickey = client_public

        self.client = client

        for node in self.multinode_data['known_nodes']:
            self.connect_client(node)

    def pollClients(self,dbcon):
        if self.client.poll(1000):
            sender,topic,msg = dejsonify(self.client.recv())
            topic_list = topic.split('/')
            if topic_list[0]=='heartbeat':
                node_name = sender
                is_parent = topic_list[2]
                last_sync_with_parent = topic_list[3]
                if self.multinode_status[node_name]['health'] < 0: #the node health was <0 , means offline
                    print node_name + " is back online"
                    self.recently_online_node_list += [node_name]
                    self.sync_node_with_parent(node_name)

                if is_parent.lower() in ['false','0']:
                    self.multinode_status[node_name]['health'] = 1
                elif is_parent.lower() in ['true','1']:
                    self.multinode_status[node_name]['health'] = 2
                    self.parent_node = node_name
                else:
                    raise ValueError('Invalid is_parent string in heart-beat message')

                self.multinode_status[node_name]['last_online_time'] = datetime.now()
                self.multinode_status[node_name]['last_sync_time'] = datetime.strptime(last_sync_with_parent,
                                                                                       '%B %d, %Y, %H:%M:%S')

            if topic_list[0]==self.node_name:
                if topic_list[1] == 'sync-with-parent':
                    pass
                    # print topic
                    # self.last_sync_with_parent = datetime.strptime(topic_list[2], '%B %d, %Y, %H:%M:%S')
                    # content = base64.b64decode(msg['database_dump'])
                    # newpath = 'bemossdb.sql'
                    # with open(newpath, 'w') as f:
                    #     f.write(content)
                    # try:
                    #     os.system(
                    #         'psql -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid();"')
                    #     os.system(
                    #         'dropdb bemossdb')  # This step requires all connections to be closed
                    #     os.system('createdb bemossdb -O admin')
                    #     dump_result = subprocess.check_output('psql bemossdb < ' + newpath, shell=True)
                    # except Exception as er:
                    #     print "Couldn't sync database with parent because of error: "
                    #     print er
                    #
                    # parent_node_name = topic_list[3]
                    # self.updateParent(parent_node_name)

                if topic_list[1] == 'republish':
                    target = msg['target']
                    actual_message = msg['actual_message']
                    actual_topic = msg['actual_topic']
                    self.bemoss_publish(target=target,topic=actual_topic+'/republished',message=actual_message,sender=sender)

            print self.node_name+": "+topic, str(msg)

        else:
            time.sleep(2)


    def cleanup(self):
        # stop auth thread
        self.auth.stop()


    def updateMultinodeData(self, dbcon, sender, topic, message):
        print "Updating Multinode data"
        topic_list = topic.split('/')
        self.configure_authenticator()
        #to/multinodeagent/from/<doesn't matter>/update_multinode_data
        if topic_list[4] == 'update_multinode_data':
            old_multinode_data = self.multinode_data
            self.getMultinodeData()
            for node in self.multinode_data['known_nodes']:
                if node not in old_multinode_data['known_nodes']:
                    print "New node has been added to the cluster: " + node['name']
                    print "We will connect to it"
                    self.connect_client(node)

            for node in old_multinode_data['known_nodes']:
                if node not in self.multinode_data['known_nodes']:
                    print "Node has been removed from the cluster: " + node['name']
                    print "We will disconnect from it"
                    self.disconnect_client(node)
                    # TODO: remove it from the node_info table

        print "yay! got it"

    def relayDirectMessage(self, dbcon, sender, topic, message):
        print topic
        #to/<some_agent_or_ui>/topic/from/<some_agent_or_ui>

        from_entity = sender
        target = message['target']
        actual_message = message['actual_message']
        actual_topic = message['actual_topic']

        for to_entity in target:
            if to_entity in settings.NO_FORWARD_AGENTS:
                return #no forwarding should be done for these agents
            elif to_entity in settings.PARENT_NODE_SYSTEM_AGENTS :
                if not self.is_parent:
                    self.republishToParent(sender, topic,message)
            elif to_entity == "ALL":
                self.disperseMessage(sender,topic=topic,message=message)
            else:
                dbcon.execute("SELECT current_node_id FROM " + node_devices_table + " WHERE agent_id=%s",
                                    (to_entity,))
                if dbcon.rowcount:
                    node_id = dbcon.fetchone()[0]
                    if node_id != self.node_index:
                        self.server.send(jsonify(sender,self.getNodeName(node_id) + '/republish/' + topic, message))
                else:
                    self.disperseMessage(sender, topic, message) #republish to all nodes if we don't know where to send



def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    print "This agent cannot be run as script."


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
