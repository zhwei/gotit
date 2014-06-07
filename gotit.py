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
from addons.config import DEBUG, domains

web.config.debug = DEBUG

mapping = (
    domains['main'], mainsite.app,
    domains['www'], mainsite.app,
    domains['api'], apis.app,
    domains['wechat'], wechat.app,
    domains['manage'], manage.app,
)


# main app
app = web.subdomain_application(mapping)

# for gunicorn
application = app.wsgifunc()
