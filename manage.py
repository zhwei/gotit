#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging

import web
from web import ctx
from web.contrib.template import render_jinja

#import redis
from bson import ObjectId
from weibo import APIClient, APIError

from addons.RedisStore import RedisStore
from addons.autocache import expire_redis_cache
from addons.utils import zipf2strio, get_unique_key
from addons.config import (domains, ADMIN_WEIBO_ID,
                           WEIBO_APP_SECRET, WEIBO_APP_KEY,
                            LOG_FILE_PATH, MONGO_DUMP_PATH)
from addons.redis2s import (rds,
                            get_count as rds_get_count)
from addons.mongo2s import (mongod as db,
                            set_zero as mongo_set_zero)

render = render_jinja('templates', encoding='utf-8',
                      globals={"domains": domains})


CALLBACK_URL = 'http://{}/callback'.format(domains['manage'])
CLIENT = APIClient(app_key=WEIBO_APP_KEY,
                   app_secret=WEIBO_APP_SECRET,
                   redirect_uri=CALLBACK_URL)
AUTH_URL = CLIENT.get_authorize_url()


urls = (
    '/', 'OLogin',
    '/callback', 'CallBack',
    '/panel', 'Panel',

    '/analytics', 'Analytics',

    '/backup/(.+)', 'Backup',
    '/backup', 'Backup',

    '/readlog/(\w+)/(.+)', 'ReadLog',

    '/o/(.+)/(.+)/(.+)', 'Update',
    '/o/(.+)/(.+)', 'Update',

    '/single/(.+)/(.+)', 'Single',
    '/single/(.+)', 'Single',

    '/de/(.+)/(.+)/(.+)', 'DetailError',
    '/de/(.+)/(.+)', 'DetailError',
    '/de/(.+)', 'DetailError',
    '/de', 'DetailError',

    '/developer/(\w+)', 'Developer',

    '/users', 'UserManage',
    '/users/(\w+)', 'UserManage',
    '/users/(\w+)/(\w+)', 'UserManage',
)

app = web.application(urls, locals())
session = web.session.Session(app, RedisStore(markup='Session:Manage:'),
                              {'count': 0,})

class OLogin:

    def GET(self):
        try:
            if session.uid == ADMIN_WEIBO_ID:
                raise web.seeother('/panel')
        except AttributeError:
            pass
        return render.ologin(auth_url=AUTH_URL)


class CallBack:

    def GET(self):

        try:
            code = web.ctx.query.split('=')[1]
        except IndexError:
            raise web.seeother(AUTH_URL)
        if len(code)!=32:
            raise web.seeother(AUTH_URL)
        try:
            _r = CLIENT.request_access_token(code)
            access_token = _r.access_token
            expires_in = _r.expires_in

            CLIENT.set_access_token(access_token, expires_in)

            uid = CLIENT.account.get_uid.get()['uid']
            if uid != ADMIN_WEIBO_ID:
                return render.ologin(auth_url=AUTH_URL, error='欢迎尝试')
            session['uid'] = uid
        except APIError:
            raise web.seeother('/')

        raise web.seeother('/panel')

class Panel:
    """ 后台面板首页
    """

    def GET(self):

        return render.panel(item=False)

class Analytics:
    """ 数据统计
    """

    def GET(self):
        try:
            data = web.input(_method='GET')
            if data.zero == "InternalError":
                rds.delete('Error:InternalError')
            elif data.zero == "Cache":
                expire_redis_cache(True)
            raise web.seeother('analytics')
        except AttributeError:
            pass
        data = {
                'Session': rds_get_count('Session:*'),
                "Cache": rds_get_count("Cache:*"),
                '用户': rds_get_count('User:*'),
                "zhe800": rds.get('AD:Count:zhe800'),
                'InternalError': rds.get('Error:InternalError'),
            }
        return render.panel(item=None, opera='analytics',
                            data=data)

class ReadLog:
    """ 查看网站日志
    """

    def readfile(self, fi, line):
        log_pwd = LOG_FILE_PATH.get(fi, "stderr")
        with open(log_pwd) as fi:
            all_lines = fi.readlines()
            counts = len(all_lines)
            for lno, li in enumerate(all_lines):
                if lno >= counts-int(line)*50:
                    yield li

    def GET(self, fi, line=1):
        try:
            lines = self.readfile(fi, line)
            return render.panel(item=None, opera='readlog', lines=lines)
        except IOError:
            return render.panel(alert="没有找到日志文件, pwd=[{}]".format(rds.get('log_file_path')))


class Backup:
    """ mongodb数据库的备份与恢复
    """

    def GET(self, label=None):

        if label=='download':
            # 备份mongodb数据库，打包成zip文件并返回下载
            dt=datetime.datetime.now()
            filename = '/tmp/gotit-backup-{}'.format(dt.strftime('%Y%m%d%H%M%S'))
            os.system('{} -d gotit -o {}'.format(MONGO_DUMP_PATH, filename))
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


