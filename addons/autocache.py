#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''装饰器版的python自动缓存系统'''

import hashlib
try:
    import cPickle as pickle
except ImportError:
    import pickle
from functools import wraps

from redis2s import rds
from config import DEBUG

def _compute_key(function, args,kw):
    '''序列化并求其哈希值'''
    key = pickle.dumps((function.func_name,args,kw))
    return hashlib.sha1(key).hexdigest() 

def _key_name(key):
    """返回Redis中实际key name"""
    return "Cache:%s" % key

def redis_memoize(ttl=-1, key=False):
    '''Auto cache, default never expire
    Modify From: https://github.com/ma6174/pycache
    '''
    def _memoize(function):
        @wraps(function) # 自动复制函数信息
        def __memoize(*args, **kw):
            if DEBUG: return function(*args, **kw)
            real_key = _key_name(key if key else _compute_key(function,
                                                    args, kw))
            #是否已缓存？
            if rds.exists(real_key):
                return rds.get(real_key)
            else:
                # 运行函数
                result = function(*args, **kw)
                #保存结果
                rds.set(real_key, result)
                rds.expire(real_key, ttl)
                return result
        return __memoize
    return _memoize

def expire_redis_cache(cache_name):
    """ if cache equals True, Remove all cache"""
    if cache_name == True:
        for key in rds.keys("Cache:*"):
            rds.delete(key)
    else:
        rds.delete("Cache:" + cache_name)
    return True