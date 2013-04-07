#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import re
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup

from cache import Cache

global URL
URL = "http://210.44.176.133"

def initlog(logfile):
    import logging
    import os
    if os.path.exists('log'):
        pass
    else:
        os.mkdir('log')
    if os.path.isfile(logfile):
        pass
    else:
        os.mknod(logfile)
    logger    = logging.getLogger()
    hdlr      = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    return logger



def __get_base_url(self):
    target = urllib2.urlopen(URL)
    with_random_url = target.geturl()
    base_url = with_random_url[:-13]
    base_url = 'http://210.44.176.132/'
    return base_url

def cache_url(self):
    '''cache the base_url'''
    cache = Cache()
    url = self.__get_base_url()
    cache.set('url',url,500)
    while True:
        result = cache.get('url')
        if result is None:
            result = self.__get_base_url()
            cache.set('url',result,500)
        return result

def __get_login_url(self,base_url):
    login_url = base_url + "Default2.aspx"
    return login_url

def __get_url(self,base_url):
    func_url = base_url + self.func + ".aspx?xh=" + self._xh
    return func_url


def get_table(self):
    base_url = self.cache_url()

    self.login(base_url)

    target_url = self.__get_url(base_url)
    target_html = self.opener.open(target_url).read()
    print target_url
    print target_html.decode('gbk')

    soup = BeautifulSoup(target_html, fromEncoding='gbk')
    if self.func == "xskbcx":
        table_name = "Table1"
    else:
        table_name = "DataGrid1"

    table = soup.find("table", {"id": table_name}) #table is class
    result = table.contents
    return result

def get_json(self):
    import json
    table = self.get_table()
    score_re = re.compile('<td>.*</td><td>.</td><td>.*</td><td>(.*)</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>(.*)</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td>')
    result = score_re.findall(str(table).decode('utf-8'))
    dic = {}
    for i in result:
        (key,value) = i
        dic[key] = value
    json = json.dumps(dic)
    return json
