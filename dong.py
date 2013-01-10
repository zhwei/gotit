#!/usr/bin/python2.7
#encoding:utf-8
import random
import re
import urllib
import urllib2
import cookielib
from BeautifulSoup import BeautifulSoup
#test
import types
 
#info
_xh = '1111051046'
_pw = 'zhejiushimima@JW'
#urls
url  =  "http://210.44.176.133"
u  =  urllib2.urlopen(url)
end  =  u.geturl()
end1 = end[:-13]
print end1
login_url = end1 + 'default3.aspx'
index_url = end1 + 'xs_main.aspx?xh=' + _xh
score_url= end1 + 'xscjcx_dq.aspx?xh=' + _xh 
timetable_url = end1 + 'xskbcx.aspx?xh=%s'% _xh 

#get VIEMSTATE
def get_view(url):
	html = urllib.urlopen(url).read()
	a = re.compile('<input type="hidden" name="__VIEWSTATE" value="(.*)" />')
	VIEWSTATE = a.findall(html)[0]
	return VIEWSTATE





#cookie
student_cookie = cookielib.CookieJar()
#login
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(student_cookie))

VIEWSTATE=get_view(login_url)
print VIEWSTATE

data = '__VIEWSTATE='+VIEWSTATE+'&TextBox1='+_xh+'&TextBox2='+_pw+'&ddl_js=%D1%A7%C9%FA&Button1=+%B5%C7+%C2%BC+'

login_request = urllib2.Request(login_url, data)
opener.open(login_request, data)

print('Login OK')
try:
	xn='2011-2012'
	xq='1'
	data = '__VIEWSTATE='+VIEWSTATE+'&btnCx=+%e6%9f%a5++%e8%af%a2+'+'&ddlxn='+xn+'&ddlxq='+xq
	year_request=urllib2.Request(score_url,data)
	opener.open(year_request,data)
	print "read ok"
except:
	print "read error"

#get result page
score_html = opener.open(score_url).read()

#print(score_html)
if score_html:
    print('html is ok')
#get table
soup = BeautifulSoup(score_html, fromEncoding='gbk')
table = soup.find("table", {"id": "DataGrid1"}) #table is class
print(table.contents)

#tr = table.tr.contents[2].contents
#for tr in table:
#    print(tr)
