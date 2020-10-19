from threading import Thread, current_thread
import multiprocessing
from multiprocessing import Process
import logging
import traceback
from bemoss_lib.utils.catcherror import getErrorInfo

class BThread(Thread):
    def __init__(self, *args, **kwargs):
        self.parent = current_thread()
        Thread.__init__(self, *args, **kwargs)

    def run(self):
        try:
            Thread.run(self)
        except Exception as self.err:
            current_process = multiprocessing.current_process()
            if hasattr(current_process,'config'):
                logQ = current_process.config['logQ']
                #self.logQ.put((source, header, level, comments + " " + payload))
                logQ.put((__name__, self.name, logging.WARNING, "%s agent crashed. Id: %s. Reason: %s " % (
                self.name, self.id, self.err) + getErrorInfo()))
            self.exitcode = -1
            self.exitmessage = str(self.err)
            raise
        else:
            self.exitcode = 0

class BProcess(Process):
    def __init__(self, *args, **kwargs):
        self.parent = None
        Process.__init__(self, *args, **kwargs)

    def run(self):
        try:
            Process.run(self)
        except Exception as self.err:
            if hasattr(self,'config'):
                logQ = self.config['logQ']
                #self.logQ.put((source, header, level, comments + " " + payload))
                logQ.put((__name__, self.name, logging.WARNING, "%s agent crashed. Id: %s. Reason: %s " % (
                self.name, self.id, self.err) + getErrorInfo()))

            self.exitmessage = str(self.err)
            raise
        else:
            pass