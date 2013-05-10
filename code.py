#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import web
import json
from web import form
from web.contrib.template import render_jinja

#addons
from addons.calc_GPA import GPA
from addons.get_CET import CET
from addons.zf import ZF
from addons.get_all_score import ALL_SCORE
from addons.autocache import memorize
from addons import config
from addons.config import index_cache, debug_mode
web.config.debug = debug_mode

urls = (
        '/', 'index',
        '/zheng', 'zheng',
        '/score', 'score',
        '/cet', 'cet',
        '/contact.html','contact',
        '/notice.html','notice', 
        '/root.txt', 'ttest', 
        '/api/kb','api_kb',
        '/api/cet','api_cet',
        '/api/gpa','api_gpa',
        '/help/gpa.html','help_gpa',
        '/comment.html','comment',
        )

#render = web.template.render('./template/') # your templates
render = render_jinja('templates', encoding='utf-8')
all_client = {}

#forms
#def get_form(viewstate):
#    info_form = form.Form(
#        form.Textbox("number", description="学号:",class_="span3",pre="&nbsp;&nbsp;"),
#        form.Password("password", description="密码:",class_="span3",pre="&nbsp;&nbsp;"),
#        form.Textbox("verify", description="验证码:",class_="span3",pre="&nbsp;&nbsp;"),
#        form.Dropdown('Type',[('3', '本学期课表查询'),('1', '本学期成绩查询'), ('2', '考试时间查询'),('4', '平均学分绩点查询')],description="查询类型:",pre="&nbsp;&nbsp;"),
#        form.Hidden('viewstate',value=viewstate),
#        validators = [
#            form.Validator('输入不合理!', lambda i:int(i.number) > 9)]
#        )
#    return info_form()

cet_form = form.Form(
        form.Textbox("zkzh", description="准考证号:",class_="span3",pre="&nbsp;&nbsp;"),
        form.Textbox("name", description="姓名:",class_="span3",pre="&nbsp;&nbsp;"),
        validators = [
            form.Validator('输入不合理!', lambda i:int(i.zkzh) != 15)]
        )
xh_form = form.Form(
        form.Textbox("xh",description="学号:",class_="span3",pre="&nbsp;&nbsp;")
        )

def get_index_form(viewstate, pic_name):
    index_form = '\
            <table><tr><th><label for="xh">学号:</label></th><td>&nbsp;&nbsp;<input type="text" id="xh" name="xh" class="span3"/></td></tr>\
            <tr><th><label for="pw">密码:</label></th><td>&nbsp;&nbsp;<input type="password" id="pw" name="pw" class="span3"/></td></tr>\
            <tr><th><label for="number">验证码:</label></th>\
                <td>&nbsp;&nbsp;<input type="text" id="verify" name="verify"/>&nbsp;<img src="/static/pic/'+ pic_name +'" alt="" height="35" width="92"/></td>\
                <td></td>\
                </tr>\
            <tr><th><tr><th><label for="Type">查询类型:</label></th><td>&nbsp;&nbsp;<select id="type" name="type">\
                <option value="1">成绩查询</option>\
                <option value="2">考试时间查询</option>\
                <option value="3">课表查询</option></select></td></tr>\
            <input type="hidden" value="'+ viewstate +'" name="viewstate"/>'
    return index_form

#成绩查询
class zheng:
    def GET(self):
        zf = ZF()
        viewstate, pic_name = zf.pre_login()
        all_client[viewstate] = zf
        form = get_index_form(viewstate, pic_name)
        return render.index(form=form ,viewstate=viewstate, pic_name=pic_name)

    def POST(self):
        content = web.input()
        self.xh = content['xh']
        self.pw = content['pw']
        t = content['type']
        yanzhengma = content['verify']
        viewstate = content['viewstate']

        try:
            zf = all_client.pop(viewstate)
        except KeyError:
            return '<script type="text/javascript">alert("刷新首页再次查询!");top.location="/"</script>'
        zf.set_user_info(self.xh, self.pw)
        ret = zf.login(yanzhengma, viewstate)

        if ret.find('欢迎您') != -1:
            pass
        elif ret.find('密码错误') != -1:
            return '<script type="text/javascript">alert("密码错误!");top.location="/"</script>'

        elif ret.find('验证码不正确') != -1:
            return '<script type="text/javascript">alert("验证码错误!");top.location="/"</script>'
        else:
            return '<script type="text/javascript">alert("未知错误,请联系管理员!");top.location="/"</script>'


        if t == "1":
            table = zf.get_score()
        elif t == "2":
            table = zf.get_kaoshi()
        elif t == "3":
            table = zf.get_kebiao()
        else:
            return '<script type="text/javascript">alert("输入不合理!");top.location="/"</script>'
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
            gpa = GPA(xh)
            jidian = gpa.get_gpa()["ave_score"]

            if table:
                return render.result(table=table, jidian=jidian)
            else:
                table = None
                error = "can not get your score"
                return render.result(table=table,error=error)

class help_gpa:
    #@memorize(index_cache)
    def GET(self):
        return render.help_gpa()

class comment:
    def GET(self):
        return render.comment()
        

class index:
    @memorize(index_cache)
    def GET(self):
        return render.aaa()

application = web.application(urls, globals(),autoreload=False).wsgifunc()
