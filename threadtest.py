
from bemoss_lib.platform.BEMOSSThread import BThread
import time
import threading

def myth(name, count):
    for i in range(10):
        print name, count
        count += 1
        if count > 5:
            this_thread = threading.currentThread()
            this_thread.name = str(count)
            print "Name updated"
        time.sleep(1)




kk = BThread(target=myth,name="myname",args=('hello',2))
kk.start()

for i in range(15):
    print "kk name is: " + kk.name
    time.sleep(1)
