#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import time

import web
from web import ctx
from web.contrib.template import render_jinja

#import redis
from bson import ObjectId
from pymongo import Connection
from weibo import APIClient, APIError

render = render_jinja('templates', encoding='utf-8')


APP_KEY = '4001516920' # app key
APP_SECRET = '44a4fb573339e30a901249978a1322b9' # app secret
CALLBACK_URL = 'http://gotit.asia:8080/manage/callback' # callback url
CLIENT = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
AUTH_URL=CLIENT.get_authorize_url()


db = Connection(host='127.0.0.1',port=27017)['gotit']
#db = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

urls = (
    '$', 'ologin',
    '/callback', 'callback',
    '/panel', 'panel',
    '/o/(.+)/(.+)/(.+)', 'update',
    '/o/(.+)/(.+)', 'update',
)

manage = web.application(urls, locals())


class ologin:

    def GET(self):
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
            if uid != 2674044833:
                return render.ologin(auth_url=AUTH_URL, error='欢迎尝试')
            ctx.session['uid'] = uid
        except APIError:
            raise web.seeother('../manage')


        raise web.seeother('panel')


def pre_request():
    ''' 访问限制
    '''

    if web.ctx.path not in ['', '/callback']:
        try:
            if ctx.session.uid != 2674044833:
                raise web.seeother('../manage')
        except AttributeError:
            raise web.seeother('../manage')


class panel:

    def GET(self):

        return render.panel(item=False)


class update:

    item_list = ['donate', 'zheng', 'cet', 'notice']
    opera_list = ['cr', 'del', 'ls', 'info']

    def GET(self, opera, item, oid=None):

        if item in self.item_list and opera in self.opera_list:

            if opera == 'ls':
                ls = db[item].find()
                return render.panel(item=item, opera=opera, ls=ls)

        return render.panel(item=item, opera=opera, oid=oid)

    def POST(self, opera, item, oid=None):

        data = web.input()

        if item in self.item_list and opera in self.opera_list:

            if opera == 'cr' :
                if item == 'donate':
                    db.donate.insert({
                        'name':data['name'],
                        'much':data['much'],
                        'datetime': datetime.datetime.now(),
                        })
                else:
                    db[item].insert({
                        'content':data['content'],
                        'datetime': datetime.datetime.now(),
                        })

            elif opera == 'del':
                db[item].remove({'_id':ObjectId(data['oid'])})

        raise web.seeother('/o/ls/'+item)

manage.add_processor(web.loadhook(pre_request))
