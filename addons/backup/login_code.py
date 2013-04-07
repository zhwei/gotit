#!/usr/bin/env python
#coding=utf-8
import cookielib
import urllib
import urllib2
import re
import os
cookies = cookielib.LWPCookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))
urllib2.install_opener(opener)


headers = {
        'Referer':'http://210.44.176.132/', 
        'Host':'210.44.176.132',
        'User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",
        'Connection':'Keep-Alive'
        }
def fetch(uri):
    req = urllib2.Request(uri,headers=headers)
    return opener.open(req)

def dump():
    for cookie in cookies:
        print cookie.name, cookie.value
        return cookie.value

uri = 'http://210.44.176.132/'
res = fetch(uri)
redirected = res.geturl()
#print redirected
#print res.info()

es = res.read()
com = re.compile(r'name="__VIEWSTATE" value="(.*?)"')
all = com.findall(es)
__VIEWSTATE =  all[0]
print "__VIEWSTATE",__VIEWSTATE
#cookie = dump()
#print "Cookie",cookie

headers = {'Referer':'http://210.44.176.132/','Host':'210.44.176.132','User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",'Connection':'Keep-Alive'}

req = urllib2.Request('http://210.44.176.132/CheckCode.aspx',headers = headers)

#req.add_header(headers)

a = opener.open(req).read()
file('a.gif','w').write(a)
from sec_code.recg import verify
yanzhengma = verify('a.gif')
#os.system('eog a.gif&')

print "________________________________"
print yanzhengma
#yanzhengma = raw_input("验证码：")
post_url = "http://210.44.176.132/Default2.aspx"
data = {
        'Button1':'',
        'RadioButtonList1':"学生",
        "TextBox1":'1111051046',
        'TextBox2':'zhejiushimima@JW',
        'TextBox3':yanzhengma,
        '__VIEWSTATE':__VIEWSTATE,
        'lbLanguage':'',
        }
post_data = urllib.urlencode(data)
headers = {'Referer':'http://210.44.176.132/Default2.aspx','Host':'210.44.176.132','User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:18.0) Gecko/20100101 Firefox/18.0",'Connection':'keep-alive'}

req = urllib2.Request(url=post_url,data=post_data,headers=headers)

a = opener.open(req)
print a.geturl()
#print a.info()
print a.read().decode('gbk')
#file('a.html','w').write(a.read())
