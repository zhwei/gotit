#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
import sys
import logging
import logging.handlers

import redis
from pymongo import Connection
from pymongo.errors import ConnectionFailure

import config
import errors
from addons.calc_GPA import GPA
from addons.get_all_score import ALL_SCORE


LEVELS = {
    'debug':logging.DEBUG,
    'info':logging.INFO,
    'warning':logging.WARNING,
    'error':logging.ERROR,
    'critical':logging.CRITICAL,
}

def init_log(log_name, level_name="error", fi=True):

    log_file_name = os.path.join(config.pwd, 'log', '%s.log'%log_name)

    # 创建一个logger
    logger=logging.getLogger(log_name)

    # 日志级别， 默认为error, 超过所设级别才会显示
    level = LEVELS.get(level_name, logging.NOTSET)
    logger.setLevel(level)

    if fi:

        # 创建一个handler, 用于写进日志文件
        # maxBytes 单个日志文件大小，超过后会新建文件，备份为 log.n
        # backupCount 超过多少个文件后会自动删除
        handler = logging.handlers.RotatingFileHandler(log_file_name,
                                                  maxBytes=1000000,
                                                  backupCount=50,)
    else:
        # 显示在控制台上
        handler = logging.StreamHandler()

    # 日志格式
    # 2011-08-31 19:18:29,816-log_name-INFO-log_line-message
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-line:%(lineno)d::%(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger



def init_redis():
    redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)
    return redis_server


def not_error_page(page):
    """检查页面
    检查页面是否有弹窗警告
    """
    import re
    res = ">alert\(\'(.+)\'\)\;"
    _m = re.search(res, page)
    if _m:
        raise errors.PageError(_m.group(1))
        #return _m.group(1)
    if page.find('ERROR - 出错啦！') != -1:
        raise errors.ZfError('正方教务系统不可用')
    return True

def get_score_jidi(xh):

    a = ALL_SCORE()
    score = a.get_all_score(xh)
    gpa = GPA(xh)
    gpa.getscore_page()
    jidi = gpa.get_gpa()["ave_score"]
    return score, jidi

def collect_checkcode(code):
    """收集中文验证码字库
    用于以后验证码识别
    写入MongoDB
    """
    try:
        db = Connection(host='127.0.0.1',port=27017)['gotit']
    except ConnectionFailure:
        sys.stderr.write('Error: Can not Connect MongoDB')
        sys.exit()
    db.checkcodes.insert({
        'code': code,
        })
    return True
