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
    "(www\.)?*.*", mainsite.app,
    "api.gotit.asia", apis.app,
    "wechat.gotit.asia", wechat.app,
    "manage.gotit.asia", manage.app,
)

# main app
app = web.subdomain_application(mapping, globals(), autoreload=False)

# for gunicorn
application = app.wsgifunc()
