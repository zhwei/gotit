#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
from web.session import Store

import redis


class RedisStore(Store):
    """
    Store for saving a session in redis
    """

    def __init__(self, ip="127.0.0.1", port=6379, db=0):

        self.db = redis.StrictRedis(host=ip, port=port, db=db)
        self.timeout = web.config.session_parameters['timeout']

    def __contains__(self, key):
        #"判定是否存在key"
        return bool(self.db.exists(key))

    def __getitem__(self, key):

        v = self.db.getset(key, self.timeout)
        self[key] = v  # update time
        return eval(v)

    def __setitem__(self, key, value):

        self.db.setex(key, 600, value)

    def __delitem__(self, key):
        self.db.delete(key)

    def cleanup(self, timeout):
        pass