#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
import redis
import logging
import logging.handlers


from web.contrib.template import render_jinja
render = render_jinja('templates', encoding='utf-8')

import config
from get_CET import CET
from calc_GPA import GPA
from get_all_score import ALL_SCORE

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

def zf_result(t, zf, time_md5):
    '''
    避免重复判断
    '''
    if t == "1":
        table = zf.get_score()
    elif t == "2":
        table = zf.get_kaoshi()
    elif t == "3":
        table = zf.get_kebiao()
    else:
        return render.input_error()
    if table:
        error = None
        return render.result(table=table, error=error, time_md5=time_md5)
    else:
        table = None
        error = "can not find your index table"
        return render.result(table=table, error=error, time_md5=time_md5)

def score_result(xh):
    '''
    成绩和绩点查询
    '''
    a = ALL_SCORE()
    table = a.get_all_score(xh)
    gpa = GPA(xh)
    gpa.getscore_page()
    jidian = gpa.get_gpa()["ave_score"]

    if table:
        return render.result(score_table=table, jidian=jidian)
    else:
        table = None
        error = "can not get your score"
    return render.result(table=table, error=error)

def init_redis():
    redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)
    return redis_server
