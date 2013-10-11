#!/usr/bin/env python
#coding=utf-8
import cookielib
import urllib
import urllib2
import re
from BeautifulSoup import BeautifulSoup
#import os
import web
urls = (
    '/',"INDEX",
)
app = web.application(urls,globals())
All_client = {}

class ZF():
    base_url = "http://210.44.176.132/"
    login_url = base_url + "Default2.aspx"
    code_url = base_url + 'CheckCode.aspx?'
    headers = {'Referer':base_url,'Host':base_url[7:21],'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",'Connection':'Keep-Alive'}

    def __init__(self):
        cookiess = cookielib.LWPCookieJar()
        self.openerq =urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiess))
        urllib2.install_opener(self.openerq)

    def set_user_info(self,xh,pw):
        self.xh = xh
        self.pw = pw

        
    def _get_score_link(self,html):
        patten = re.compile('<li><a href="(.*?)" target=\'zhuti\' onclick=".*?">成绩查询</a></li>')
        real_link = self.base_url + patten.findall(html)[0]
        return real_link

    def _get_viewstat_posturl(self,score_link):
        req = urllib2.Request(score_link,headers=self.headers)
        ret = self.openerq.open(req).read()
        com = re.compile('<input type="hidden" name="__VIEWSTATE" value="(.*?)"')
        all = com.findall(ret)
        __VIEWSTATE =  all[0]
        com2 = re.compile('<form name="Form1" method="post" action="(.*?)" id="Form1">')
        all = com2.findall(ret)
        print all
       # post_url =  all[0]
        post_url = 'xscjcx_dq.aspx?xh=1011051022&xm=%C2%ED%CE%B0%CE%B0&gnmkdm=N121501'
        post_url = self.base_url + post_url
        return post_url,__VIEWSTATE
    def get_all_socre(self):
        html = self.login()
        score_link = self._get_score_link(html)
        post_url,__VIEWSTATE = self._get_viewstat_posturl(score_link)
        post_url = 'http://210.44.176.132/xscjcx_dq.aspx?xh=1011051022&xm=%C2%ED%CE%B0%CE%B0&gnmkdm=N121605'
        data = {
            '__EVENTTARGET':'ddlxn',
            '__EVENTARGUMENT':'',
            '__VIEWSTATE':__VIEWSTATE,
            'ddlxn':'全部',
            'ddlxq':'2',
        }
        data = urllib.urlencode(data)
        req = urllib2.Request(url=post_url,data=data,headers=self.headers)
        ret = self.openerq.open(req).read()

        post_url = 'http://210.44.176.132/xscjcx_dq.aspx?xh=1011051022&xm=%C2%ED%CE%B0%CE%B0&gnmkdm=N121605'
        data = {
            '__EVENTTARGET':'ddlxq',
            '__EVENTARGUMENT':'',
            '__VIEWSTATE':__VIEWSTATE,
            'ddlxn':'全部',
            'ddlxq':'全部',
        }
        data = urllib.urlencode(data)
        req = urllib2.Request(url=post_url,data=data,headers=self.headers)
        ret = self.openerq.open(req).read()

        post_url = 'http://210.44.176.132/xscjcx_dq.aspx?xh=1011051022&xm=%C2%ED%CE%B0%CE%B0&gnmkdm=N121605'
        data = {
            '__EVENTTARGET':'',
            '__EVENTARGUMENT':'',
            '__VIEWSTATE':__VIEWSTATE,
            'ddlxn':'全部',
            'ddlxq':'全部',
            'btnCx':' 查  询 ',
        }
        data = urllib.urlencode(data)
        req = urllib2.Request(url=post_url,data=data,headers=self.headers)
        ret = self.openerq.open(req).read()
        print >> file('c.html','w'),ret

    def pre_login(self):
        #get __VIEWSTATE
        req = urllib2.Request(self.base_url,headers=self.headers)
        ret = self.openerq.open(req)
        page = ret.read()
        com = re.compile(r'name="__VIEWSTATE" value="(.*?)"')
        all = com.findall(page)
        __VIEWSTATE =  all[0]
        self.VIEWSTATE = __VIEWSTATE
        print __VIEWSTATE
        # get CheckCode.aspx
        req = urllib2.Request(self.code_url,headers = self.headers)
        a = self.openerq.open(req).read()
        filename = 'static/pic.gif'
        fi = file(filename,'wb')
        fi.write(a)
        fi.close()
        return __VIEWSTATE
#        yanzhengma = raw_input("验证码:").decode("utf-8").encode("gb2312")
#        from sec_code.recg import verify
#        yanzhengma = verify(filename)
        #os.remove(filename)
    def login(self,yanzhengma,VIEWSTATE):
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
        print data
        post_data = urllib.urlencode(data)
        headers = {'Referer':'http://210.44.176.132/Default2.aspx','Host':'210.44.176.132','Origin':'http://210.44.176.132','User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",'Connection':'keep-alive','Expires':'-1'}
        req = urllib2.Request(url=self.login_url,data=post_data,headers=headers)
        ret = self.openerq.open(req).read().decode("gbk").encode("utf-8")
        print ret
        return ret

    def __get_url(self):
        func_url = self.base_url + self.func + ".aspx?xh=" + self.xh
        return func_url


    def get_table(self):
        #url = self.__get_url()
        url = 'http://210.44.176.132/xskbcx.aspx?xh=1011051022&xm=%C2%ED%CE%B0%CE%B0&gnmkdm=N121603'
        req = urllib2.Request(url=url,headers=self.headers)
        target_html = self.openerq.open(req)
        return target_html

        soup = BeautifulSoup(target_html, fromEncoding='gbk')
        if self.func == "xskbcx":
            table_name = "Table1"
        else:
            table_name = "DataGrid1"
        table = soup.find("table", {"id": table_name}) #table is class
        result = table.contents
        #print result
        return result

    def check_login(self,ret):
        if ret.find('欢迎您') != -1:
            return 0
        elif ret.find('密码错误') != -1:
            return 1
        elif ret.find('验证码不正确') != -1:
            return 2
        else:
            return -1
    

class INDEX():
    def GET(self,args = None):
        z = ZF()
        VIEWSTATE = z.pre_login()
        All_client[VIEWSTATE] = z
        data = '<html><form name="myform" action="." method="POST"><input type="hidden" name="VIEWSTATE" value = "%s"><input type="text" name="yanzhengma"><input type="submit" name="submit" id="submit" value="Submit"><img src="/static/pic.gif" /></html>'%VIEWSTATE
        return data
    
    def POST(self,args = None):
        input = web.input()
        yanzhengma = input['yanzhengma']
        VIEWSTATE = input['VIEWSTATE']
        self.xh = ""
        self.pw = ""
        z = All_client.pop(VIEWSTATE)
        z.set_user_info(self.xh,self.pw)
        ret = z.login(yanzhengma,VIEWSTATE)
        table = z.get_table()
        return table

if __name__=='__main__':
    app.run()

#xh = raw_input("xh")
#pw = raw_input("pw")
#z.main()
#z.get_table()
