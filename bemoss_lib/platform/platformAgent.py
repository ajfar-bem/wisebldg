import time, threading
from Queue import Empty, Full
from multiprocessing import Value
from bemoss_lib.utils import db_helper
import multiprocessing
from multiprocessing.reduction import reduce_connection
from guppy import hpy
import traceback
import sys
import linecache

from bemoss_lib.platform.BEMOSSThread import BThread
import logging

def singleFrame2string(frame):
    # from module traceback
    lineno = frame.f_lineno # or f_lasti
    co = frame.f_code
    filename = co.co_filename
    name = co.co_name
    s = '  File "{}", line {}, in {}'.format(filename, lineno, name)
    line = linecache.getline(filename, lineno, frame.f_globals).lstrip()
    return s + '\n\t' + line

def frameToStr(frame):
    l = []
    while frame:
        l.insert(0, singleFrame2string(frame))
        frame = frame.f_back
    return '\n'.join(l)



class PlatformAgent(object):
    class RPCTimeout(BaseException):
        pass

    def __init__(self,name,inQ,outQ,logQ,stopFlag,id,*args,**kwargs):
        self.outQ = outQ #Outgoing message queue
        self.inQ = inQ #Incoming message queue
        self.logQ = logQ
        self.name = name
        self.id = id
        self.threads_list = list() #List of threads under this agent. runPeriodically, and listenMessages creates threads
        self.stopFlag = stopFlag #when it is made false, the process ends

        self.contcount = 0
        self.dbcon = db_helper.actual_db_connection()

    def dbrpc(self, command, args, kwargs, timeout=30):

        leftPipe, rightPipe = multiprocessing.Pipe()
        reduced_Pipe = reduce_connection(rightPipe)
        message = dict()
        message['command'] = command
        message['args'] = args
        message['kwargs'] = kwargs
        finalmessage = {"reduced_return_pipe": reduced_Pipe, "actual_message": message}
        self.publish(source=self.name,destinations=['metadataagent'],topic='dbrpc',message=finalmessage)
        if leftPipe.poll(timeout):
            result = leftPipe.recv()
            return result
        else:
            raise self.RPCTimeout("Time Out")

    def mylog(self, source, payload="", header="", comments="",level=logging.DEBUG):

        if not header:
            header=str(self.name)
        else:
            header = str(self.name) + "/" + str(header)

        payload = str(payload)

        comments = str(comments)

        self.logQ.put((source, header, level, comments + " " + payload))

    def debugLog(self, source, payload="", header="", comments=""):
        self.mylog(source,payload=payload,header=header,comments=comments,level=logging.DEBUG)

    def warningLog(self, source, payload="", header="", comments=""):
        self.mylog(source, payload=payload, header=header, comments=comments, level=logging.WARNING)

    def infoLog(self, source, payload="", header="", comments=""):
        self.mylog(source, payload=payload, header=header, comments=comments, level=logging.INFO)


    def runContinuously(self, func, *args, **kwargs):
        stopFlag = Value('i', 0)
        watchDogTimer = Value('i', 0)
        def parallelFunc():
            #dbcon = db_helper.db_connection(parent=self)
            dbcon = self.dbcon
            while not stopFlag.value:
                func(dbcon, *args,**kwargs)
                watchDogTimer.value = 0  # reset it to zero every loop.

        self.contcount += 1
        parallelThread = BThread(target=parallelFunc,name="%s:%s/%s/%s%s"%(self.name,self.id,'runContinuously',func.__name__,str(self.contcount)))
        parallelThread.id = self.id
        parallelThread.watchDogTimer = watchDogTimer
        parallelThread.daemon = True
        parallelThread.func = parallelFunc
        parallelThread.callback = func
        parallelThread.start()
        parallelThread.id = self.id

        self.threads_list.append((parallelThread, stopFlag,watchDogTimer))

    def runPeriodically(self, func, period, start_immediately = True, *args, **kwargs):
        """
        :param func: the function to run periodically
        :param period: the period in seconds
        :param args: optional positional arguments to pass to the periodic function
        :param kwargs: optional keyword argument to pass to function
        :param start_immediately: if true, the first run is done immediately
        :return: None. The periodic function thread will be added to self.threads_list
        """
        stopFlag = Value('i',0) #this flag will be set to 1 by the main thread to kill this thread. 'i' for int
        watchDogTimer = Value('i',0) #This integer will be reset to zero every min(period,20sec). The main thread will
                                    #will increment it every 10sec, and if it becomes too large (>60), then it means
                                    #this thread is hung up. The main thread then let the whole process end with an exception.
                                    #External agency such as a platformmonitor agent will need to restart the agent process again
        def periodic_func():
            #dbcon = db_helper.db_connection(parent=self)
            #the database connection object is created once for the periodic function thread, and passed to the function
            #evertime it is called. postgresql has threadsafety level 2, which means connection objects can be shared
            #between threads but not cursor object. We are creating a new connection and cursor for each thread; if
            #resource consumption becomes an issue, the db_connection can be modified to only return a new cursor using
            #the same connection.
            dbcon = self.dbcon #Sharing the same connection between threads using lock

            if start_immediately:
                run_time = True #if the function should run
            else:
                run_time = False

            if period > 20:
                next_call = time.time() + 20
            else:
                next_call = time.time() + period

            last_run_time = time.time()

            while not stopFlag.value:

                watchDogTimer.value = 0 #reset it to zero every loop.
                this_thread = threading.currentThread()
                #print "WDTVAL " + this_thread.name + ":" + str(watchDogTimer.value)
                if not start_immediately:
                    time.sleep(max(0, next_call - time.time()))

                if time.time() - last_run_time > period:
                    run_time = True

                if run_time:
                    func(dbcon,*args, **kwargs)
                    run_time = False
                    last_run_time += period

                if start_immediately:
                    time.sleep(max(0, next_call - time.time()))


                if last_run_time + period - time.time() > 20:
                    next_call += 20
                else:
                    next_call = last_run_time + period

            print "Exiting periodic from " + self.name

        periodicThread = BThread(target=periodic_func,name="%s:%s/%s/%s"%(self.name,self.id,'periodic_func',func.__name__),
                                 )
        periodicThread.id = self.id
        periodicThread.watchDogTimer = watchDogTimer
        periodicThread.daemon = True
        periodicThread.func = periodic_func
        periodicThread.callback = func
        periodicThread.start()
        periodicThread.id = self.id
        self.threads_list.append((periodicThread,stopFlag,watchDogTimer))

    def publish(self,source, destinations,topic,message):
        try:
            #source = self.name
            self.outQ.put((source,destinations,topic,message),True,10)
        except Full:
            print "OutQueue is full"
            return False

    def listenMessages(self, callback, *args, **kwargs):
        """
        :param callback: The function to call when new message arrives. The function must accept atleast one argument
         for the incoming message
        :param args: the optional positional argument for the callback function
        :param kwargs: optional keyword argument of the the callback function
        :return: None. The listening callback thread will be added to self.thread_list
        """
        stopFlag = Value('i',0)
        watchDogTimer = Value('i', 0)
        def poll_messages():
            #dbcon = db_helper.db_connection(parent=self)
            dbcon = self.dbcon

            while not stopFlag.value:
                try:
                    sender, topic, message = self.inQ.get(True,1) #block for 1 second to wait for message
                    #print("Got message at: %s. Sender: %s. Topic: %s .Message: %s " % (self.name, sender,topic,message))
                    if topic == "tstatus":
                        threads = threading.enumerate()
                        replies = []
                        for thread in threads:
                            if hasattr(thread, 'id'):
                                id = thread.id
                            else:
                                if hasattr(thread, 'parent') and hasattr(thread.parent, 'id'):
                                    id = thread.parent.id
                                else:
                                    id = -1
                            if hasattr(thread,'exitmessage'):
                                thmessage = "Crashed: "+ thread.exitmessage
                            else:
                                thmessage = ""

                            if hasattr(thread,'watchDogTimer'):
                                wdt = str(thread.watchDogTimer.value)
                            else:
                                wdt = ""
                            name = thread.name
                            if thread.isAlive():
                                status = "running"
                            else:
                                status = "crashed"

                            replies.append((id,name,status,wdt,thmessage))

                        replies = sorted(replies, key=lambda x: x[0])

                        def extract_pipe(reduced_pipe):
                            rebuild_func = reduced_pipe[0]
                            return rebuild_func(*reduced_pipe[1])

                        return_pipe = extract_pipe(message["reduced_return_pipe"])
                        print replies
                        return_pipe.send(replies)
                    else:
                        callback(dbcon, sender, topic, message,*args,**kwargs)
                except Empty:
                    pass
                watchDogTimer.value = 0  # reset it to zero every loop.
            print "Exiting message poll from " + self.name

        listenThread = BThread(target=poll_messages,name="%s:%s/%s/%s"%(self.name,self.id,'listenMessage',callback.__name__))
        listenThread.id = self.id
        listenThread.daemon = True
        listenThread.func = poll_messages
        listenThread.watchDogTimer = watchDogTimer
        listenThread.callback = callback
        listenThread.start()
        listenThread.id = self.id

        self.threads_list.append((listenThread,stopFlag,watchDogTimer))

    def exit_function(self):
        print "Good Bye from: " + self.name

    def run(self):
        counter = 0
        heap_count = 0
        while True:

            #if heap_count %10 == 0:
            #    heap_count = 0
            #    h = hpy()
            #    print "\nPrinting Memory Usage inside " + self.name
            #    info = h.heap()
            #    print info.byrcs
            #heap_count += 1
            counter = counter+1
            if not self.stopFlag.value: #if process is not stopped, restart crashed thread every 10 seconds
                if counter == 10:
                    counter = 0
                    for i in range(len(self.threads_list)):
                        thread, thread_stopFlag, thread_watchDogTimer = self.threads_list[i]
                        if not thread.isAlive():
                            old_name = thread.name
                            old_func = thread.func
                            callback = thread.callback
                            old_id = thread.id
                            callback_name = callback.__name__
                            thread = BThread(target=old_func,name=old_name)
                            thread.id = old_id
                            thread.func = old_func
                            thread.callback = callback
                            thread.daemon = True
                            thread.start()
                            thread_stopFlag.value = 0
                            print "Restarting dead thread " + str(callback_name) + " at: " + self.name
                            self.threads_list[i] = thread, thread_stopFlag, thread_watchDogTimer
                        else:
                            thread_watchDogTimer.value += 1
                            #print "The name is:|" + thread.name + "| and WDT is:" + str(thread_watchDogTimer.value)
                            if thread_watchDogTimer.value >= 60: #stuck for over 600 seconds
                                for _, stuckthread_stopFlag, _ in self.threads_list:
                                    stuckthread_stopFlag.value = 1 #ask the thread to stop
                                #print "The name was:|" + thread.name + "| and WDT was:" + str(thread_watchDogTimer.value)
                                sysframes = sys._current_frames()
                                stuckframe = sysframes.get(thread.ident,None)
                                stuckAt = frameToStr(stuckframe)
                                self.warningLog(__name__,payload=stuckAt,comments="A thread {} is stuck. Since, there is no mechanism of killing a thread in python, " \
                                      "I, the main thread, is killing myself (basically a suicide). The BEMOSS process will" \
                                      " probably spawn a new version of me. The stuck thread and all other threads have been directed to stop" \
                                      " when it gets unstuck, so hopefully it will suicide too".format(thread.name))
                                #TODO WARNING: Each time a child thread is stuck, we kill the main thread, and to BEMOSS it will
                                #TODO look like the agent is dead, so, the platformmonitor agent, will spawn a new agent (main thread),
                                #TODO which will inturn create new child thread. You now have two copy of a child-thread: one is the new one,
                                #TODO the other is the stuck child thread from previous agent. If that stuck thread becomes unstuck, it will
                                #TODO kill itself (since it's stop flag has been set), and we will be all right. If however, it remains stuck,
                                #TODO and this new child thread also becomes stuck, then we will be in a vicious cycle of creating more and more
                                #TODO stuck child threads. YOU HAVE BEEN WARNED

                                raise Exception("Stuck Thread: %s"%thread.func.func_code)

            else:
                for i in range(len(self.threads_list)):
                    thread, thread_stopFlag,thread_watchDogTimer  = self.threads_list[i]
                    if not thread_stopFlag.value:
                        thread_stopFlag.value = 1 #make the thread stop
                alive_thread_list =[]
                for i in range(len(self.threads_list)):
                    thread, thread_stopFlag, thread_watchDogTimer = self.threads_list[i]
                    if thread.isAlive():
                        alive_thread_list.append(thread) #if some thread still alive, break the for loop and continue with while loop

                if not alive_thread_list:
                    self.cleanup() #all threads are dead
                    break #break the outer while loop and exit process
                else:
                    print self.name + ": Waiting for these threads to die: " + " ".join([alive_thread.func.__name__ for alive_thread in alive_thread_list])

            time.sleep(1)

    def cleanup(self):
        """
        Implement cleanup activity
        :return:
        """
        print "Cleaned Up"
