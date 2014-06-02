#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from urlparse import urljoin
import logging
import datetime
import gevent
import gevent.monkey
from gevent.queue import Queue, Empty
gevent.monkey.patch_socket()

import requests
from bson import ObjectId

from addons.mongo2s import mongod
from addons.utils import send_mail

class GotitAPI:

    headers={
            'accesstoken':'203ccbb1c5d05d2a58bf6d81e68fb9b2'
        }

    def get_url(self, url):
        """ Get target url """
        base_url = "http://api.t.gotit.asia/"
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
                mongod.users.update({'_id':ObjectId(_user['_id'])},
                          {'$set':{
                              "score_status": score_message,
                              'last_fetch': datetime.datetime.now(),}
                          },)
                score = score_dict.get('data', None)
                new_hash = get_sha(score)
                if new_hash != _user.get('score_hash', None):
                    mongod.users.update({'_id':ObjectId(_user['_id'])},
                      {'$set':{
                          "score_hash": new_hash,
                          'last_fetch': datetime.datetime.now(),}
                      },)
                    if send_dict_email([_email], score):
                        user_log(_user['_id'], "Score", "OK","Success", thread_name)
                else:
                    user_log(_user['_id'], "Score", "PASS", "Not Change", thread_name)
            else:
                if score_message != _user.get('score_status', None):
                    mongod.users.update({'_id':ObjectId(_user['_id'])},
                          {'$set':{
                              "score_status": score_message,
                              'last_fetch': datetime.datetime.now(),}
                          },)
                    send_dict_email([_email],
                        data={"Error Message":score_message})
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

tasks = Queue(maxsize=10)

def boss():
    """ 从mongo中获取用户创建任务，放入Queue
    Queue最大容量为10, 等于10时阻塞
    """
    for t in mongod.users.find({"active": True}):
        task = {'action':'score', 'user': t}
        tasks.put(task)

def worker(thread_name):
    try:
        while True:
            task = tasks.get(timeout=1)
            if task['action'] == "score":
                gotit = GotitAPI()
                gotit.score_task(task, thread_name)
            elif task['action'] == "lib":
                pass
            else:
                gevent.sleep(0)
    except Empty:
        pass

gevent.spawn(boss).join()
threads = []
for w in ('Tom', 'Jerry', 'Obama'):
    threads.append(gevent.spawn(worker, w))
gevent.joinall(threads)