#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import web
from web import form

import random
import re
import urllib
import urllib2
import cookielib
from BeautifulSoup import BeautifulSoup
import gpa

urls = (
        '/', 'index',
        '/contact.html','contact',
        '/notice.html','notice'
        )


render = web.template.render('template/') # your templates

#urls
login_url = 'http://210.44.176.132/default3.aspx'

#get url
def get_url(_xh,funl):
    url='http://210.44.176.132/' + funl +'.aspx?xh=' + _xh 
    print url
    return url


#timetable_url = 'http://210.44.176.132/xskbcx.aspx?xh=%s'% _xh 


def login(login_url,_xh,_pw):
    if login_url: 
        html1 = urllib.urlopen(login_url).read()
    else:
        print("login url is error")

    a = re.compile('<input type="hidden" name="__VIEWSTATE" value="(.*)" />')
    try:
        VIEWSTATE = a.findall(html1)[0]
    except:
        print("can not get viewstate")
    #cookie
    student_cookie = cookielib.CookieJar()
    #login
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(student_cookie))
    data = '__VIEWSTATE='+VIEWSTATE+'&TextBox1='+_xh+'&TextBox2='+_pw+'&ddl_js=%D1%A7%C9%FA&Button1=+%B5%C7+%C2%BC+'
    try:
    	login_request = urllib2.Request(login_url, data)
    	opener.open(login_request, data)
    	# print opener
    	return opener
    except:
    	# out = ["<div class='alert alert-error'><h4><center><strong>Login ERROR!!!</strong><center></h4></div>",]
    	return "error"


def get_score(score_url, opener,tname):
    #get result page
    if opener == "error":
    	out = ["<div class='alert alert-error'><h4><center><strong>Login ERROR!!!</strong><center></h4></div>",]
    	return out
    else:
	    score_html = opener.open(score_url).read()
	    if score_html:
	        #print score_html
	        print('html is ok')
	    #get table
	    soup = BeautifulSoup(score_html, fromEncoding='gbk')
	    table = soup.find("table", {"id": tname}) #table is class
	    if table:
	        out = table.contents
	    else:
	        out = ["<div class='alert alert-error'><h4><center><strong>System is Busy!!!</strong><center></h4></div>",]
	    return out


info_form = form.Form(
        form.Textbox("number", description="学号:",class_="span3",pre="&nbsp;&nbsp;"),
        form.Password("password", description="密码:",class_="span3",pre="&nbsp;&nbsp;"),
        form.Dropdown('Type',[('1', '成绩查询'), ('2', '考试时间查询'), ('3', '课表查询'),('4', '平均学分绩点查询')],description="查询类型:",pre="&nbsp;&nbsp;"),
        validators = [
            form.Validator('输入不合理!', lambda i:int(i.number) > 9)]
        )

#成绩查询
class index:
    def GET(self):
        form = info_form()
        return render.index(form)

    def POST(self):
        form = info_form()
        if not form.validates():
            return render.index(form)
        else:
            _xh = form.d.number
            _pw = form.d.password
            t = form.d.Type

            if login(login_url,_xh,_pw):
                opener = login(login_url, _xh,_pw)
                if t == "1":
                    tname = "DataGrid1"
                    funl = "xscjcx_dq"
                elif t == "2":
                    tname = "DataGrid1"
                    funl = "xskscx"
                elif t == "3":
                    tname = "Table1"
                    funl = "xskbcx"
                elif t == "4":
                	a = gpa.calc_score(_xh)
                	table = [
                		# "<tr><td><strong>姓名</strong></td><td><strong>" + str(a["name"])+"</strong></td></tr>",
                		# "<tr><td><strong>班级</strong></td><td><strong>" + str(a["class"])+"</strong></td></tr>",
                		"<tr><td><strong>平均学分绩点</strong></td><td><strong>" + str(a["ave_score"])+"</strong></td></tr>",
                		# "<tr><td><strong>总基点</strong></td><td><strong>" + str(a["total_score"])+"</strong></td></tr>",
                		# "<tr><td><strong>总学分</strong></td><td><strong>" + str(a["totle_credits"])+"</strong></td></tr>",
                		# "<tr><td><strong>至今未通过科目</strong></td><td><strong>" + str(len(a['not_accept']))+"</strong></td></tr>",
                	]
                	error = None
                	return render.result(table,error)
                else:
                    return '<script type="text/javascript">alert("输入不合理!");top.location="/"</script>'

                score_url = get_url(_xh,funl)
                table = get_score(score_url, opener,tname)

                if table:
                    error = None
                    return render.result(table, error)
                else:
                    table = None
                    error = "can not find your index table"
                    return render.result(table, error)

#contact us
class contact:
    """contact us page"""
    def GET(self):
        return render.contact()
        
#notice 
class notice:
    def GET(self):
        return render.notice()


if __name__  == "__main__":
    app = web.application(urls, globals())

    app.run()
