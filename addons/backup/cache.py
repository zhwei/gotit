#!/usr/bin/env python
#coding=utf-8
import urllib2
from time import time
class Cache:
    '''简单的缓存系统'''
    def __init__(self):
        '''初始化'''
        self.mem = {}
        self.time = {}

    def set(self, key, data, age=-1):
        '''保存键为key的值，时间位age'''
        self.mem[key] = data
        if age == -1:
            self.time[key] = -1
        else:
            self.time[key] = time() + age
        return True

    def get(self,key):
        '''获取键key对应的值'''
        if key in self.mem.keys():
            if self.time[key] == -1 or self.time[key] > time():
                return self.mem[key]
            else:
                self.delete(key)
                return None
        else:
            return None

    def delete(self,key):
        '''删除键为key的条目'''
        del self.mem[key]
        del self.time[key]
        return True

#def get_base_url():
#    '''get the base url'''
#    URL = 'http://210.44.176.133'
#    target = urllib2.urlopen(URL)
#    with_random_url = target.geturl()
#    base_url = with_random_url[:-13]
#    return base_url
#
#if __name__ == "__main__":
#    cache = Cache()
#    url = get_base_url()
#    cache.set('url',url,5)   #a的值是'aaaa',生存时间位5秒
#    while True:
#        result = cache.get("url")
#        if result is None:
#            result = get_base_url()
#            cache.set("url",result,10)
#        return result
