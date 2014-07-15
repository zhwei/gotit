#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import datetime
import gevent
import gevent.monkey
from gevent.queue import Queue, Empty
gevent.monkey.patch_socket()
from urlparse import urljoin

import requests
from bson import ObjectId

from addons.mongo2s import mongod
from addons.utils import send_mail
from addons.config import CRON_TOKEN

class GotitAPI:

    headers={'accesstoken': CRON_TOKEN,}

    def get_url(self, url):
        """ Get target url """
        base_url = "http://api.gotit.asia/"
        return urljoin(base_url, url)

    def __init__(self):

        pass

    def get(self, url, **kwargs):

        _req = requests.get(url,
                headers=self.headers, **kwargs)

        return json.loads(_req.content)

    def post(self, url, data, **kwargs):

        _req = requests.post(url, data=data,
                headers=self.headers, **kwargs)

        return json.loads(_req.content)

    def get_score(self, xh, pw):
        """ 抓取成绩 """
        url=self.get_url("/score/current_semester.json?nocode=true")
        data = json.dumps({"xh":xh, "pw":pw})
        return self.post(url, data=data)

    def score_task(self, task, thread_name):
        """ 成绩任务 """
        _user = task['user']
        _xh, _pw = _user['xh'], _user['pw']
        _email = _user['email']
        if task.get("action", None):
            score_dict = self.get_score(_xh, _pw)
            score_message = score_dict['status']['message']
            if score_message == "Success":
                score = score_dict.get('data', None)
                if not score:
                    score, _mark = {"STATUS":u"暂无成绩"}, False
                else: _mark = True
                new_hash = get_sha(score)
                if new_hash != _user.get('score_hash', None):
                    if send_dict_email([_email], score):
                        if _mark:
                            mongod.users.update({'_id':ObjectId(_user['_id'])},
                              {'$set':{"score_hash": new_hash,
                                  "score_status": score_message,
                                  'last_fetch': datetime.datetime.now(),}},)
                            user_log(_user['_id'], "Score", "OK","Success", thread_name)
                        else:
                            mongod.users.update({'_id':ObjectId(_user['_id'])},
                              {'$set':{"score_hash": new_hash,
                                  "score_status": "NO SCORE",
                                  'last_fetch': datetime.datetime.now(),}},)
                            user_log(_user['_id'], "Score", "EMPTY", "NO SCORE", thread_name)
                else:
                    mongod.users.update({'_id':ObjectId(_user['_id'])},
                          {'$set':{"score_status": "Not Change",
                              'last_fetch': datetime.datetime.now(),}},)
                    user_log(_user['_id'], "Score", "PASS", "Not Change", thread_name)
            else:
                if score_message != _user.get('score_status', None):
                    mongod.users.update({'_id':ObjectId(_user['_id'])},
                          {'$set':{"score_status": score_message,
                              'last_fetch': datetime.datetime.now(),}},)
                    send_dict_email([_email],
                        data={"Error Message": score_message})
                    user_log(_user['_id'], "Score", "ERROR_SEND", score_message, thread_name)
                else:
                    user_log(_user['_id'], "Score", "ERROR_PASS",score_message, thread_name)

def send_dict_email(to_list, data, title="Gotit邮件通知"):
    """ 发送字典格式的内容 """
    from web.contrib.template import render_jinja
    render = render_jinja('templates/email', encoding='utf-8')
    return send_mail(to_list, title, render.score(object_list=data))

def user_log(user_id, item, status, message, thread_name):
    """ 创建用户日志 """
    mongod.CronLog.insert({
        "user_id": user_id,
        "item": item,
        "status": status,
        "message": message,
        "thread_name": thread_name,
        "created_date": datetime.datetime.now()
    })
    return True

def get_sha(words):
    """获取哈希值"""
    import hashlib
    return hashlib.sha224(str(words).encode('utf-8')).hexdigest()


def boss():
    """ 从mongo中获取用户创建任务，放入Queue
    Queue最大容量为10, 等于10时阻塞
    """
    global tasks
    for t in mongod.users.find({"active": True}):
        task = {'action':'score', 'user': t}
        tasks.put(task)
        logging.error("Create task %s[%s]" % (t['xh'], task['action']))

def worker(thread_name):
    logging.error("I am Worker %s" % thread_name)
    global tasks
    try:
        while True:
            task = tasks.get(timeout=1)
            logging.error("%s Processing %s" % (thread_name, task['user']['xh']))
            if task['action'] == "score":
                gotit = GotitAPI()
                gotit.score_task(task, thread_name)
            elif task['action'] == "lib":
                pass
            else:
                gevent.sleep(0)
    except Empty:
        logging.error("%s QUITING time" % thread_name)
        pass

def control():
    global tasks
    tasks = Queue(maxsize=10)
    #gevent.spawn(boss).join()
    threads = [gevent.spawn(boss),]
    for w in ('Tom', 'Jerry', 'Obama', 'hello'):
        threads.append(gevent.spawn(worker, w))
    gevent.joinall(threads)

if __name__ == '__main__':
    while True:
        logging.error("Cron Work Start")
        logging.error(datetime.datetime.now())
        control()
        logging.error("Sleeping ...")
        gevent.sleep(600)
