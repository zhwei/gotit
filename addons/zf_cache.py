#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import threading
from urllib2 import URLError

from zf import ZF
from tools import init_log

import config

# 初始化 Condition
con = threading.Condition()

# GIL
mylock = threading.RLock()

# 初始化全局变量
## 保存缓存的对象
global all_clients
all_clients = {}
## 供交换使用
global temp_clients
temp_clients ={}
## 经过get后的对象
global used_clients
used_clients = {}



# 初始化客户数目
INIT_CLIENT_NUM = 10
# 守护线程数目
DAEMON_THREAD_NUM = 1
# 创建线程数目
CREATE_THREAD_NUM = 2
# 检查线程数目
CHECK_THREAD_NUM = 1
# 过期时间（秒）
EXPIRE_SECOND = 50
# 单次创建线程数目
NEW_CLIENT_NUM = 5
# 缓存的client数目
CACHE_CLIENT_NUM = 60

# 初始化日志模块
logger = init_log(log_name='zf_cache', level_name='info',fi=False)


def get_count():
    """
    获取缓存的数目
    """
    global all_clients
    return len(all_clients.keys())

def zhengfang():
    """
    正方相关操作,调用zf类
    """
    viewstate=None
    while viewstate is None:
        try:
            time.sleep(0.01)
            zf = ZF()
            viewstate, time_md5 = zf.pre_login()
            with mylock:
                temp_clients[time_md5] = (zf, viewstate, time.time())
        except URLError:
            viewstate = None
            logger.error('can not touch zheng fang')
            pass
        except IOError:
            viewstate=None
            logger.error('io error can not write to gif')
            pass
    return (viewstate, time_md5, zf)

def delete_verify_img(time_md5):
    """
    用于删除验证码文件
    """
    import os
    try:
        path = os.path.join(config.pwd,'static/pic/', '%s.gif'%time_md5)
        os.remove(path)
    except:
        logger.error('Delete file %s.gif error'%time_md5)

def create_clients_thread():

    """
    创建缓存的线程，会在其他方法中调用
    """

    global temp_clients
    viewstate = None
    while viewstate is None:
        viewstate, time_md5, zf = zhengfang()
        with mylock:
            temp_clients[time_md5] = (zf, viewstate, time.time())

    time.sleep(0.5)


def create_client(nu=2):
    """
    直接创建缓存的方法，多线程调用create_client_thread()，
    创建两个线程
    """
    # global second
    global temp_clients
    global all_clients

    second = {}
    for i in range(nu):

        cr=threading.Thread(name='Create Client Thread '+str(i),
                            target=create_clients_thread)
        cr.start()
        with mylock:
            second = dict(second, **temp_clients)
            temp_clients = {}

    # print 'second ', len(second.keys())
    con.acquire()
    all_clients = dict(all_clients, **second)
    con.notify()
    con.release()
    # print 'After C  left %s' % len(all_clients.keys())
    logger.info('After C  left %s' % get_count())

def init_client():

    """
    初始化缓存的方法，仅在应用刚刚启动的时候调用
    """

    global temp_clients
    global all_clients
    second = {}
    init_list = []
    for i in range(INIT_CLIENT_NUM):
        time.sleep(0.1)
        cr=threading.Thread(name='Init Client Thread '+str(i),
                            target=create_clients_thread)
        cr.start()
        init_list.append(cr)

        # print 'thread %s init' % i
        logger.info('thread '+ cr.name + ' inited ')

        with mylock:
            second = dict(second, **temp_clients)
            temp_clients = {}
    con.acquire()
    all_clients = dict(all_clients, **second)
    con.notify()
    con.release()

    for i in init_list:
        i.join()
        # print 'init thread %s is over' % i.name
        logger.info('init thread %s is over' % i.name)

    # print "ALL init thread is over, there is %s clients" % len(all_clients.keys())
    logger.warning("ALL init thread is over, there is %s clients" % get_count())
    time.sleep(2)


class DaemonThread(threading.Thread):
    def run(self):
        global count
        global second
        global all_clients

        while True:
            if con.acquire():
                if get_count() >= CACHE_CLIENT_NUM:
                    con.wait()
                    # print 'daemon waiting ...'
                    logger.info('daemon thread is waiting ...')
                    con.notify()
                    con.release()
                else:
                    con.notify()
                    con.release()
                    create_client(NEW_CLIENT_NUM)
                    # all_clients = dict(all_clients, **second)
                    # print  self.name+' CREATE, left' + str(len(all_clients.keys()))

                time.sleep(1)

class Consumer(threading.Thread):
    """
    模拟用户，仅在测试时调用
    """
    def run(self):
        global count
        while True:
            # with mylock:
            #     count = get_count()
            if con.acquire():
                if get_count() < 10:
                    viewstate, time_md5, zf =zhengfang()
                    with mylock:
                        result = (zf, viewstate, time.time())
                    print result
                else:
                    all_clients.pop(all_clients.keys()[0])
                    print 'POP , IS %s ' % get_count()
                    con.notify()
                con.release()
                time.sleep(1)



def enumer():
    while True:
        time.sleep(5)
        logger.info("++++++++++++++++++++++++++++++++++")
        n=1
        for item in threading.enumerate():
            n+=1
            # print n, item.name
            logger.info('%s, %s'%(n, item.name))
        if n>100:
            logger.error('too much threads now is %s'%n)
        logger.info("++++++++++++++++++++++++++++++++++")

def check_clients():
    """
    检查字典中缓存的对象是否过期
    all_clients
    Used_clients
    """
    global all_clients

    while True:
        con.acquire()
        on_check = all_clients
        con.notify()
        con.release()

        time.sleep(3)
        with mylock:
            del_list = []
        for key in on_check.keys():
            if time.time() - on_check[key][2] > EXPIRE_SECOND:
                with mylock:
                    del_list.append(key)
            else:
                pass
        con.acquire()
        for d in del_list:
            try:
                all_clients.pop(d)
                delete_verify_img(d)
            except KeyError:
                pass
        # print 'REMOVE %s' % len(del_list)
        logger.info('REMOVE %s' % len(del_list))
        con.notify()
        con.release()

        # print 'check over'
        logger.info('check over')


def cache_zf_start():
    init_client()

    for i in range(DAEMON_THREAD_NUM):
        p = DaemonThread()
        p.setDaemon(True)
        p.start()

    for i in range(CHECK_THREAD_NUM):
        ch = threading.Thread(name='Check_Thread '+str(i), target=check_clients)
        ch.start()

    t = threading.Thread(target=enumer)
    t.start()



def get_time_md5():
    """
    处理GET时的操作
    """
    global all_clients
    global Used_Client

    key = all_clients.keys()[0]
    current = all_clients.pop(key)
    time_md5 = key
    used_clients[key] = current
    return time_md5

def get_from_used(time_md5):
    """
    用于处理POST
    """
    global used_clients
    tup=used_clients.get(time_md5)
    return tup

if __name__ == '__main__':

    cache_zf_start()