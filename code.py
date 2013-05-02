#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#import os
#import sys
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import web
import json
from web import form
web.config.debug = True
from web.contrib.template import render_jinja

#addons
from addons.calc_GPA import GPA
from addons.get_CET import CET
from addons.zf import ZF
from addons.get_all_score import ALL_SCORE
from addons.autocache import memorize
from addons import config
from addons.config import index_cache


urls = (
        '/', 'index',
        '/score', 'score',
        '/cet', 'cet',
        '/contact.html','contact',
        '/notice.html','notice', 
        '/root.txt', 'ttest', 
#.        '/api/score','api_score',
        '/api/kb','api_kb',
        '/api/cet','api_cet',
        '/api/gpa','api_gpa',
        )

#render = web.template.render('./template/') # your templates
render = render_jinja('templates', encoding='utf-8')

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
    #@memorize(index_cache)
    def GET(self):
        form = info_form()
        zf = ZF()
        cookie = zf.get()
        return render.index(form=form, cookie=cookie)

    def POST(self):
        form = info_form()
        if not form.validates():
            return render.index(form=form)
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
                result = a["ave_score"]
                #table = [
                #    "<tr><td><strong>平均学分绩点</strong></td><td><strong>" + str(a["ave_score"]).encode('utf-8')+"</strong></td></tr>",
                #]
                #error = None
                return render.result_gpa(gpa=result)
            else:
                return '<script type="text/javascript">alert("输入不合理!");top.location="/"</script>'

            zheng = ZF(_xh,_pw,func)
            zheng.main()
            table = zheng.get_table()

            if table:
                error = None
                return render.result(table=table, error=error)
            else:
                table = None
                error = "can not find your index table"
                return render.result(table=table, error=error)

#cet
class cet:
    @memorize(index_cache)
    def GET(self):
        form = cet_form()
        if config.baefetch:
            return render.cet_bae(form=form)
        else:
            return render.cet(form=form)
        #return render.cet_raise()
    def POST(self):
        form = cet_form()
        if not form.validates():
            return render.cet(form=form)
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
            return render.result_dic(items=items,res=res)

#api
class api_kb:
    def GET(self):
        return 'Hello kb!'
    def POST(self):
        data=web.input()
        _xh=data.xh
        _pw=data.pw
        zheng = ZF(_xh,_pw,'xskbcx')
        json_object = zheng.get_json('xskbcx')
        return json_object

class api_score:
    def GET(self):
        return 'Hello World!'
    def POST(self):
        data=web.input()
        _xh=data.xh
        _pw=data.pw
        zheng = ZF(_xh,_pw,'xscjcx_dq')
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
    @memorize(index_cache)
    def GET(self):
        return render.contact()
        
#notice 
class notice:
    @memorize(index_cache)
    def GET(self):
        return render.notice()

#taobao accelerating
class ttest:
    def GET(self):
        return render.root()

#get all score
class score:
    @memorize(index_cache)
    def GET(self):
        form = xh_form()
        return render.score(form=form)

    def POST(self):
        form = xh_form()
        if not form.validates():
            return render.score(form=form)
        else:
            xh = form.d.xh
            a = ALL_SCORE()
            table = a.get_all_score(xh)

            if table:
                error = None
                return render.result(table=table,error=error)
            else:
                table = None
                error = "can not get your score"
                return render.result(table=table,error=error)
        

application = web.application(urls, globals(),autoreload=False).wsgifunc()
#if __name__  == "__main__":
#    app = web.application(urls, globals(),autoreload=False)
#    app.run()
