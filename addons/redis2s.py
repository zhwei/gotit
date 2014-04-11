#!/usr/bin/env python
# -*- coding: utf-8 -*-

import redis

# Redis Tools

def init_redis():
    redis_server = redis.StrictRedis(host='localhost', port=6379, db=0)
    return redis_server

rds = init_redis()


def get_count(pattern="*"):
    """ 获取符合条件的key数目
    """
    rds = init_redis()
    return len(rds.keys(pattern))
