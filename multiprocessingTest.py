from multiprocessing import  Process
from threading import Thread
import time

def func1():
    print "Func 1 start"
    for i in range(10000000):
        pass
    print "Func 1 end"
def func2():
    print "Func 2 start"
    for i in range(1000000):
        pass
    print "Func 2 end"


print "Main Start"
p = Thread(target=func1)
p2 = Thread(target=func2)
#func1()
p.start()
p2.start()
print "Main End"



