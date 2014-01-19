#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 使用requests替换原来的urllib和urllib2
#
# 将每个用户的cookies缓存在redis中，
# 替换以前的将对象保存在内存中
#

import re
import base64

try:
    import cPickle as pickle
except ImportError:
    import pickle

import requests
from BeautifulSoup import BeautifulSoup

import config
import errors
from utils import init_redis, not_error_page
from image import process_image_string


def process_links(base_url):
    # process links
    login_url = base_url + "Default2.aspx"
    code_url = base_url + 'CheckCode.aspx'
    headers = {
            'Referer':base_url,
            'Host':base_url[7:21],
            'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686;\
                    rv:18.0) Gecko/20100101 Firefox/18.0",
            'Connection':'Keep-Alive'
            }
    return login_url, code_url, headers

def safe_get(*args, **kwargs):
    try:
        _req = requests.get(*args, **kwargs)
        not_error_page(_req.text)
    except requests.ConnectionError:
        raise errors.ZfError('无法连接到正方教务系统')
    return _req

def safe_post(*args, **kwargs):
    try:
        _req = requests.post(*args, **kwargs)
        not_error_page(_req.text)
    except requests.ConnectionError:
        raise errors.ZfError('无法连接到正方教务系统')
    return _req

class ZF:

    def __init__(self):

        if config.random:
            with_random_url = safe_get(config.zf_url).url
            _random = with_random_url.split('/')[-2]
            self.base_url=config.zf_url+_random+'/'
        else:
            self.base_url = config.zf_url

        self.login_url, self.code_url, self.headers = process_links(self.base_url)

    def pre_login(self):

        # get __VIEWSTATE
        _req = safe_get(self.base_url, headers=self.headers)
        _content = _req.content
        com = re.compile(r'name="__VIEWSTATE" value="(.*?)"')
        self.VIEWSTATE = com.findall(_content)[0]

        # get checkcode
        _req1 = safe_get(self.code_url, cookies=_req.cookies, headers=self.headers)

        import time
        import md5
        image_content = _req1.content
        time_md5 = 'user_'+md5.md5(str(time.time())).hexdigest()
        image_content=process_image_string(image_content)
        base64_image="data:image/gif;base64,"+image_content.encode('base64').replace('\n','')

        # store in redis
        rds= init_redis()
        rds.hset(time_md5, 'checkcode', base64_image)
        rds.hset(time_md5, 'base_url', self.base_url)
        rds.hset(time_md5, 'viewstate', self.VIEWSTATE)

        # pickle cookies
        pickled = pickle.dumps(_req1.cookies)
        rds.hset(time_md5, 'cookies', base64.encodestring(pickled))

        # set expire time(milliseconds)
        rds.pexpire(time_md5, 200000)

        return time_md5


class Login:

    def init_from_form(self, time_md5, post_content):

        self.xh = post_content['xh']
        self.pw = post_content['pw']
        self.time_md5 = time_md5
        self.verify = post_content['verify'].decode("utf-8").encode("gb2312")

    def init_from_redis(self):
        # init datas
        rds= init_redis()
        self.base_url = rds.hget(self.time_md5, 'base_url')
        self.viewstate = rds.hget(self.time_md5, 'viewstate')
        pickled = base64.decodestring(rds.hget(self.time_md5, 'cookies'))
        self.cookies = pickle.loads(pickled)
        rds.pexpire(self.time_md5, 200000) # 延时

    def login(self, time_md5, post_content):

        self.init_from_form(time_md5, post_content)
        self.init_from_redis()
        self.login_url, self.code_url, self.headers = process_links(self.base_url)

        # init post data
        data = {
            'Button1':'',
            'RadioButtonList1':"学生",
            "TextBox1":self.xh,
            'TextBox2':self.pw,
            'TextBox3':self.verify,
            '__VIEWSTATE':self.viewstate,
            'lbLanguage':'',
        }

        _req = safe_post(
                url=self.login_url,
                data=data,
                cookies=self.cookies,
                headers=self.headers)

        self.cookies = _req.cookies

        not_error_page(_req.text)


    def init_after_login(self, time_md5, xh):
        """初始化二次查找需要的数据
        用户已经登录，从redis中获取cookies等数据
        进行第二次抓取
        """
        self.xh = xh
        self.time_md5=time_md5
        self.init_from_redis()
        self.login_url, self.code_url, self.headers = process_links(self.base_url)


    def get_html(self, search_item):
        """
        仅用来抓取目的网页
        """
        url = self.base_url + search_item + ".aspx?xh=" + self.xh
        _req = safe_get(url = url, cookies=self.cookies, headers = self.headers)

        not_error_page(_req.text)

        return _req.text

    #self.content_dict = {
    #        'xscjcx_dq':'DataGrid1',  # 成绩
    #        'xskbcx':'Table1',        # 课表
    #        'xskscx':'DataGrid1',     # 考试时间
    #        }

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
