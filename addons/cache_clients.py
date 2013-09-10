#!/usr/bin/env python
# -*- coding: utf-8 -*-


#import os
import time
import threading
from urllib2 import URLError

mylock = threading.RLock()

from zf import ZF


global all_clients
all_clients = {}

global temp_clients

temp_clients = {}


def get_count():
    return len(all_clients.keys())

class CreateClients(threading.Thread):


    def run(self):

        global temp_clients

        try:
            zf = ZF()
            viewstate, time_md5 = zf.pre_login()
            with mylock:
                temp_clients[time_md5] = (zf, viewstate, time.time())
                print self.name + ' create at ' + str(temp_clients[time_md5][2]),', temp ', len(temp_clients.keys())
                temp_clients = {}
        except URLError:
            print "can not touch zhengfang"

        except IOError:
            print "io error"

        time.sleep(0.5)


class DaemonThread(threading.Thread):

    def daemon_thread(self):

        """
        用于监控大字典
        """
        global count
        global second
        global all_clients

        while True:

            if con.acquire():
                count = len(all_clients.keys())
                if count >= 10:
                    con.wait()
                    print "daemon waiting..."
                    time.sleep(0.5)
                    con.notify()
                    con.release()
                else:
                    con.notify()
                    con.release()
                    with mylock:
                        second = {}
                    for i in range(10):
                        cr=CreateClients()
                        cr.start()
                        with mylock:
                            try:
                                second = dict(second, **temp_clients)
                                print 'second have %s keys' % len(second.keys())
                            except TypeError:
                                print 'SECOND type error ---------------'
                        print self.name + " createing at time " + str(i)
                        time.sleep(0.5)
                    con.acquire()
                    try:
                        all_clients = dict(all_clients, **second)
                        print 'merge with second('+str(len(second.keys()))+') all clients left '+str(len(all_clients.keys()))
                        second = {}
                    except TypeError:
                        print 'daemon thread type error'
                    con.notify()
                    con.release()
                time.sleep(1)


    def run(self):

        self.daemon_thread()


class PopClient(threading.Thread):

    def run(self):
        while True:
            if con.acquire():
                if get_count() < 10:
                    print 'all clients less than 10'
                    con.wait()
                else:
                    all_clients.pop(all_clients.keys()[0])
                    msg = self.name + ' pop , all_clients left ' + str(get_count())
                    print msg
                    con.notify()
                con.release()
                time.sleep(0.5)


def start():

    global temp_clients
    global all_clients
    temp_clients = {}

    for i in range(2):
        cr=CreateClients(name='create clients '+str(i))
        cr.start()
    con.acquire()
    all_clients = dict(all_clients, **temp_clients)
    con.notify()
    con.release()


    dae = DaemonThread()
    dae.start()

    for i in range(2):
        t = PopClient(name='pop thread - '+str(i))
        t.start()


if __name__ == '__main__':
    con = threading.Condition()
    start()
