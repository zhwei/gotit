#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''装饰器版的python自动缓存系统'''

import time
import hashlib
try:
    import cPickle as pickle
except ImportError:
    import pickle
from functools import wraps

from redis2s import rds

# _cache = {}


def redis_memoize(cache_name, ttl=-1):
    """
    """

    cache_name = "cache_" + cache_name

    def _decorator(function):
        def __memoize(*args, **kwargs):
            if rds.get('SINGLE_cache') == 'yes_bak':
                key = 'value'
                if rds.hexists(cache_name, key):
                    return pickle.loads(rds.hget(cache_name, key))
                else:
                    value = function(*args, **kwargs)
                    rds.hset(cache_name, key, pickle.dumps(value))
                    if ttl != -1:
                        rds.expire(cache_name, ttl)
                    return value
            else:
                return function(*args, **kwargs)
        return __memoize
    return _decorator

def expire_redis_cache(cache_name):

    rds.delete("cache_" + cache_name)

    return True


def _is_obsolete(entry, duration):
    '''是否过期'''
    if duration == -1: #永不过期
        return False
    return time.time() - entry['time'] > duration

def _compute_key(function, args,kw):
    '''序列化并求其哈希值'''
    key = pickle.dumps((function.func_name,args,kw))
    return hashlib.sha1(key).hexdigest()

# def memorize(duration = -1):
#     '''自动缓存'''
#     def _memoize(function):
#         @wraps(function) # 自动复制函数信息
#         def __memoize(*args, **kw):
#             key = _compute_key(function, args, kw)
#             #是否已缓存？
#             if key in _cache:
#                 #是否过期？
#                 if _is_obsolete(_cache[key], duration) is False:
#                     return _cache[key]['value']
#             # 运行函数
#             result = function(*args, **kw)
#             #保存结果
#             _cache[key] = {
#                 'value' : result,
#                 'time'  : time.time()
#             }
#             return result
#         return __memoize
#     return _memoize


