#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import re
import urllib
import urllib2
import cookielib
from BeautifulSoup import BeautifulSoup

from cache import Cache

global URL
URL = "http://210.44.176.133"
headers = {'Referer':'http://210.44.176.132/','Host':'210.44.176.132','User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",'Connection':'Keep-Alive'}

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


class ZHENG:
    _xh = None
    _pw = None
    func = None
    # headers
    headers = {'Referer':'http://210.44.176.132/','Host':'210.44.176.132','User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",'Connection':'Keep-Alive'}

    def __init__(self,xh,pw,func):
        self._xh = xh
        self._pw = pw
        self.func = func
        #cookie
        cookies = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
        urllib2.install_opener(self.opener)


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
        func_url = base_url + self.func + ".aspx?xh=" + self._xh# + "&xm=%D5%C5%CE%C0&gnmkdm=N121603"
        return func_url

    def login(self,base_url):
        login_url = self.__get_login_url(base_url)

        # catch the view arg
        html1 = urllib.urlopen(login_url).read()
        print login_url
        a = re.compile('<input type="hidden" name="__VIEWSTATE" value="(.*)" />')
        VIEWSTATE = a.findall(html1)[0]
        
        
        # recg the verigy code
        req = urllib2.Request(base_url + 'CheckCode.aspx',headers = self.headers)
        a = self.opener.open(req).read()
        file('a.gif','wb').write(a)
        from sec_code.recg import verify
        check = verify('a.gif')
        print check + "@@@@@@@@@@@@@@@@@@@@"

        data = {
                'Button1':'',
                'RadioButtonList1':"学生",
                "TextBox1":self._xh,
                'TextBox2':self._pw,
                'TextBox3':check,
                '__VIEWSTATE':VIEWSTATE,
                'lbLanguage':'',
                }
        post_data = urllib.urlencode(data)

        headers = {'Referer':'http://210.44.176.132/Default2.aspx','Host':'210.44.176.132','User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",'Connection':'keep-alive'}

        login_request = urllib2.Request(login_url, post_data, headers = headers)

        #opener.open(login_request, post_data).read()
        status = self.opener.open(login_request, post_data).readlines()[0]
        print str(status).decode('gbk')

        print "*************************************************************"
        #string = ("密码错误！！","验证码不正确！！",)

        #k = 0
        #while k < len(string) - 1:
        #    key = string[k].decode('utf-8').encode('gb2312')
        #    t = status.find(key)
        #    if t != -1:
        #        if k == 0:
        #            print(self._xh+"    login error")
        #            return 'err0'
        #        elif k == 1:
        #            print ("************* verify error")
        #            self.login(self,base_url)
        #            return 'err1'
        #    k = k + 1


    def get_table(self):
        base_url = self.cache_url()

        self.login(base_url)

        target_url = self.__get_url(base_url)
        #logger = initlog("log/zheng.log")
        #logger.info(target_url)
        self.headers = {'Referer':'http://210.44.176.132/xs_main.aspx?xh=1111051046','Host':'210.44.176.132','User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",'Connection':'keep-alive'}
        target_html = self.opener.open(target_url).read()
        print target_url
        print target_html.decode('gbk')
        #adsf = file('adsf.html','wb')
        #adsf.write(target_html)
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
