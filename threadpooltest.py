import threading
import time
import datetime
import requests
lock = threading.Lock()


N = 2000  # spawn 100 threads

delay = 15/N  # delay between spawning

report_count = dict()

def report(id):  # assemble the report of who have reported in a given minute
    minute = datetime.datetime.now().minute
    hour = datetime.datetime.now().hour
    with lock:
        if minute not in report_count:
            report_count[minute] = [0] * N

    if id % 10000 == 0:
        print("Creating count ID: " + str(id) + " for minute " + str(minute))

    report_count[minute][id] = report_count[minute][id] + 1


def periodicFunc(id):
    for i in range(100):
        #print "Thread:"+str(id)+" doing requests"
        resp = requests.get(
                "https://xnfixa0ri5.execute-api.us-east-1.amazonaws.com/Development/BEMOSSAPIGateWay")
        if resp.status_code != 200:
            print(resp.status_code)
        x=resp.text
        report(id)
        time.sleep(20)



def printStats():
    for i in range(100):
        print("Printing report for the minute \n")
        print(datetime.datetime.now())
        last_minute = datetime.datetime.now().minute - 1
        hour = datetime.datetime.now().hour
        if last_minute in report_count:
            times_per_minute = dict()
            for entry in report_count[last_minute]:
                if entry not in times_per_minute:
                    times_per_minute[entry] = 0
                times_per_minute[entry] += 1
            for times_per_minute_lable, times_per_minute_value in times_per_minute.items():
                print("%s threads reported %s times in the last minute \n" % (
                    times_per_minute_value, times_per_minute_lable))
        else:
            print("No data for this minute. Wait. ")
        time.sleep(30)

threadList = list()
for i in range(N):
    x = threading.Thread(target=periodicFunc,args=(i,))
    x.start()

statThread = threading.Thread(target=printStats)
statThread.start()
statThread.join(timeout=100)
print("Done creating tasks")
print("Done starting tasks")