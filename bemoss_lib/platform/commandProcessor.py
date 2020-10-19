import datetime
from threading import Thread, current_thread
from multiprocessing import Process, Queue, Value
from platformData import *
import importlib
global processes_dict, archived_process_list
import threading
from BEMOSSThread import BThread, BProcess
from multiprocessing.reduction import reduce_connection
import multiprocessing
import os

agentDict = {
"basicagent": "Agents.basicAgent.BasicAgent",
"devicediscoveryagent": "Agents.deviceDiscoveryAgent.DiscoveryAgent",
"multinodeagent": "Agents.multiNodeAgent.MultiNodeAgent",
"networkagent": "Agents.networkAgent.NetworkAgent",
"approvalhelperagent": "Agents.approvalHelperAgent.ApprovalHelperAgent",
"platformmonitoragent": "Agents.platformMonitorAgent.PlatformMonitorAgent",
"thermostatagent": "Agents.thermostatAgent.ThermostatAgent",
"tsdagent": "Agents.tsdAgent.TSDAgent",
"vipagent": "Agents.vipAgent.VIPAgent",
"bacnetagent": "Agents.BACnetAgent.BACnetAgent",
"lightingscheduleragent": "Applications.lightingSchedulerAgent.LightingSchedulerAgent",
"plugloadscheduleragent": "Applications.plugloadSchedulerAgent.PlugloadSchedulerAgent",
"illuminancebasedlightingcontrol":"Applications.illuminanceBasedLightingControl.IlluminanceBasedLightingControl",
"thermostatcontrolagent": "Applications.thermostatControlAgent.ThermostatControlAgent",
"faultdetection": "Applications.faultDetection.FaultDetectionAgent",
"demandresponse": "Applications.demandResponse.DemandResponse",
"gatewayagent":"Agents.GatewayAgent.WebSocketAgent",
"gatewaydeviceagent":"Agents.gatewayDeviceAgent.GatewayDeviceAgent",
"metadataagent":"Agents.metadataAgent.MetadataAgent",
"scheduleragent":"Agents.schedulerAgent.SchedulerAgent"

}

process_count = 1000



#these agents are run as thread, instead of a different process
useThreadsInstead = ['basicagent','thermostatagent']
def getAgent(agent_name):
    agent_full_path = agentDict.get(agent_name.lower(),None)
    if agent_full_path is None:
        #bad agent name
        return None
    agent_module_name = ".".join(agent_full_path.split(".")[:-1])
    agent_name = agent_full_path.split(".")[-1]
    agent_module = importlib.import_module(agent_module_name)
    agent = getattr(agent_module,agent_name)
    return agent


