import threading
import time
import datetime
import requests
from Queue import Queue

lock = threading.Lock()

tasks = Queue()

N = 5000  # spawn 100 threads
POOL = 200
delay = 10/N  # delay tasks

pending_work = 0
pending_lock = threading.Lock()

url = "https://jsonplaceholder.typicode.com/posts/1"
#url = "https://xnfixa0ri5.execute-api.us-east-1.amazonaws.com/Development/BEMOSSAPIGateWay"
report_count = dict()
report_count_count = dict()
def report(id):  # assemble the report of who have reported in a given minute
    minute = datetime.datetime.now().minute
    hour = datetime.datetime.now().hour

    with lock:
        if minute not in report_count:
            report_count[minute] = [0] * N

        if minute not in report_count_count:
            report_count_count[minute] = 0

        report_count_count[minute] += 1
        report_count[minute][id] = report_count[minute][id] + 1



def periodicFunc(id):
    global pending_work
    while True:
        task_id = tasks.get(block=True)
        resp = requests.get(url)
        if resp.status_code != 200:
            print(resp.status_code)
        #print("Task Done:"+str(task_id))
        x=resp.text
        report(task_id)

        with pending_lock:
            pending_work -= 1



def taskfill():
    global pending_work

    for i in range(100):
        print("Before Pending work: "+str(pending_work))

        print("Before Size:" + str(tasks.qsize()))
        for i in range(N):
            tasks.put(i)
            #time.sleep(delay)
            with pending_lock:
                pending_work += 1

        print("After Size:" + str(tasks.qsize()))
        print("After Pending work: " + str(pending_work))
        time.sleep(60)



def printStats():
    for i in range(100):
        print("Printing report for the minute \n")
        print("Before Report Pending work: " + str(pending_work))
        print(datetime.datetime.now())
        last_minute = datetime.datetime.now().minute - 1
        hour = datetime.datetime.now().hour
        if last_minute in report_count:
            times_per_minute = dict()
            for count in report_count[last_minute]:
                if count not in times_per_minute:
                    times_per_minute[count] = 0
                times_per_minute[count] += 1
            for times_per_minute_lable, times_per_minute_value in times_per_minute.items():
                print("%s threads reported %s times in the last minute \n" % (
                    times_per_minute_value, times_per_minute_lable))
        else:
            print("No data for this minute. Wait. ")
        time.sleep(30)

def pendingReport():
    while True:
        print("Pending work Report: " + str(pending_work) + " at " + str(datetime.datetime.now()))
        time.sleep(10)

threadList = list()
for i in range(POOL):
    x = threading.Thread(target=periodicFunc,args=(i,))
    x.start()


statThread = threading.Thread(target=printStats)
statThread.start()


taskFillThread = threading.Thread(target=taskfill)
taskFillThread.start()

pendingReportTh = threading.Thread(target=pendingReport)
pendingReportTh.start()

statThread.join(timeout=1000)
print("Done creating tasks")
print("Done starting tasks")