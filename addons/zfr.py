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
import logging
try:
    import cPickle as pickle
except ImportError:
    import pickle
from urlparse import urlparse

import requests
from BeautifulSoup import BeautifulSoup

import config
import errors
import image
from redis2s import rds
from utils import not_error_page, get_unique_key
import mongo2s

USER_RDS_PREFIX = "User:Zf:"

def prepare_request(base_url, just_header=False):
    # process links
    _parse = urlparse(base_url)
    headers = {
            'Referer':base_url,
            'Host':_parse.netloc,
            'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686;\
                    rv:18.0) Gecko/20100101 Firefox/30.0",
            'Connection':'Keep-Alive'
            }

    if just_header: return headers
    login_url = base_url + "Default2.aspx"
    code_url = base_url + 'CheckCode.aspx'
    return login_url, code_url, headers

def safe_get(*args, **kwargs):
    try:
        _req = requests.get(*args, **kwargs)
        not_error_page(_req.text)
    except requests.ConnectionError:
        raise errors.RequestError('无法连接到正方教务系统')
    return _req

def safe_post(*args, **kwargs):
    try:
        _req = requests.post(*args, **kwargs)
        not_error_page(_req.text)
    except requests.ConnectionError:
        raise errors.RequestError('无法连接到正方教务系统')
    return _req

def get_viewstate(page):
    """get __VIEWSTATE
    """
    try:
        com = re.compile('name="__VIEWSTATE".*?value="(.*?)"')
        # logging.error(com.findall(page))
        vs = com.findall(page)[0]
    except IndexError:
        import time
        rds.hset('Error:Hash:zfr:GetVsIndexError', time.time(), page)
        raise errors.PageError("请求错误, 请重新查询")
    return vs


class ZF:
    """ 处理用户第一次请求时的数据
    """
    def __init__(self):

        if config.random:
            with_random_url = safe_get(config.zf_url).url
            _random = with_random_url.split('/')[-2]
            self.base_url=config.zf_url+_random+'/'
        else:
            self.base_url = config.zf_url

        self.login_url, self.code_url, self.headers = prepare_request(self.base_url)

    def pre_login(self):

        # get __VIEWSTATE
        _req = safe_get(self.base_url, headers=self.headers)
        self.VIEWSTATE = get_viewstate(_req.text)
        #_content = _req.content
        #com = re.compile(r'name="__VIEWSTATE" value="(.*?)"')
        #self.VIEWSTATE = com.findall(_content)[0]

        # create uid
        uid = get_unique_key(prefix=USER_RDS_PREFIX)

        # get checkcode
        #checkcode=self.get_checkcode(uid)
        _req1 = safe_get(self.code_url, cookies=_req.cookies, headers=self.headers)
        image_content = _req1.content
        image_content=image.process_image_string(image_content)
        base64_image="data:image/gif;base64,"+image_content.encode('base64').replace('\n','')

        pickled_cookies = pickle.dumps(_req.cookies)
        # store in redis
        rds.hmset(uid, {
                "checkcode" : base64_image,
                "base_url"  : self.base_url,
                "viewstate" : self.VIEWSTATE,
                'cookies'   : base64.encodestring(pickled_cookies),
            })
        # set expire time(milliseconds)
        rds.pexpire(uid, config.COOKIES_TIME_OUT)

        return uid

    def get_checkcode(self, uid):

        try:
            pickled = base64.decodestring(rds.hget(uid, 'cookies'))
        except TypeError:
            raise errors.PageError("请求错误, 请重新查询")
        self.cookies = pickle.loads(pickled)
        rds.pexpire(uid, config.COOKIES_TIME_OUT) # 延时
        # get checkcode
        _req1 = safe_get(self.code_url, cookies=self.cookies, headers=self.headers)
        image_content = _req1.content
        img=image.process_image_string(image_content)
        return img


