#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
from os.path import join
import zipfile
import logging
import logging.handlers
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


import config
import errors
from calc_GPA import GPA
from redis2s import rds

class PageAlert(object):
    """ 处理页面警告
    从redis中获取页面警告
    """

    def __getattr__(self, item):
        """从redis中获取警告内容"""
        alert = rds.get('SINGLE_{}'.format(item))
        return alert

def get_unique_key(prefix=None):

    import uuid
    key = uuid.uuid4().hex
    if prefix: key = "{}_{}".format(prefix, key)
    return key

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
        raise errors.RequestError('正方教务系统不可用')
    return True

def get_score_gpa(xh):
    """返回学分绩点
    """
    gpa = GPA(xh)
    gpa.getscore_page()
    score = gpa.get_all_score()
    jidi = gpa.get_gpa()
    return score, jidi


def zipf2strio(foldername, includeEmptyDIr=True):
    """ 压缩目录, 压缩包写入StringIO 并返回
    """
    empty_dirs = []
    fi = StringIO.StringIO()
    zip = zipfile.ZipFile(fi, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(foldername):
        empty_dirs.extend([dir for dir in dirs if os.listdir(join(root, dir)) == []])
        for name in files:
            zip.write(join(root ,name))
        if includeEmptyDIr:
            for dir in empty_dirs:
                zif = zipfile.ZipInfo(join(root, dir) + "/")
                zip.writestr(zif, "")
        empty_dirs = []
    zip.close()
    return fi


def incr_key(key, expire=False):
    """ 如果存在则++，不存在则设为0 """
    if rds.exists(key): rds.incr(key)
    else:
        rds.set(key, 0)
        if expire: rds.expire(key, expire)
    return int(rds.get(key) or 0)

def send_mail(to_list, subject, content):
    import smtplib
    from email.mime.text import MIMEText
    me="hello"   #这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(content,_subtype='html',_charset='gb2312')    #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = subject    #设置主题
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(config.EMAIL_HOST)  #连接smtp服务器
        s.login(config.EMAIL_HOST_USER,config.EMAIL_HOST_PASSWORD)  #登陆服务器
        s.sendmail(me, to_list, msg.as_string())  #发送邮件
        s.close()
        return True
    except Exception, e:
        logging.error(e)
        return False