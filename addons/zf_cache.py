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
## 成功登录的
global login_succeed
login_succeed = {}


# 初始化客户数目
INIT_CLIENT_NUM = 10
# 守护线程数目
DAEMON_THREAD_NUM = 1
# 创建线程数目
CREATE_THREAD_NUM = 2
# 检查线程数目
CHECK_THREAD_NUM = 1
# 过期时间（秒）
EXPIRE_SECOND = 300
# 单次创建线程数目
NEW_CLIENT_NUM = 2
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

def get_client_num(name='all'):
    '''
    返回缓存的对象数目
    all->all_clients
    used->used_clients
    login->login_succeed
    '''
    global all_clients
    global used_clients
    global login_succeed
    if name=='all':
        dic=all_clients
    elif name=='used':
        dic=used_clients
    elif name=='login':
        dic=login_succeed
    else:
        dic=all_clients
    return len((dic.keys()))

def zhengfang():
    """
    正方相关操作,直接调用zf类
    返回（viewstate, timd_md5, zf)
    """
    viewstate=None
    start = time.time()
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
        if time.time() - start > 10:
            break
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
        cr.setDaemon(True)
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
    '''
    线程遍历
    '''
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

def get_enumer_num():
    '''
    返回线程数目
    '''
    n=0
    for i in threading.enumerate():
        n+=1
    return n


def check_clients():
    """
    检查字典中缓存的对象是否过期
    all_clients
    Used_clients
    login_succeed
    """
    global all_clients
    global used_clients
    global login_succeed

    while True:

        time.sleep(30)

        if config.zf_accelerate:
            li=[all_clients, login_succeed, used_clients]
        else:
            li=[login_succeed,]

        for dic in li:
            on_check = dic

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
                    dic.pop(d)
                    delete_verify_img(d)
                except KeyError:
                    pass
            logger.info('REMOVE %s' % len(del_list))
            con.notify()
            con.release()

        logger.info('check over')


def cache_zf_start():
    """
    调用缓存的主方法
    """

    for i in range(DAEMON_THREAD_NUM):
        p = DaemonThread()
        p.setDaemon(True)
        p.start()

    for i in range(CHECK_THREAD_NUM):
        ch = threading.Thread(name='Check_Thread '+str(i), target=check_clients)
        ch.setDaemon(True)
        ch.start()

    t = threading.Thread(name='Enumer_thread',target=enumer)
    t.setDaemon(True)
    t.start()

def just_check():
    """
    在不使用缓存的时候调用该方法
    删除不使用的缓存
    """
    for i in range(CHECK_THREAD_NUM):
        ch = threading.Thread(name='Check_Thread '+str(i), target=check_clients)
        ch.setDaemon(True)
        ch.start()


def get_time_md5():
    """
    处理GET时的操作
    """
    global all_clients
    global Used_Client

    if config.zf_accelerate:
        time_md5 = all_clients.keys()[0]
        try:
            zf, viewstate, time_start = all_clients.pop(time_md5)
        except KeyError:
            viewstate, time_md5, zf = zhengfang()
    else:
        viewstate, time_md5, zf = zhengfang()
        time_start = time.time()

    used_clients[time_md5] = (zf, viewstate, time_start)

    return time_md5


def zf_login(content):
    """
    传入content-表单输入
    返回 zf 对象和登录返回信息
    """
    global used_clients
    global login_succeed

    xh = content['xh']
    pw = content['pw']
    yanzhengma = content['verify']
    time_md5 = content['time_md5']

    zf, viewstate, time_start = used_clients.get(time_md5)

    zf.set_user_info(xh, pw)
    ret = zf.login(yanzhengma, viewstate)

    login_succeed[time_md5]=[zf, xh ,time.time()]

    return zf, ret

def find_login(time_md5):
    """
    二次查询
    返回(zf, xh, time_start)
    """
    global login_succeed
    tup = login_succeed.get(time_md5)
    login_succeed[time_md5][2]=time.time()# 更新最后查询时间
    return tup



# if __name__ == '__main__':
#
#     cache_zf_start()
