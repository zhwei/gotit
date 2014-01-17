#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import base64

try:
    import cPickle as pickle
except ImportError:
    import pickle

import requests
from BeautifulSoup import BeautifulSoup

import config
from utils import init_redis
from image import process_image_string



class ZF:

    #def get_random(self):
    #    return random

    def __init__(self):

        if config.random:
            with_random_url = requests.get(config.zf_url).url
            _random = with_random_url.split('/')[-2]
            self.base_url=config.zf_url+_random+'/'
        else:
            self.base_url = config.zf_url
        self.login_url = self.base_url + "Default2.aspx"
        self.code_url = self.base_url + 'CheckCode.aspx'
        self.headers = {
                'Referer':self.base_url,
                'Host':self.base_url[7:21],
                'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686;\
                        rv:18.0) Gecko/20100101 Firefox/18.0",
                'Connection':'Keep-Alive'
                }

    def pre_login(self):

        # get __VIEWSTATE
        _req = requests.get(self.base_url, headers=self.headers)
        _content = _req.content
        com = re.compile(r'name="__VIEWSTATE" value="(.*?)"')
        self.VIEWSTATE = com.findall(_content)[0]

        # get checkcode
        _req1 = requests.get(self.code_url, cookies=_req.cookies, headers=self.headers)

        import time
        import md5
        image_content = _req1.content
        time_md5 = 'user_'+md5.md5(str(time.time())).hexdigest()
        image_content=process_image_string(image_content)
        base64_image="data:image/gif;base64,"+image_content.encode('base64').replace('\n','')

        rds= init_redis()

        rds.hset(time_md5, 'checkcode', base64_image)
        rds.hset(time_md5, 'base_url', self.base_url)
        rds.hset(time_md5, 'viewstate', self.VIEWSTATE)

        pickled = pickle.dumps(_req1.cookies)
        rds.hset(time_md5, 'cookies', base64.encodestring(pickled))

        rds.pexpire(time_md5, 200000) # expire milliseconds

        return time_md5


class Login:

    def __init__(self, time_md5, xh, pw, yanzhengma):

        # init datas
        rds= init_redis()

        self.base_url = rds.hget(time_md5, 'base_url')
        self.viewstate = rds.hget(time_md5, 'viewstate')

        pickled = base64.decodestring(rds.hget(time_md5, 'cookies'))
        self.cookies = pickle.loads(pickled)

        self.yanzhengma = yanzhengma
        self.xh = xh
        self.pw = pw

        # process links
        self.login_url = self.base_url + "Default2.aspx"
        self.code_url = self.base_url + 'CheckCode.aspx'

        self.headers = {
                'Referer':self.base_url,
                'Host':self.base_url[7:21],
                'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686;\
                        rv:18.0) Gecko/20100101 Firefox/18.0",
                'Connection':'Keep-Alive'
                }


        # init post data
        data = {
            'Button1':'',
            'RadioButtonList1':"学生",
            "TextBox1":self.xh,
            'TextBox2':self.pw,
            'TextBox3':self.yanzhengma,
            '__VIEWSTATE':self.viewstate,
            'lbLanguage':'',
        }

        _req = requests.post(url=self.login_url, 
                data=data,
                cookies=self.cookies,
                headers=self.headers)

        self.cookies = _req.cookies
        # succ page content(unicode)
        self.text = _req.text



    def get_html(self, search_item):
        """
        仅用来抓取目的网页
        """
        url = self.base_url + search_item + ".aspx?xh=" + self.xh
        _req = requests.get(url = url, cookies=self.cookies, headers = self.headers)
        return _req.text

    def get_score(self):
        """
        查询当前学期成绩, 返回的内容为列表
        """
        html = self.get_html("xscjcx_dq")
        soup = BeautifulSoup(html, fromEncoding='gbk')
        result = soup.find("table", {"id": "DataGrid1"}).contents
        return result

    def get_kebiao(self):
        """
        课表 , 返回的内容为列表
        """
        html = self.get_html("xskbcx")
        soup = BeautifulSoup(html, fromEncoding='gbk')
        result = soup.find("table", {"id": "Table1"}).contents
        return result

    def get_kaoshi(self):
        """
        考试时间, 返回的内容为列表
        """
        html = self.get_html("xskscx")
        soup = BeautifulSoup(html, fromEncoding='gbk')
        result = soup.find("table", {"id": "DataGrid1"}).contents
        return result


























#zf = ZF()
#v, t = zf.pre_login()
#y = raw_input('yanzhengma>')
#zf.set_user_info('1111051046', 'zhejiushimima')
#print zf.login(y, v)
