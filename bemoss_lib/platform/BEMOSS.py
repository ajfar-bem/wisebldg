import threading
from Queue import Empty, Full
from multiprocessing import Process, Queue, Value
import datetime
import os
import zmq
import logging
from logging import handlers

from platformData import *

from BEMOSSThread import BThread, BProcess
from commandProcessor import processCommand

import cgitb
cgitb.enable() #gives more detailed traceback

main_logger = logging.getLogger("filelogger")
main_logger.level = logging.DEBUG

console_logger = logging.getLogger("consolelogger")
console_logger.level = logging.INFO

fileHandler = handlers.RotatingFileHandler(filename="BEMOSS.log",maxBytes=50000000,backupCount=10) #50 MB limit
consoleHandler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")

fileHandler.setFormatter(formatter)


main_logger.handlers = [fileHandler]
console_logger.handlers = [consoleHandler]
main_logger.propagate = False
console_logger.propagate = False



changeLogFilterQ = Queue(10)

def handelLogging():
    filterheader = ""
    while True:
        source, header, level, message = logQueue.get()
        message = header +" :" + message
        try:
            newfilter = changeLogFilterQ.get(False)
        except Empty:
            pass
        else:
            filterheader = newfilter

        main_logger.log(level,message)
        if filterheader:
            if header.startswith(filterheader):
                console_logger.log(level,"filtering:" + filterheader + ": " + message)
        else:
            console_logger.log(level, message)


def handleCommands(threadLock,stopFlag):
    while True:
        #  Wait for next request from client
        print "Creating Socket"
        context = zmq.Context()
        rep_socket = context.socket(zmq.REP)
        rep_socket.bind(address)
        message = rep_socket.recv()

        print message
        if message == "Exit":
            stopFlag.Value = 1
            break

        splitmessage = message.split(" ")
        if len(splitmessage) == 2 and splitmessage[0] == "filterlog": #update the console log filtering
            changeLogFilterQ.put(splitmessage[1])
            print("Filter requested:" + splitmessage[1])
            rep_socket.send(str("Filter Requested"))
            continue


        with threadLock:
            try:
                reply = processCommand(message)
            except Exception as ex:
                reply = "Problem executing command: " + str(type(ex)) + " " + str(ex)
            else:
                print "Command Processed: " + message
        if not reply:
            reply = ""
        rep_socket.send(str(reply))

    print "Exiting handle commands Thread"





stopFlag = Value('i',0)

threadLock = threading.Lock()
command_line_thread = BThread(target=handleCommands,args=(threadLock,stopFlag))
command_line_thread.id = -1
command_line_thread.name = "commandHandler"
command_line_thread.daemon = True
command_line_thread.start()


logging_thread = BThread(target=handelLogging)
logging_thread.id = -1
logging_thread.name = "loggingHandler"
logging_thread.daemon = True
logging_thread.start()



start_time = datetime.datetime.now()

print "****BEMOSS started****"
print os.getpid()
mainThread = threading.current_thread()
mainThread.name = "MainBEMOSSThread"
mainThread.id = 0
counter = 0
while not stopFlag.value:
    #check if there is any new messages in the outQueue of the agents
    try:
        source,destinations,topic,message = outQueue.get(True,1)
        for destination in destinations:
            if destination in inQueues_dict:
                try: #for each destination, put the message in the destination's inQueue
                    inQueues_dict[destination].put((source, topic,message), False)
                except Full:
                    _ = inQueues_dict[destination].get() #if destination inQueue is full, remove old, and put
                    inQueues_dict[destination].put((source, topic, message), False)
                    print(destination + " QueueFull")
                    raise
            elif destination == "platformmanager":
                with threadLock:
                    processCommand(topic + ' ' + message)

    except Empty:
        #continue
        # counter +=1
        # if counter == 10:
        #     counter = 0
        #     h = hpy()
        #     print "\nPrinting Memory Usage"
        #     info= h.heap()
        #     print info.byvia
        pass
    time_diff = datetime.datetime.now() - start_time
    # if time_diff > datetime.timedelta(minutes=20):
    #     break
    # time.sleep(0.1)

print "BEMOSS exited"
