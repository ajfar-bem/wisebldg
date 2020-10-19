from bemoss_lib.utils.BEMOSS_globals import APPROVAL_STATUS
from bemoss_lib.utils.SimpleWebSocketServer import SimpleSSLWebSocketServer, WebSocket
from bemoss_lib.platform.BEMOSSAgent import BEMOSSAgent
import json, time, pickle, settings
from bemoss_lib.utils.find_own_ip import getIPs
import datetime
import threading


class WebSocketAgent(BEMOSSAgent):
    def __init__(self, *args, **kwargs):
        super(WebSocketAgent, self).__init__(*args, **kwargs)
        # self.agent_id = kwargs['name']
        self.runContinuously(self.runServer)
        self.run()

    def runServer(self, dbcon):

        # Main request messages format
        #
        # For discovery ----- {"TYPE": "DISCOVER", "PAYLOAD": {
        #     "MODEL_NAMES": { "On_Off Switch": None,"LightSwitch": None},""BUILDING_ID":12345}, "AUTHORIZATION_CODE": "xxxxxx"}
        #
        # For status change -{"TYPE": "CHANGE_STATUS", "PAYLOAD": {"APR": ["WNC_484389", ],"PND": [],"NBM": []},
        #                                "AUTHORIZATION_CODE": "xxxxxx"}
        #
        # For Authorize------ {"TYPE": "AUTHORIZE", "PAYLOAD": {"AGENT_ID": "Phil_0017881a4676"}, "AUTHORIZATION_CODE": "xxxxxx"}
        #
        # For Control ------- {"TYPE": "CONTROL", "PAYLOAD": {"AGENT_ID": "Sock_221609K0102348","POSTMSG": {"status":"OFF"}},
        #                     "AUTHORIZATION_CODE": "xxxxxx"}
        #
        #
        #
        class handlerClass(WebSocket):

            def __init__(self, agent, *args, **kwargs):
                self.agent = agent
                super(handlerClass, self).__init__(*args, **kwargs)


            def handleMessage(self):
                # where u get data from gateway
                try:
                    print("got this MESSAGE from IOT gateway ", self.data)
                    json_message=json.loads(self.data)   #todo bad data handling everywhere
                    if(json_message["TYPE"])=="DISCOVER":
                        self.agent.bemoss_publish(target="devicediscoveryagent", topic="gateway_discovered_devices", message=json_message["PAYLOAD"], sender=self)
                    elif (json_message["TYPE"]) == "MONITOR":
                        for element in json_message["PAYLOAD"]:
                            try:
                                for agent_id, data in element.items():
                                    self.agent.bemoss_publish(target=agent_id.encode("utf-8") , topic="gateway_monitor_data" , message=data , sender=self)
                            except Exception as e:
                                continue
                    elif (json_message["TYPE"]) == "CONTROL":
                            for agent_id, data in json_message["PAYLOAD"].items():
                                self.agent.bemoss_publish(target=agent_id.encode("utf-8"), topic="gateway_control_response",
                                                  message=data, sender=self)
                    elif (json_message["TYPE"]) == "AUTHORIZE":
                        self.agent.bemoss_publish(target="approvalhelperagent", topic="device_config",
                                                  message=json_message["PAYLOAD"], sender=self)
                    elif (json_message["TYPE"]) == "CHANGE_STATUS":
                        pass#Is this needed ?
                    elif(json_message["TYPE"]) == "FIRST TIME CONNECT":
                        self.gateway_handshake(json_message)
                        self.gateway_configure(json_message)
                    elif (json_message["TYPE"]) == "RECONNECT": #comes here only if cloud BEM went offline and gateway onneted to it
                         #wrote seperately to do some stored data fetching from gateway
                        self.gateway_handshake(json_message)
                    #todo get any stored data? or stored data is received with some specific type
                except Exception as e:
                    print (e)

            def initialise_gateway(self,gateway_id,building_id):

                info = {}
                IP, port = self.address
                info["ip_address"] = IP + ":" + str(port)
                self.agent.dbcon.execute("UPDATE iot_gateway SET gateway_settings=%s,status=%s WHERE gateway=%s",
                                         (json.dumps(info), "APR", str(gateway_id)))
                self.agent.dbcon.commit()
                self.agent.subscribe('gateway_discover' + '_' + str(building_id),self.gateway_discover)
                self.agent.subscribe('gateway_device_status_update' + '_' + str(gateway_id), self.gateway_device_status_update)
                self.agent.subscribe('gateway_device_control' + '_' + str(gateway_id), self.gateway_device_control)
                self.agent.subscribe('gateway_device_authorize' + '_' + str(gateway_id), self.gateway_device_authorize)

            def check_entry(self,gateway_details,building_id):
                time_requested = gateway_details[2]
                current_time = datetime.datetime.now()
                gateway_id=gateway_details[0]
                diff = current_time - time_requested.replace(tzinfo=None)
                time = divmod(diff.days * 86400 + diff.seconds, 60)
                if time[0] <6000 or (time[0] == 1 and time[1] == 0):
                    self.initialise_gateway(gateway_id, building_id)
                else:
                    print "deleting this entry"
                    self.agent.dbcon.execute('delete from iot_gateway where gateway=%s',
                                             (str(gateway_id),))  # deleting the entry since connection is not valid
                    self.agent.dbcon.commit()
                    self.close()

            def gateway_handshake(self,json_message):
                gateway_id = json_message["UNIQUE_ID"]
                gateway_details = self.agent.get_gateway_config(self.agent.dbcon, gateway_id)
                if gateway_details is not None:
                    building_id = gateway_details[5]
                    status = gateway_details[6]
                    if status == "PND":
                        self.check_entry(gateway_details, building_id)
                    else:
                        self.initialise_gateway(gateway_id, building_id)
                else:
                    print("No entry of connected gateway on db, so simply closing connection")
                    self.close()


            def handleConnected(self):
                print(self.address, 'connected')
                # self.senddata() #i can do handshake here

            def gateway_configure(self,json_message):

                details=dict()
                gateway_id = json_message["UNIQUE_ID"]
                gateway_details = self.agent.get_gateway_config(self.agent.dbcon, gateway_id)
                details["NAME"]=gateway_details[1]
                details["SETTINGS"]=gateway_details[3]
                details["ACCOUNT_ID"]=gateway_details[4]
                details["BUILDING_ID"]=gateway_details[5]

                try:

                    ADU=dict()
                    ADU["TYPE"]="CONFIGURE"
                    ADU["PAYLOAD"] = details
                    ADU["AUTHORIZATION_CODE"] = settings.GATEWAY_AUTHORIZATION_CODE
                    print("sending to gateway")
                    self.sendMessage(json.dumps(ADU))

                except Exception as e:
                    print("somethin went wrong")

            def gateway_discover(self, dbcon, sender, topic, message):


                try:

                    ADU=dict()
                    ADU["TYPE"]="DISCOVER"
                    ADU["PAYLOAD"] = message

                    ADU["AUTHORIZATION_CODE"] = settings.GATEWAY_AUTHORIZATION_CODE
                    print("sending to gateway")
                    self.sendMessage(json.dumps(ADU))

                except Exception as e:
                    print("somethin went wrong")

            def gateway_device_authorize(self, dbcon, sender, topic, message):

                try:

                    PDU = dict()
                    PDU["AGENT_ID"] = message
                    ADU = dict()
                    ADU["TYPE"] = "AUTHORIZE"
                    ADU["PAYLOAD"] = PDU
                    ADU["AUTHORIZATION_CODE"] = settings.GATEWAY_AUTHORIZATION_CODE
                    print("sending to gateway")
                    self.sendMessage(json.dumps(ADU))

                except Exception as e:
                    print("somethin went wrong")

            def gateway_device_status_update(self, dbcon, sender, topic, message):

                try:
                    APRlist = list()
                    PNDlist = list()
                    NBMlist = list()
                    status_change=dict()
                    ADU = dict()
                    ADU["TYPE"] = "CHANGE_STATUS"
                    for agent_id, status in message:
                        if status==APPROVAL_STATUS.APR:
                            APRlist.append(agent_id)
                        elif status==APPROVAL_STATUS.PND:
                            PNDlist.append(agent_id)
                        else:
                            NBMlist.append(agent_id)
                    status_change["APR"] = APRlist
                    status_change["PND"] = PNDlist
                    status_change["NBM"] = NBMlist
                    ADU["PAYLOAD"] = status_change
                    ADU["AUTHORIZATION_CODE"] = settings.GATEWAY_AUTHORIZATION_CODE
                    print("sending to gateway")
                    self.sendMessage(json.dumps(ADU))

                except Exception as e:
                    print("somethin went wrong")

            def gateway_device_control(self, dbcon, sender, topic, message):

                try:

                    PDU = dict()
                    PDU["AGENT_ID"] = message['AGENT_ID']
                    PDU["POSTMSG"]=message['POSTMSG']
                    ADU = dict()
                    ADU["TYPE"] = "CONTROL"
                    ADU["PAYLOAD"] = PDU     #{"AGENT_ID": "Sock_221609K0102348","POSTMSG": {"status":"OFF"}}
                    ADU["AUTHORIZATION_CODE"] = settings.GATEWAY_AUTHORIZATION_CODE
                    print("sending to gateway")
                    self.sendMessage(json.dumps(ADU))

                except Exception as e:
                    print("somethin went wrong")

            def handleClose(self):
                print(self.address, 'closed')

        ips = getIPs()
        print "found local ips- ", ips
        device_address = ips[0]
        self.server = SimpleSSLWebSocketServer(device_address, 8889, handlerClass, certfile=settings.GATEWAY_KEYS_FOLDER+"/server.crt",
                                               keyfile=settings.GATEWAY_KEYS_FOLDER+"/server.key")

        print("server startedd")
        self.server.serveforever(self)



