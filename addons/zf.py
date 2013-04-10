#!/usr/bin/env python
#coding=utf-8
import cookielib
import urllib
import urllib2
import re
from BeautifulSoup import BeautifulSoup
import config
#import os
from autocache import memorize

@memorize(300)
def get_base_url():
    target = urllib2.urlopen(config.zf_url)
    with_random_url = target.geturl()
    base_url = with_random_url[:-13]
    return base_url


class ZF():
    if config.random:
        base_url = get_base_url()
    else:
        base_url = config.zf_url
    login_url = base_url + "Default2.aspx"
    code_url = base_url + 'CheckCode.aspx'
    headers = {'Referer':base_url,'Host':base_url[7:21],'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",'Connection':'Keep-Alive'}

    def __init__(self,xh,pw,func):
        self.xh = xh
        self.pw = pw
        self.func = func
        cookies = cookielib.LWPCookieJar()
        self.opener =urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
        urllib2.install_opener(self.opener)

    def login(self):
        #get __VIEWSTATE
        req = urllib2.Request(self.base_url,headers=self.headers)
        ret = self.opener.open(req)
        page = ret.read()
        com = re.compile(r'name="__VIEWSTATE" value="(.*?)"')
        all = com.findall(page)
        __VIEWSTATE =  all[0]
        # get CheckCode.aspx
        req = urllib2.Request(self.code_url,headers = self.headers)
        a = self.opener.open(req).read()
        filename = 'pic/'+str(self.xh) + '.gif'
        fi = file(filename,'wb')
        fi.write(a)
        fi.close()
        from sec_code.recg import verify
        yanzhengma = verify(filename)
        #os.remove(filename)

        data = {
            'Button1':'',
            'RadioButtonList1':"学生",
            "TextBox1":self.xh,
            'TextBox2':self.pw,
            'TextBox3':yanzhengma,
            '__VIEWSTATE':__VIEWSTATE,
            'lbLanguage':'',
        }
        post_data = urllib.urlencode(data)
        #headers = {'Referer':'http://210.44.176.132/Default2.aspx','Host':'210.44.176.132','User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",'Connection':'keep-alive'}
        req = urllib2.Request(url=self.login_url,data=post_data,headers=self.headers)
        ret = self.opener.open(req).read().decode("gbk").encode("utf-8")
        return ret

    def __get_url(self):
        func_url = self.base_url + self.func + ".aspx?xh=" + self.xh
        return func_url


    def get_table(self):
        url = self.__get_url()
        req = urllib2.Request(url=url,headers=self.headers)
        target_html = self.opener.open(req)

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
    
    def main(self):
        for i in range(10):
            ret =self.login()
            status = self.check_login(ret)
            if status == 0:
                break
            elif status == 1:
                return 'pwd'
            elif status == 2:
                continue
            elif status == -1:
                return 'ufo'



#xh = raw_input("xh")
#pw = raw_input("pw")
#z = ZF(xh,pw,'xscjcx_dq')
#z.main()
#z.get_table()
