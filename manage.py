#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import web
from web import ctx
from web.contrib.template import render_jinja

#import redis
from bson import ObjectId
from weibo import APIClient, APIError

from addons import mongo2s
from addons import redis2s
from addons.redis2s import rds
from addons.utils import zipf2strio, get_unique_key
from addons.autocache import expire_redis_cache
from addons.RedisStore import RedisStore
# from addons.config import SINGLE_HEAD

render = render_jinja('templates', encoding='utf-8')


# APP_KEY = rds.get('weibo_app_key') # app key
APP_KEY = '4001516920' # app key
APP_SECRET = rds.get('weibo_app_secret') # app secret
CALLBACK_URL = 'http://manage.gotit.asia/callback' # callback url
CLIENT = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
AUTH_URL=CLIENT.get_authorize_url()

# 公告前缀(redis中的键前缀)
SINGLE_HEAD = "SINGLE_"

ADMIN_WEIBO_ID = int(rds.get('admin_weibo_id'))



# init mongoDB
db = mongo2s.init_mongo()
rds = redis2s.init_redis()

urls = (
    '/', 'ologin',
    '/callback', 'callback',
    '/panel', 'panel',
    # '/now', 'now',
    '/analytics', 'analytics',

    '/backup/(.+)', 'backup',
    '/backup', 'backup',

    '/readlog/(.+)', 'readlog',

    '/o/(.+)/(.+)/(.+)', 'update',
    '/o/(.+)/(.+)', 'update',

    '/single/(.+)/(.+)', 'single',
    '/single/(.+)', 'single',

    '/de/(.+)/(.+)/(.+)', 'DetailError',
    '/de/(.+)/(.+)', 'DetailError',
    '/de/(.+)', 'DetailError',
    '/de', 'DetailError',

    'developer/(\w+)', 'Developer',
)

app = web.application(urls, locals())

# session
session = web.session.Session(app, RedisStore(), {'count': 0,})

class ologin:

    def GET(self):
        try:
            if session.uid == ADMIN_WEIBO_ID:
                raise web.seeother('/panel')
        except AttributeError:
            pass
        return render.ologin(auth_url=AUTH_URL)


class callback:

    def GET(self):

        try:
            code = web.ctx.query.split('=')[1]
        except IndexError:
            raise web.seeother(AUTH_URL)
        if len(code)!=32:
            raise web.seeother(AUTH_URL)

        _r = CLIENT.request_access_token(code)
        access_token = _r.access_token
        expires_in = _r.expires_in

        CLIENT.set_access_token(access_token, expires_in)

        try:
            uid = CLIENT.account.get_uid.get()['uid']
            if uid != ADMIN_WEIBO_ID:
                return render.ologin(auth_url=AUTH_URL, error='欢迎尝试')
            session['uid'] = uid
        except APIError:
            raise web.seeother('/')

        raise web.seeother('/panel')


def pre_request():
    ''' 访问限制
    '''

    if web.ctx.path not in ['/', '/callback']:
        try:
            if session.uid != ADMIN_WEIBO_ID:
                raise web.seeother('/')
        except AttributeError:
            raise web.seeother('/')


class panel:
    """ 后台面板首页
    """

    def GET(self):

        return render.panel(item=False)

class analytics:
    """ 数据统计
    """

    def GET(self):
        try:
            data = web.input(_method='GET')
            li = ('internalerror', 'checkcode')
            if data.zero in li: mongo2s.set_zero(data.zero)
            raise web.seeother('analytics')
        except AttributeError:
            pass
        coll = db.analytics
        data = {
                'internalerror': coll.find_one({'item':'internalerror'})['times'],
                'CheckCodes': db.checkcodes.count(),
                'session': redis2s.get_count('SESSION*'),
                '用户': redis2s.get_count('user*'),
            }
        return render.panel(item=None, opera='analytics',
                            data=data)

