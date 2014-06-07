#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import base64
try:
    import cPickle as pickle
except ImportError:
    import pickle
import logging

import web
from web.session import Store

import redis

SESSION_MARKUP='Session:'


class RedisStore(Store):
    """
    Store for saving a session in redis
    """

    def __init__(self, ip="127.0.0.1", port=6379, db=0, markup=None, timeout=None):

        self.db = redis.StrictRedis(host=ip, port=port, db=db)
        # self.timeout = web.webapi.config.session_parameters.timeout
        self.markup = markup or SESSION_MARKUP
        self.timeout = timeout or 600

    def __contains__(self, key):
        #"判定是否存在key"
        try:
            return bool(self.db.exists(self.markup+key))
        except redis.ConnectionError:
            sys.stderr.write('Error: Can not Connect Redis')
            sys.exit()

    def __getitem__(self, key):

        v = self.db.get(self.markup+key)
        if v:
            self.db.expire(self.markup+key, self.timeout)
            return self.decode(v)
        else:
            raise KeyError

    def __setitem__(self, key, value):

        self.db.setex(self.markup+key, self.timeout, self.encode(value))

    def __delitem__(self, key):
        self.db.delete(self.markup+key)

    def cleanup(self, timeout):
        pass

    def decode(self, session_data):
        """ 重写decode方法
        避免：Error: Incorrect padding 报错

        Decode base64, padding being optional.

        :param session_data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.
        """
        missing_padding = 4 - len(session_data) % 4
        if missing_padding:
            session_data += b'='* missing_padding

        pickled = base64.decodestring(session_data)
        try:
            return pickle.loads(pickled)
        except pickle.UnpicklingError:
            from time import time
            self.db.hset('Error:Hash:UnpicklingError', time(), pickled)
            return pickle.loads(pickled)
