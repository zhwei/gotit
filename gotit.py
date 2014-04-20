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
from addons.RedisStore import RedisStore

web.config.debug = debug_mode

mapping = (
    "www.t.gotit.asia", mainsite.app,
    "api.t.gotit.asia", apis.app,
    "wechat.t.gotit.asia", wechat.app,
    "manage.t.gotit.asia", manage.app,
)


# main app
app = web.subdomain_application(mapping)

# for gunicorn
application = app.wsgifunc()
