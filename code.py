#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import web
from web import form
web.config.debug = False

import random
import re
import urllib
import urllib2
import cookielib
from BeautifulSoup import BeautifulSoup

#self
from calc_GPA import GPA
from get_CET import CET
from zheng import ZHENG


urls = (
        '/', 'index',
        '/cet', 'cet',
        '/contact.html','contact',
        '/notice.html','notice', 
        '/orca.txt', 'orca', 
        '/root.txt', 'ttest', 
        )


render = web.template.render('template/') # your templates

#forms
info_form = form.Form(
        form.Textbox("number", description="学号:",class_="span3",pre="&nbsp;&nbsp;"),
        form.Password("password", description="密码:",class_="span3",pre="&nbsp;&nbsp;"),
        form.Dropdown('Type',[('1', '成绩查询'), ('2', '考试时间查询'), ('3', '课表查询'),('4', '平均学分绩点查询')],description="查询类型:",pre="&nbsp;&nbsp;"),
        validators = [
            form.Validator('输入不合理!', lambda i:int(i.number) > 9)]
        )
cet_form = form.Form(
        form.Textbox("zkzh", description="准考证号:",class_="span3",pre="&nbsp;&nbsp;"),
        form.Textbox("name", description="姓名:",class_="span3",pre="&nbsp;&nbsp;"),
        validators = [
            form.Validator('输入不合理!', lambda i:int(i.zkzh) != 15)]
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
            
            if t == "1":
                func = "xscjcx_dq"
            elif t == "2":
                func = "xskscx"
            elif t == "3":
                func = "xskbcx"
            elif t == "4":
                gpa = GPA(_xh)
                a = gpa.get_gpa()
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

            zheng = ZHENG(_xh,_pw,func)
            table = zheng.get_table()

            if table:
                error = None
                return render.result(table, error)
            else:
                table = None
                error = "can not find your index table"
                return render.result(table, error)

#cet
class cet:
    def GET(self):
        form = cet_form()
        return render.cet(form)
    def POST(self):
        form = cet_form()
        if not form.validates():
            return render.cet(form)
        else:
            zkzh = form.d.zkzh
            name = form.d.name
            name = name.encode('utf-8')
            items = ["学校","姓名","阅读","写作","综合", "准考证号", "考试时间", "总分", "考试类别", "听力"]
            cet = CET()
            result = cet.get_last_cet_score(zkzh,name)
            return render.result_dic(items,result)

#contact us
class contact:
    """contact us page"""
    def GET(self):
        return render.contact()
        
#notice 
class notice:
    def GET(self):
        return render.notice()

#orca accelerating
class orca:
    def GET(self):
        return render.orca()
#taobao accelerating
class ttest:
    def GET(self):
        return render.root()

if __name__  == "__main__":
    app = web.application(urls, globals())
    app.run()
