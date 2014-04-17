#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import web

import mainsite
import apis
import manage
import wechat

# debug mode
from addons.config import debug_mode
web.config.debug = debug_mode

mapping = (
    "(www\.)?gotit.asia", mainsite.app,
    "api.gotit.asia", apis.app,
    "wechat.gotit.asia", wechat.app,
    "manage.gotit.asia", manage.app,
)


# main app
app = web.subdomain_application(mapping, globals(), autoreload=False)

# session
# if web.config.get('_session') is None:
#     session = web.session.Session(app, RedisStore(), {'count': 0, 'xh':False})
#     web.config._session = session
# else:
#     session = web.config._session

# # web server
# def session_hook():
#     """ share session with sub apps
#     """
#     web.ctx.session = session
# app.add_processor(web.loadhook(session_hook))

# for gunicorn
application = app.wsgifunc()
