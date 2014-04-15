#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import web

import mainsite
import apis
import manage
import wechat

from addons.config import debug_mode

# debug mode
web.config.debug = debug_mode

mapping = (
    "(www\.)?gotit.local", mainsite.app,
    "api.gotit.local", apis.app,
    "wechat.gotit.local", wechat.app,
    "manage.gotit.local", manage.app,
)

# main app
app = web.subdomain_application(mapping, globals(), autoreload=False)

# for gunicorn
application = app.wsgifunc()

def dev_server():
    app.run()

if __name__ == "__main__":

    from django.utils import autoreload
    autoreload.main(dev_server)
