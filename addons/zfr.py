#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
#import os

import requests
from BeautifulSoup import BeautifulSoup

import config
from utils import init_redis
from image import process_image_string



class ZF:

    def get_random(self):
        with_random_url = requests.get(config.zf_url).url
        random = with_random_url.split('/')[-2]
        return random

    def __init__(self):

        if config.random:
            self.base_url=config.zf_url+self.get_random()+'/'
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

    def set_user_info(self,xh,pw):
        self.xh = xh
        self.pw = pw


    def pre_login(self):

        # get __VIEWSTATE
        _req = requests.get(self.base_url, headers=self.headers)
        _content = _req.content
        com = re.compile(r'name="__VIEWSTATE" value="(.*?)"')
        self.VIEWSTATE = com.findall(_content)[0]

        # get checkcode
        _req1 = requests.get(self.code_url, cookies=_req.cookies, headers=self.headers)
        self.cookies = _req1.cookies
        image_content = _req1.content

        import time
        import md5
        time_md5 = md5.md5(str(time.time())).hexdigest()
        image_content=process_image_string(image_content)
        base64 = image_content.encode('base64').replace('\n','')

        redis_server = init_redis()
        redis_server.setex('CheckCode_'+time_md5, 100,base64)
        return self.VIEWSTATE, time_md5


    def login(self, yanzhengma, VIEWSTATE):

        yanzhengma = yanzhengma.decode("utf-8").encode("gb2312")
        data = {
            'Button1':'',
            'RadioButtonList1':"学生",
            "TextBox1":self.xh,
            'TextBox2':self.pw,
            'TextBox3':yanzhengma,
            '__VIEWSTATE':VIEWSTATE,
            'lbLanguage':'',
        }

        _req = requests.post(url=self.login_url, data=data, cookies=self.cookies, headers=self.headers)
        ret = _req.text

        return ret



    def get_html(self, search_item):
        """
        仅用来抓取目的网页
        """
        url = self.base_url + search_item + ".aspx?xh=" + self.xh
        _req = requests.get(url = url, headers = self.headers)
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