def processCommand(command):
    global process_count
    def find_matches(pid):
        matches = []
        l = len(pid)
        for process_name, process in processes_dict.items():
            if str(process.id)[-l:] == str(pid):
                matches.append(process_name)
        return matches

    commands = command.split(' ')
    reply = ''


    if len(commands) == 2 and commands[0].lower() == "error":
        agent_name = commands[1]  # assume the argument is agent_name
        try:
            process = processes_dict.get(agent_name)
            error =  process.err
        except AttributeError:
            return ""

        return error


    elif commands[0].lower() == 'status':
        running_count = 0
        stopped_count = 0
        stop_requested_count = 0

        for process_name, process in processes_dict.items():
            if process.is_alive():
                if process.config['stopFlag'].value == 0:
                    status, code = "running", ""
                    running_count +=1
                else:
                    status, code = "stop_requested",""
                    stop_requested_count +=1
            else:
                status, code = "stopped",process.exitcode
                stopped_count += 1
            if hasattr(process,'pid'):
                pid = process.pid
            else:
                pid = os.getpid()

            reply += "{:<6} {:<10} {:<30} {:<6} {:<10}\n".format(process.id, pid, process.name, status, code)

        reply += "Total %s Agents. Running: %s. Stoped: %s. Stop_Requested: %s" % (len(processes_dict.keys()),running_count,stopped_count,stop_requested_count)
        return reply
    # elif commands[0].lower() == 'tstatus': #thread_status
    #     threads = threading.enumerate()
    #
    #     replies = []
    #     for thread in threads:
    #         if hasattr(thread, 'id'):
    #             replies.append((thread.id,thread.name))
    #         else:
    #             if hasattr(thread,'parent') and hasattr(thread.parent,'id'):
    #                 replies.append((thread.parent.id,thread.name))
    #             else:
    #                 replies.append((-1,thread.name))
    #
    #     replies = sorted(replies,key=lambda x: x[0])
    #     if len(commands) > 1:
    #         id = commands[1] #filter only this
    #         new_reply = []
    #         for rep in replies:
    #             if str(rep[0]) == str(id):
    #                 new_reply.append(rep)
    #         replies = new_reply
    #     for id, name in replies:
    #         reply +=("{:<6} {:<50}\n".format(id, name))
    #
    #     return reply
    elif len(commands) == 2 and commands[0].lower() == "tstatus":
        target = commands[1]
        leftPipe, rightPipe = multiprocessing.Pipe()
        reduced_Pipe = reduce_connection(rightPipe)
        finalmessage = {"reduced_return_pipe": reduced_Pipe}
        outQueue.put(("commandhandler", [target], 'tstatus', finalmessage))
        if leftPipe.poll(20):
            result = leftPipe.recv()
            reply = ""
            count = 0
            alive_count = 0
            for id, name, status, watchdogtimer, msg in result:

                reply += "{:<6} {:<60} {:<6} {:<5} {:<10}\n".format(id, name, status, watchdogtimer, msg)
                count += 1
                if status:
                    alive_count += 1

            reply += "Total %s threads. Running: %s. Stoped: %s." % (count, alive_count, count-alive_count)
            return reply
        else:
            return "Timed out"

    elif len(commands) == 2 and commands[0].lower() in ["start", "start_agent", "stop", "stop_agent"]:
        agent_name = commands[1] #assume the argument is agent_name
        if not agent_name in processes_dict: #if agent_name is not present
            #assume it to be pid from the end
            matches = find_matches(pid=agent_name)
            if len(matches) == 1:
                agent_name = matches[0]
            if len(matches) == 0:
                return "invalid pid"
            elif len(matches) > 1:
                reply = "\n".join(
                    [str(processes_dict[process_name].id) + " " + process_name for process_name in matches])
                return reply
        process_name = agent_name
        process = processes_dict[process_name]
        if commands[0].lower() in ["start","start_agent"]:
            old_agent = process.agent
            old_config = process.config
            old_config['stopFlag'].value = 0
            old_config['id'] = process_count
            p = BProcess(target=process.agent, name=process.name, kwargs=old_config)
            p.id = process_count
            process_count += 1
            p.agent = old_agent
            p.config = old_config
            p.start()
            processes_dict[process_name] = p
        else:
            process.config['stopFlag'].value = 1
            archived_process_list.append((datetime.datetime.utcnow(), process))
        return reply

    elif len(commands) == 3 and commands[0].lower() in ["launch_agent","start"]:
        agent_type = commands[1]
        agent_name = commands[2]

        agent = getAgent(agent_type)
        if agent:
            print "Launching " + agent.__name__ + " with name: " + agent_name
            inQ = Queue(AGENT_QUEUE_SIZE)
            inQueues_dict[agent_name] = inQ
            stopFlag = Value('i',0)
            config = {'name': agent_name, 'inQ': inQ, 'outQ': outQueue, 'logQ':logQueue, 'stopFlag': stopFlag, 'id':process_count}
            p = BProcess(target=agent, name=agent_name, kwargs=config)
            p.id = process_count
            process_count += 1
            p.agent = agent
            p.config = config
            p.daemon = True
            p.start()
            if agent_name in processes_dict:  # if there is existing process by that name, terminate it
                processes_dict[agent_name].config['stopFlag'].value = 1  # make the old process stop
                archived_process_list.append((datetime.datetime.utcnow(), processes_dict[agent_name])) #TODO kill processes in archived process if still running and clear it periodically
            processes_dict[agent_name] = p
            return ""
        else:
            return agent_type + " Agent not found"

    elif commands[0].lower() in ["remove_agent","remove"]:
        if len(commands) == 2:
            agent_name = commands[1] #assume the argument is agent_name
        else:
            return "Invalid number of arguments"
        if not agent_name in processes_dict: #if agent_name is not present
            #assume it to be pid from the end
            matches = find_matches(pid=agent_name)
            if len(matches) == 1:
                agent_name = matches[0]
            elif len(matches) == 0:
                return "invalid pid"
            else:
                return " ".join([processes_dict[process_name].id for process_name in matches])

        if agent_name in processes_dict or find_matches(pid=agent_name):
            if processes_dict[agent_name].is_alive():
                if processes_dict[agent_name].config['stopFlag'].value == 1:
                    return "Wait for it to stop first"
                else:
                    return "Should stop first"
            processes_dict.pop(agent_name) #remove it from process-dict
            inQueues_dict.pop(agent_name)
            return ""
    else:
        return "Invalid command"