class readlog:
    """ 查看网站日志
    """

    def readfile(self, line):
        log_pwd = rds.get('log_file_path')
        with open(log_pwd) as fi:
            all_lines = fi.readlines()
            counts = len(all_lines)
            for lno, li in enumerate(all_lines):
                if lno >= counts-int(line)*50:
                    yield li

    def GET(self, line):
        try:
            lines = self.readfile(line)
            return render.panel(item=None, opera='readlog', lines=lines)
        except IOError:
            return render.panel(alert="没有找到日志文件, pwd=[{}]".format(rds.get('log_file_path')))


class backup:
    """ mongodb数据库的备份与恢复
    """

    def GET(self, label=None):

        if label=='download':

            mongoexport_path = rds.get('mongoexport_path')
            # 备份mongodb数据库，打包成zip文件并返回下载
            dt=datetime.datetime.now()
            filename = '/tmp/gotit-backup-{}'.format(dt.strftime('%Y%m%d%H%M%S'))
            os.system('{} -d gotit -o {}'.format(mongoexport_path, filename))
            ret = zipf2strio(filename) # 打包写入StringIO对象
            try:
                import shutil
                shutil.rmtree(filename) # 删除备份文件夹
            except OSError:
                pass
            web.header('Content-Type','application/octet-stream')
            web.header('Content-disposition', 'attachment; filename=%s.zip' % filename[5:])
            return ret.getvalue()

        return render.panel(item=None, opera='backup')

    #def POST(self, label=None):

    #    x = web.input(myfile={})
    #    ret=web.debug(x['myfile'])
    #    return ret


class update:
    """ 内容管理 """
    item_list = ['donate', 'notice', 'wxcomment', 'developer']
    opera_list = ['cr', 'del', 'ls']

    def GET(self, opera, item, oid=None):

        if item in self.item_list and opera in self.opera_list:

            if opera == 'ls':
                ls = db[item].find().sort("datetime",-1)
                return render.panel(item=item, opera=opera, ls=ls)

        return render.panel(item=item, opera=opera, oid=oid)

    def POST(self, opera, item, oid=None):

        data = web.input()

        if item in self.item_list and opera in self.opera_list:

            if opera == 'cr' :
                if item == 'donate':
                    db.donate.insert({
                        'name':data['name'],
                        'much':float(data['much']),
                        'datetime': datetime.datetime.now(),
                        })
                    expire_redis_cache('donate')
                elif item == 'developer':
                    _token = get_unique_key()
                    db[item].insert({
                        'token' : _token,
                        'description':data['content'],
                        'datetime': datetime.datetime.now(),
                        })
                    expire_redis_cache('developer')
                else:
                    db[item].insert({
                        'content':data['content'],
                        'datetime': datetime.datetime.now(),
                        })
                    expire_redis_cache('notice')
            elif opera == 'del':
                db[item].remove({'_id':ObjectId(data['oid'])})

        raise web.seeother('/o/ls/'+item)


class single:
    """ 用于处理网站首页等位置的警告或提示信息
    存储在redis中, 简单键值对
    """

    opera_list = ['cr', 'del', 'info']

    def GET(self, opera, item=None):
        if opera in self.opera_list:
            if opera == 'info':

                def get_kv():
                    for key in rds.keys(SINGLE_HEAD+"*"):
                        yield (key[7:], rds.get(key))

                return render.panel2(single_list=get_kv(), opera=opera)

        return render.panel2(item=item, opera=opera)

    def POST(self, opera, item=None, key=None):

        data = web.input()

        if opera in self.opera_list:

            if opera == 'cr' :

                key = SINGLE_HEAD + data['key']
                rds.set(key, data['content'])

                expire_redis_cache(data['key'])

            elif opera == 'del':
                rds.delete(SINGLE_HEAD + item)

        raise web.seeother('/single/info')

class DetailError:
    """查看redis中保存的hash错误
    """

    def GET(self, key=None, hkey=None, do=None):

        content = None
        key_list = None

        if do == "del":
            rds.hdel(key, hkey)
            raise web.seeother("/de/{}".format(key))

        if hkey:
            content = rds.hget(key, hkey)
        elif key:
            key_list = rds.hkeys(key)
        else:
            key_list = rds.keys("error_*")

        return render.panel(item=False, opera='detail_error',
            key=key, hkey=hkey, key_list=key_list, content=content)


# app.add_processor(web.loadhook(pre_request))
