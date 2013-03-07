#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import os
#import sys

#abspath = os.path.dirname(__file__)
#sys.path.append(abspath)
#os.chdir(abspath)

import web
import json
from web import form
web.config.debug = True

#addons
from addons.calc_GPA import GPA
from addons.get_CET import CET
from addons.zheng import ZHENG
from addons.get_all_score import ALL_SCORE


urls = (
        '/', 'index',
        '/score', 'score',
        '/cet', 'cet',
        '/contact.html','contact',
        '/notice.html','notice', 
        '/root.txt', 'ttest', 
        '/api/score','api_score',
        '/api/cet','api_cet',
        '/api/gpa','api_gpa',
        )

render = web.template.render('./template/') # your templates
#render = web.template.render(os.path.abspath(os.path.dirname(__file__)) + '/template/')

#forms
info_form = form.Form(
        form.Textbox("number", description="学号:",class_="span3",pre="&nbsp;&nbsp;"),
        form.Password("password", description="密码:",class_="span3",pre="&nbsp;&nbsp;"),
        form.Dropdown('Type',[('3', '本学期课表查询'),('1', '本学期成绩查询'), ('2', '考试时间查询'),('4', '平均学分绩点查询')],description="查询类型:",pre="&nbsp;&nbsp;"),
        validators = [
            form.Validator('输入不合理!', lambda i:int(i.number) > 9)]
        )
cet_form = form.Form(
        form.Textbox("zkzh", description="准考证号:",class_="span3",pre="&nbsp;&nbsp;"),
        form.Textbox("name", description="姓名:",class_="span3",pre="&nbsp;&nbsp;"),
        validators = [
            form.Validator('输入不合理!', lambda i:int(i.zkzh) != 15)]
        )
xh_form = form.Form(
        form.Textbox("xh",description="学号:",class_="span3",pre="&nbsp;&nbsp;")
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
        #return render.cet_raise()
    def POST(self):
        form = cet_form()
        if not form.validates():
            return render.cet(form)
        else:
            zkzh = form.d.zkzh
            name = form.d.name
            name = name.encode('utf-8')
            items = ["学校","姓名","阅读","写作","综合", "准考证号", "考试时间","总分","考试类别","听力" ]
            cet = CET()
            res = cet.get_last_cet_score(zkzh,name)
            #s = ""
            #for i in res.keys():
            #    s = "%s%s\n%s\n"%(s,i,res[i])
            #return s
            return render.result_list(items,res)

#api
class api_score:
    def GET(self):
        return 'Hello World!'
    def POST(self):
        data=web.input()
        _xh=data.xh
        _pw=data.pw
        zheng = ZHENG(_xh,_pw,'xscjcx_dq')
        json_object = zheng.get_json()
        return json_object
class api_cet:
    def GET(self):
        return 'cet'
    def POST(self):
        data=web.input()
        nu = data.nu
        name=data.name.encode('utf-8')
        cet = CET()
        result = cet.get_last_cet_score(nu,name)
        result = json.dumps(result)
        return result
class api_gpa:
    def GET(self):
        return 'gpa'
    def POST(self):
        data = web.input()
        xh = data.xh
        gpa = GPA(xh)
        result = gpa.get_gpa()
        result = json.dumps(result)
        return result

#contact us
class contact:
    """contact us page"""
    def GET(self):
        return render.contact()
        
#notice 
class notice:
    def GET(self):
        return render.notice()

#taobao accelerating
class ttest:
    def GET(self):
        return render.root()

#get all score
class score:
    def GET(self):
        form = xh_form()
        return render.score(form)

    def POST(self):
        form = xh_form()
        if not form.validates():
            return render.score(form)
        else:
            xh = form.d.xh
            a = ALL_SCORE()
            table = a.get_all_score(xh)

            if table:
                error = None
                return render.result(table,error)
            else:
                table = None
                error = "can not get your score"
                return render.result(table,error)
        

#if __name__  == "__main__":
application = web.application(urls, globals(),autoreload=False).wsgifunc()
#    app.run()
