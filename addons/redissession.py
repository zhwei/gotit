#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from web.session import Store


import redis

class RedisStore(Store):
    """
    Store for saving a session in redis
    """

    def __init__(self, ip="127.0.0.1", port=6379, db=0):

        self.db = redis.StrictRedis(host=ip, port=port, db=db)

    def __contains__(self, key):
        "判定是否存在key"
        return bool(self.db.exists(key))

    def __getitem__(self, key):

        atime, v = self.db.get(key)
        self[key] = v  # update time
        return v

    def __setitem__(self, key, value):

        data = (time.time(), value)
        self.db.set(key,data)

    def __delitem__(self, key):

        self.db.delete(key)

    def cleanup(self, timeout):
        now = time.time()
        for k in self.db.keys('*'):
            atime, v = self.db.get(k)
            if now - atime > timeout:
                del self[k]
