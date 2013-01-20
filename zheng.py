#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import random
import re
import urllib
import urllib2
import cookielib
from BeautifulSoup import BeautifulSoup

global URL
URL = "http://210.44.176.133"

class ZHENG:
    _xh = None
    _pw = None
    func = None

    def __init__(self,xh,pw,func):
        self._xh = xh
        self._pw = pw
        self.func = func

    def __get_base_url(self):
        target = urllib2.urlopen(URL)
        with_random_url = target.geturl()
        base_url = with_random_url[-13]
        return base_url
    def __get_login_url(self):
        base_url = self.__get_base_url()
        login_url = base_url + "Default3.aspx"
        return login_url

    def __get_url(self):
        base_url = self.__get_base_url()
        func_url = base_url + self.func + "aspx?xh=" + self._xh
        return func_url
    
    def login(self):
        login_url = __get_login_url()

        html1 = urllib.urlopen(login_url).read()
        a = re.compile('<input type="hidden" name="__VIEWSTATE" value="(.*)" />')
        try:
            VIEWSTATE = a.findall(html1)[0]
        except:
            print("can not get viewstate")
        #cookie
        student_cookie = cookielib.CookieJar()
        #login
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(student_cookie))
        data = '__VIEWSTATE='+VIEWSTATE+'&TextBox1='+self._xh+'&TextBox2='+self._pw+'&ddl_js=%D1%A7%C9%FA&Button1=+%B5%C7+%C2%BC+'

        login_request = urllib2.Request(login_url, data)
        opener.open(login_request, data)
        status = opener.open(login_request, data).read()
        print(status.decode("gb2312").encode("utf-8"))
        string = "密码错误！！"
        key = string.decode('utf-8').encode('gb2312')
        t = status.find(key)

        return opener
        except:
            # out = ["<div class='alert alert-error'><h4><center><strong>Login ERROR!!!</strong><center></h4></div>",]
            return "error"



    def get_table(self):
        login_url = self.__get_base_url()
        login_html = urllib2.urlopen(login_url).read()
        view_re = re.compile('<input type="hidden" name="__VIEWSTATE" value="(.*)" />')
        VIEWSTATE = view_re.findall(login_html)[0]

        student_cookie = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(student_cookie))
        data = '__VIEWSTATE='+VIEWSTATE+'&TextBox1='+self._xh+'&TextBox2='+self._pw+'&ddl_js=%D1%A7%C9%FA&Button1=+%B5%C7+%C2%BC+'
        login_request = urllib2.Request(login_url, data)
        opener.open(login_request, data)

        #验证是否登录成功
        status = opener.open(login_request, data).read()
        print(status.decode("gb2312").encode("utf-8"))
        string = "密码错误！！"
        key = string.decode('utf-8').encode('gb2312')
        t = status.find(key)
        if t != -1:
            result = [u"<div class='alert alert-error'><h4><center><strong>用户名或密码错误!</strong><center></h4></div>",]
            return result
        else:
            target_url = self.__get_url()
            print "++++++++++++++++++++++++++"
            target_html = opener.open(target_url).read()
            # print target_html
            #get table
            soup = BeautifulSoup(target_html, fromEncoding='gbk')
            if self.func == "xskbcx":
                table_name = "Table1"
            else:
                table_name = "DataGrid1"
            table = soup.find("table", {"id": table_name}) #table is class
            # if table:
            result = table.contents
            # else:
                # result = ["<div class='alert alert-error'><h4><center><strong>System is Busy,Please Try Again!</strong><center></h4></div>",]
            return result













