class Update:
    """ 内容管理 """
    item_list = ['donate', 'notice', 'wxcomment', 'developer']
    opera_list = ['cr', 'del', 'ls']

    def add_counts(self, ls):
        for _i in ls:
            _token = _i['token']
            _day_key = "Token:Day:{}".format(_token)
            _total_key = "Token:Total:{}".format(_token)
            _i['day'] = rds.get(_day_key)
            _i['total'] = rds.get(_total_key)
            yield _i

    def GET(self, opera, item, oid=None):

        if item in self.item_list and opera in self.opera_list:
            if opera == 'ls':
                ls = db[item].find().sort("datetime",-1)
                if item == "developer":
                    ls = self.add_counts(ls)
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
                elif item == 'developer':
                    _token = get_unique_key()
                    db[item].insert({
                        'token' : _token,
                        'description':data['content'],
                        'datetime': datetime.datetime.now(),
                        })
                else:
                    db[item].insert({
                        'content':data['content'],
                        'datetime': datetime.datetime.now(),
                        })
            elif opera == 'del':
                db[item].remove({'_id':ObjectId(data['oid'])})

            expire_redis_cache(item)
        raise web.seeother('/o/ls/'+item)


class Single:
    """ 用于处理网站首页等位置的警告或提示信息
    存储在redis中, 简单键值对
    """

    opera_list = ['cr', 'del', 'info']
    SINGLE_HEAD = "Single:"

    def GET(self, opera, item=None):
        if opera in self.opera_list:
            if opera == 'info':

                def get_kv():
                    for key in rds.keys(self.SINGLE_HEAD+"*"):
                        yield (key[7:], rds.get(key))

                return render.panel2(single_list=get_kv(), opera=opera)

        return render.panel2(item=item, opera=opera)

    def POST(self, opera, item=None, key=None):

        data = web.input()

        if opera in self.opera_list:

            if opera == 'cr' :
                key = self.SINGLE_HEAD + data['key']
                rds.set(key, data['content'])

            elif opera == 'del':
                rds.delete(self.SINGLE_HEAD + item)

            expire_redis_cache(True)
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
        if key and hkey=="clear" and do=="clear":
            rds.delete(key)
            raise web.seeother("/de")
        if hkey:
            content = rds.hget(key, hkey)
        elif key:
            key_list = rds.hkeys(key)
        else:
            key_list = rds.keys("Error:Hash:*")

        return render.panel(item=False, opera='detail_error',
            key=key, hkey=hkey, key_list=key_list, content=content)

class UserManage:


    def GET(self, action="list", user_id=None):

        user_list = log_list = cuser = None
        if action == "list":
            _k = web.input(_method="GET").get('active', None)
            if _k == "all" or _k == None:
                _pre_user_list = db.users.find()
            else:
                _t = True if _k == "true" else False
                _pre_user_list = db.users.find({"active": _t})
            user_list = _pre_user_list.sort('created_date', -1)
        if action in ("detail", "update", "delete", "log") and user_id:
            cuser = db.users.find_one({'_id':ObjectId(user_id)})
        if action == "log":
            PAGE_LIMIT = 77
            _k = web.input(_method="GET").get('key', None)
            _v = web.input(_method="GET").get('value', None)
            if _k and _v:
                log_list = db.CronLog.find({
                        "user_id": ObjectId(user_id),
                        _k: _v,
                    }).sort('created_date', -1).limit(PAGE_LIMIT)
            else:
                log_list = db.CronLog.find({"user_id": ObjectId(user_id)
                    }).sort('created_date', -1).limit(PAGE_LIMIT)
        if action.endswith("active"):
            # active or deactive
            _t = True if action == "active" else False
            logging.error(_t)
            db.users.update({'_id':ObjectId(user_id)},
                      {'$set':{'active': _t,
                        'updated_date': datetime.datetime.now(),}},)
            raise web.redirect("/users/detail/%s" % user_id)
        return render.user(action=action, user_list=user_list,
                           cuser=cuser, log_list=log_list)

    def POST(self, action="create", user_id=None):

        data = web.input()
        if action == "create":
            db["users"].insert({
                'name': data['name'],
                'email' : data["email"],
                'xh': data['xh'],
                'pw': data['pw'],
                'alipay': data['alipay'],
                'active': True,
                'created_date': datetime.datetime.now(),
                'updated_date': datetime.datetime.now(),
            })
        elif action == "update":
            db.users.update({'_id':ObjectId(user_id)},
                      {'$set':{
                        'name': data['name'],
                        'email' : data["email"],
                        'xh': data['xh'],
                        'pw': data['pw'],
                        'alipay': data['alipay'],
                        'updated_date': datetime.datetime.now(),}
                      },)
            raise web.redirect("/users/detail/%s" % user_id)
        elif action == "delete":
            db.users.remove({"_id":ObjectId(data['user_id'])})
            db.CronLog.remove({"user_id": ObjectId(data['user_id'])})

        raise web.redirect("/users")



def pre_request():
    ''' 访问限制
    '''
    if web.ctx.path not in ['/', '/callback']:
        try:
            if session.uid != ADMIN_WEIBO_ID:
                raise web.seeother('/')
            web.header("Cache-Control", "no-cache")
        except AttributeError:
            raise web.seeother('/')

app.add_processor(web.loadhook(pre_request))
