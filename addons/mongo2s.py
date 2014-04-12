#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import datetime

from pymongo import Connection
from pymongo.errors import ConnectionFailure

# MongoDB Tools

def init_mongo():
    """ 初始化MongoDB 
    """
    try:
        db = Connection(host='127.0.0.1',port=27017)['gotit']
    except ConnectionFailure:
        sys.stderr.write('Error: Can not Connect MongoDB')
        sys.exit()

    return db

def get_last_one_by_date(collection):

    mongo = init_mongo()
    li = mongo[collection].find().sort('datetime',-1)
    ret = li[0]
    return ret

def collect_checkcode(code):
    """收集中文验证码字库
    用于以后验证码识别
    写入MongoDB
    """
    db = init_mongo()

    db.checkcodes.insert({
        'code': code,
        })
    return True

def mcount(item):
    """记录某些事件发生的次数，写入mongodb
    Usage: mcount('submit')
    """
    db = init_mongo()
    key = {'item':item}
    data = {
            "$inc":{"times":1},
            "$set":{
                'last':datetime.datetime.now(),
                }
            }
    db.analytics.update(key, data, upsert=True)
    return True

def set_zero(item):
    """ 将某项记录置0
    """
    db = init_mongo()
    key = {'item':item}
    data = {
            "$set":{
                'times':0,
                'last':datetime.datetime.now(),
                }
            }
    db.analytics.update(key, data, upsert=True)
    return True
