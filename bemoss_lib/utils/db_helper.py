__author__ = 'root'

import settings
import psycopg2
import json
import time
db_database = settings.DATABASES['default']['NAME']
db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']
db_table_node_device = settings.DATABASES['default']['TABLE_node_device']
db_table_device_info = settings.DATABASES['default']['TABLE_device_info']
db_table_node_info = settings.DATABASES['default']['TABLE_node_info']

def get_approved_devices(cur, node=None, zone_type='current'):
    approved_devices = []
    cur.execute("SELECT agent_id,device_type_id, approval_status FROM "+db_table_device_info)
    if cur.rowcount != 0:
        rows = cur.fetchall()
        for row in rows:
            cur.execute("SELECT assigned_node_id,current_node_id FROM "+db_table_node_device+" WHERE agent_id=%s",
                     (row[0],))
            if cur.rowcount == 0:
                print 'No info found for agent. Ignore'
                continue
            zone_info = cur.fetchone()
            new_node = zone_info[1]
            old_node = zone_info[0]
            if row[2].upper() in ['APR','APPROVED']:
                if (node==None or (zone_type== 'current' and new_node==node) or (zone_type== 'old' and old_node==node)):
                    approved_devices += [row[0]]
    return approved_devices

def get_device_nickname(cur,agent_id):
    nickname = ''
    try:
        cur.execute("SELECT nickname FROM "+db_table_device_info+" WHERE agent_id=%s",(agent_id,))
        if cur.rowcount !=0:
            nickname = cur.fetchone()[0]
    except:
        nickname=''

    return nickname


class db_connection(object):
    #A shadow db_connection class, that actually uses RPC call to metadataagent to get/save data.
    def __init__(self,parent):
        self.args = None
        self.kwargs = None
        self.resultrowcount = None
        self.parent = parent #parent agent
        self.result = None

    def execute(self,*args,**kwargs):
        self.args = args
        self.kwargs = kwargs

    def fetchone(self):
        self.result, self.resultrowcount = self.parent.dbrpc('fetchone',self.args,self.kwargs)
        if self.resultrowcount == -1:
            raise Exception(self.result)
        else:
            return self.result

    def fetchall(self):
        self.result, self.resultrowcount = self.parent.dbrpc('fetchall',self.args,self.kwargs)
        if self.resultrowcount == -1:
            raise Exception(self.result)
        else:
            return self.result

    @property
    def rowcount(self):
        self.result, self.resultrowcount = self.parent.dbrpc('rowcount',self.args,self.kwargs)
        if self.resultrowcount == -1:
            raise Exception(self.result)
        else:
            return self.resultrowcount

    def commit(self):
        self.result, self.resultrowcount = self.parent.dbrpc('commit', self.args, self.kwargs)
        if self.resultrowcount == -1:
            raise Exception(self.result)
        else:
            return self.resultrowcount

    def close(self): #virtual db_connection don't need to be closed
        return True




class actual_db_connection(object):

    def __init__(self):
        self.database_connect()

    def database_connect(self):
        connection_successful = False
        while not connection_successful:
            try:
                with open(settings.MULTINODE_PARENT_IP_FILE, 'r') as f:
                    self.parent_ip = f.read().strip()
                self.con = psycopg2.connect(host=self.parent_ip, port=db_port, database=db_database,
                                            user=db_user,
                                            password=db_password)
                self.cur = self.con.cursor()  # open a cursor to perfomm database operations

                print("connects to the database name {} successfully at {}".format(db_database,self.parent_ip))
                connection_successful = True
            except IOError as er:
                print "Parent IP file doesn't exist. Waiting for it to be created"
                time.sleep(1)
            except psycopg2.Error as er:
                print("Database down".format(db_database))
                print er
                print "Retrying again in 1 second"
                time.sleep(1)


    def reconnector(func):
        def reconnect(*args,**kwargs):
            self = args[0]
            retry_counter = 0
            while True:
                try:
                    #print "Running db-operation-on: " + str(self.parent_ip)
                    return func(*args,**kwargs)
                except psycopg2.IntegrityError as er:
                    raise
                except psycopg2.Error as er:
                    print er
                    self = args[0] #extract refernce to self
                    self.database_connect()
                    time.sleep(1)
                    if retry_counter > 5:
                        raise
                    retry_counter += 1
        return reconnect

    @reconnector
    def execute(self,*args,**kwargs):
        return self.cur.execute(*args,**kwargs)

    @reconnector
    def fetchone(self,*args,**kwargs):
        return self.cur.fetchone(*args,**kwargs)

    @reconnector
    def fetchall(self, *args, **kwargs):
        return self.cur.fetchall(*args, **kwargs)

    @property
    @reconnector
    def rowcount(self):
        return self.cur.rowcount

    @reconnector
    def commit(self):
        return self.con.commit()

    def close(self):
        return self.con.close()


def makestr(input): #convert unicode to str recursively
    if isinstance(input, dict):
        return {makestr(key): makestr(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [makestr(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def get_multinode_data():
    multinode_data_path = settings.MULTINODE_DATA_PATH
    with open(multinode_data_path, 'r') as f:
        multinode_data = makestr(json.load(f))
    return multinode_data

def get_node_id():
    multinode_data = get_multinode_data()
    node_name = multinode_data['this_node']
    for index,node in enumerate(multinode_data['known_nodes']):
        if node['name'] == node_name:
            return index
    else:
        raise ValueError('"this_node:" entry on the multinode_data json file is invalid')