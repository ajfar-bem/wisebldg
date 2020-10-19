import zmq
import os
import sys
import subprocess
import os
from bemoss_lib.databases.cassandraAPI import startCassandra
import settings

context = zmq.Context()
address = settings.PLATFORM_SOCKET_ADDRESS

#  Socket to talk to server
intial_message = []
import settings
import time
def send_command(command):
    req_socket = context.socket(zmq.REQ)
    req_socket.connect(address)
    req_socket.RCVTIMEO = 5000

    try:
        req_socket.send(command)
    except zmq.error.ZMQError:
        return "Failed sending"

    try:
        message = req_socket.recv()
    except zmq.error.Again:
        return "Timed Out"
    else:
        return message

def startBEMOSS(skipBEMOSS=False, skipPlatformMonitorAgent=False):
    startCassandra.start()
    os.system(settings.PROJECT_DIR + "/start_webserver.sh " + settings.PROJECT_DIR)
    if not skipBEMOSS:
        os.system("nohup x-terminal-emulator -e %s/env/bin/python %s/bemoss_lib/platform/BEMOSS.py" % (
        settings.PROJECT_DIR, settings.PROJECT_DIR))
        time.sleep(2)

    command_list = ["launch_agent metadataagent metadataagent","launch_agent devicediscoveryagent devicediscoveryagent",
                    "launch_agent approvalhelperagent approvalhelperagent","launch_agent vipagent ui","launch_agent tsdagent tsdagent",
                    "launch_agent scheduleragent scheduleragent","launch_agent bacnetagent bacnetagent","launch_agent basicagent basicagent"]
    for command in command_list:
        print "sending: " + command
        print send_command(command)
        time.sleep(.2)

    #print send_command("launch_agent gatewayagent gatewayagent")

if __name__ == "__main__":
    commands = sys.argv
    if len(commands) >= 1:
        if commands[1] == "forever":
            inp = ''
            while inp != 'exit':
                inp = raw_input(":")
                if inp == "startBEMOSS":
                    startBEMOSS()
                elif inp == "startAgents":
                    startBEMOSS(skipBEMOSS=True)
                elif inp == "startCoreAgents":
                    startBEMOSS(skipBEMOSS=True, skipPlatformMonitorAgent=True)
                else:
                    print send_command(inp)
        if commands[1] == "startBEMOSS":
            startBEMOSS()
        else:
            command = ' '.join(commands[1:])
            print send_command(command)

