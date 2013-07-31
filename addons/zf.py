#!/usr/bin/env python
#coding=utf-8
import cookielib
import urllib
import urllib2
import re
from BeautifulSoup import BeautifulSoup
import config
#import os
from image import process_image


#def get_viewstate

class ZF():

    def get_base_url(self):
        target = urllib2.urlopen(config.zf_url)
        with_random_url = target.geturl()
        base_url = with_random_url[:-13]
        return base_url

    def __init__(self):
        self.cookies = cookielib.LWPCookieJar()
        self.opener =urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
        urllib2.install_opener(self.opener)

        if config.random:
            self.base_url = self.get_base_url()
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
        """
        初始化登陆, 获取viewstate参数 创建验证码图片
        放置在/static/pic/中, 并且返回验证码图片名
        """
        #get __VIEWSTATE
        req = urllib2.Request(self.base_url,headers=self.headers)
        ret = self.opener.open(req)
        page = ret.read()
        com = re.compile(r'name="__VIEWSTATE" value="(.*?)"')
        all = com.findall(page)
        __VIEWSTATE =  all[0]
        self.VIEWSTATE = __VIEWSTATE
        #print __VIEWSTATE
        # get CheckCode.aspx
        req = urllib2.Request(self.code_url,headers = self.headers)
        a = self.opener.open(req).read()
        import time
        import md5
        time_md5 = md5.md5(str(time.time())).hexdigest()
        pic_name = time_md5 + ".gif"
        filename = 'static/pic/' + pic_name
        fi = file(filename,'wb')
        fi.write(a)
        fi.close()
        process_image(filename)
        return __VIEWSTATE, time_md5


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
        post_data = urllib.urlencode(data)
        req = urllib2.Request(url=self.login_url,data=post_data,headers=self.headers)
        ret = self.opener.open(req).read().decode("gbk").encode("utf-8")
        return ret



    def get_html(self, search_item):
        """
        仅用来抓取目的网页
        """
        url = self.base_url + search_item + ".aspx?xh=" + self.xh
        req = urllib2.Request(url = url, headers = self.headers)
        target_html = self.opener.open(req).read().decode('gbk')
        #print  target_html.encode("utf-8")
        return target_html


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


def get_json(table):
    import json

    score_re = re.compile('<td>.*</td><td>.</td><td>.*</td><td>(.*)</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>(.*)</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td>')
    result = score_re.findall(str(table).decode('utf-8'))
    dic = {}
    for i in result:
        (key,value) = i
        dic[key] = value
    json_object = json.dumps(dic)
    return json_object

#    def get_json(self,func):
#        self.func = func
#        res = self.get_table()
#        dic = {}
#        dic['kebiao'] = res
#        import json
#        json_obj = json.dumps(dic)
#        return json_obj
#



#xh = raw_input("xh")
#pw = raw_input("pw")
