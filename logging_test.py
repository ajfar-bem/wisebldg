import logging
import logging.handlers
import threading
import time

main_logger = logging.getLogger("filelogger1")
main_logger.level = logging.DEBUG

console_logger = logging.getLogger("consolelogger1")
console_logger.level = logging.INFO

fileHandler = logging.handlers.RotatingFileHandler(filename="BEMOSS.log",maxBytes=50000000,backupCount=10) #50 MB limit
consoleHandler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
                              "%Y-%m-%d %H:%M:%S")

fileHandler.setFormatter(formatter)


main_logger.addHandler(fileHandler)
console_logger.addHandler(consoleHandler)

def threadFunc():
    main_logger.log(30,"Hello")

th = threading.Thread(target=threadFunc)
th.start()
time.sleep(1)
print "Done"