class Login:
    """ 用户登录
    以及后续的查询操作
    """

    def init_from_form(self, uid, post_content):
        """ 在用户提交帐号密码的时候初始化对象的必要数据
        """
        self.xh = post_content.get('xh')
        self.pw = post_content.get('pw')
        self.uid = uid
        try:
            # collect checkcode
            mongo2s.collect_checkcode(post_content.get('verify', ''))
            self.verify = post_content['verify'].decode("utf-8").encode("gb2312")
        except UnicodeEncodeError:
            raise errors.PageError('验证码错误')

    def init_from_redis(self):
        """ 用户后续查询时从redis获取数据
        """
        # init datas
        self.base_url = rds.hget(self.uid, 'base_url')
        self.viewstate = rds.hget(self.uid, 'viewstate')
        _uid = rds.hget(self.uid, 'cookies')
        if _uid is None:
            raise errors.PageError('请重新登录！')
        pickled = base64.decodestring(_uid)
        self.cookies = pickle.loads(pickled)
        rds.pexpire(self.uid, config.COOKIES_TIME_OUT) # 延时

    def login(self, uid, post_content):

        self.init_from_form(uid, post_content)
        self.init_from_redis()
        self.login_url, self.code_url, self.headers = prepare_request(self.base_url)
        # init post data
        data = {
            'Button1':'',
            'RadioButtonList1':"学生",
            "txtUserName":self.xh,
            'TextBox2':self.pw,
            'txtSecretCode':self.verify,
            '__VIEWSTATE':self.viewstate,
            'lbLanguage':'',
        }
        _req = safe_post(
                url=self.login_url,
                data=data,
                cookies=self.cookies,
                headers=self.headers)

        #self.cookies = _req.cookies

        not_error_page(_req.text) # 判断请求是否出错
        rds.hset(uid, "xh", self.xh)
        rds.pexpire(uid, config.COOKIES_TIME_OUT) # 延时

    def no_code_login(self, post_content):
        """ 无验证码登录 """
        if config.random:
            with_random_url = safe_get(config.zf_url).url
            _random = with_random_url.split('/')[-2]
            self.base_url=config.zf_url+_random+'/'
        else:
            self.base_url = config.zf_url

        self.xh = post_content.get('xh')
        self.pw = post_content.get('pw')
        self.login_url = self.base_url + "Default6.aspx"
        self.headers = prepare_request(self.base_url, just_header=True)
        _req1 = safe_get(self.login_url, headers=self.headers)
        _viewstate = get_viewstate(_req1.content)
        self.cookies = _req1.cookies
        data = {
            'tname':'',
            'tbtns':'',
            'tnameXw':'yhdl',
            'tbtnsXw':'yhdl|xwxsdl',
            'tbtnsXm':'',
            'rblJs':"学生",
            "txtYhm":self.xh,
            'txtXm':"",
            'txtMm':self.pw,
            '__VIEWSTATE': _viewstate,
            'btnDl': '登 录',
        }
        safe_post(
            url=self.login_url,
            data=data,
            cookies = _req1.cookies,
            headers=self.headers
        )
        uid = get_unique_key(USER_RDS_PREFIX)
        pickled_cookies = pickle.dumps(self.cookies)
        rds.hmset(uid, {
                "base_url"  : self.base_url,
                'cookies'   : base64.encodestring(pickled_cookies),
                "xh"        : self.xh,
            })
        rds.pexpire(uid, config.COOKIES_TIME_OUT) # 延时
        return uid

    def init_after_login(self, uid, xh=None):
        """初始化二次查找需要的数据
        用户已经登录，从redis中获取cookies等数据
        进行第二次抓取
        """
        self.xh = xh or rds.hget(uid, "xh")
        self.uid= uid
        self.init_from_redis()
        self.login_url, self.code_url, self.headers = prepare_request(self.base_url)


    def get_html(self, search_item):
        """
        仅用来抓取目的网页
        """
        url = self.base_url + search_item + ".aspx?xh=" + self.xh
        _req = safe_get(url = url, cookies=self.cookies, headers = self.headers, allow_redirects=False)

        not_error_page(_req.text)

        return _req.text

    def get_score(self):
        """
        查询当前学期成绩, 返回的内容为列表
        """
        html = self.get_html("xscjcx_dq")
        soup = BeautifulSoup(html, fromEncoding='gbk')
        result = soup.find("table", {"id": "DataGrid1"}).contents
        return (result, )

    def get_timetable(self):
        """
        课表 , 返回的内容为列表
        """
        html = self.get_html("xskbcx")
        soup = BeautifulSoup(html, fromEncoding='gbk')
        result = soup.find("table", {"id": "Table1"}).contents
        ret2 = soup.find("table", {"id": "Table3"}).contents
        return (result, ret2)

    def get_kaoshi(self):
        """
        考试时间, 返回的内容为列表
        """
        html = self.get_html("xskscx")
        soup = BeautifulSoup(html, fromEncoding='gbk')
        result = soup.find("table", {"id": "DataGrid1"}).contents
        return (result,)

    def more_kebiao(self):
        """ 其他学期课表
        """
        _com = re.compile('value="(\d{4}-\d{4})"')
        html = self.get_html("xskbcx")
        result = _com.findall(html)
        return result

    def years(self, url, year, xq):
        """ 其他学期课表
        """
        html = self.get_html("xskbcx")
        viewstate = get_viewstate(html)
        data = {
                "__EVENTTARGET":"xqd",
                "__EVENTARGUMENT":"",
                "__VIEWSTATE":viewstate,
                "xnd": year,
                "xqd": xq,
                }
        #url = self.base_url + 'xskbcx' + ".aspx?xh=" + self.xh
        _ret = requests.post(url=url, data=data,cookies=self.cookies, headers=self.headers)
        soup = BeautifulSoup(_ret.text, fromEncoding='gbk')
        result = soup.find("table", {"id": "Table1"}).contents
        return result

    def get_last_timetable(self):
        """二次提交
        """
        html = self.get_html("xskbcx")
        viewstate = get_viewstate(html)
        data = {
                "__EVENTTARGET":"xqd",
                "__EVENTARGUMENT":"",
                "__VIEWSTATE":viewstate,
                "xnd":'2014-2015',
                "xqd":"1",
                }
        url = self.base_url + 'xskbcx' + ".aspx?xh=" + self.xh
        _ret = requests.post(url=url, data=data,cookies=self.cookies, headers=self.headers)
        soup = BeautifulSoup(_ret.text, fromEncoding='gbk')
        ret1 = soup.find("table", {"id": "Table1"}).contents
        ret3 = soup.find("table", {"id": "Table3"}).contents
        return (ret1, ret3)


    def get_last_score(self):
        """二次提交
        """
        html = self.get_html("xscjcx_dq")
        viewstate = get_viewstate(html)
        data = {
                "__EVENTTARGET":"",
                "__EVENTARGUMENT":"",
                "__VIEWSTATE":viewstate,
                "ddlxn":"2013-2014",
                "ddlxq":"1",
                "btnCx":" 查  询 ",
                }
        url = self.base_url + 'xscjcx_dq' + ".aspx?xh=" + self.xh
        _ret = requests.post(url=url, data=data,cookies=self.cookies, headers=self.headers)
        soup = BeautifulSoup(_ret.text, fromEncoding='gbk')
        result = soup.find("table", {"id": "DataGrid1"}).contents
        return (result, )
