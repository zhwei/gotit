#!/usr/bin/env python
# -*- coding: utf-8 -*-

from code import app
from addons.tools import init_redis

def dev_server():
    app.run()

if __name__ == "__main__":
    r = init_redis()
    r.flushdb()
    print "clear redis db"
    from django.utils import autoreload
    autoreload.main(dev_server)
