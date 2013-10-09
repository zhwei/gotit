#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# import time

import web
from urllib2 import URLError

from web.contrib.template import render_jinja

# addons
from addons import config
from addons import get_old_cet, get_book, get_gpa, get_score
from addons.get_CET import CET

from addons.autocache import memorize
from addons.forms import xh_form, cet_form, get_index_form, login_form
from addons.config import index_cache, debug_mode, zheng_alert
from addons.zf_cache import get_time_md5, cache_zf_start, zf_login, \
    find_login, just_check, get_count, get_client_num, get_enumer_num

from addons.tools import zf_result, score_result, init_redis

from addons.RedisStore import RedisStore

from urls import urls

if config.zf_accelerate:
    # 缓存正方相关
    cache_zf_start()
else:
    just_check()



# 调试模式
web.config.debug = debug_mode
app = web.application(urls, globals(),autoreload=False)
# gunicorn 部署使用
application = app.wsgifunc()


# session settings

if web.config.get('_session') is None:
    session = web.session.Session(app, RedisStore(), {'count': 0, 'logged_in':False})
    web.config._session = session
else:
    session = web.config._session

web.config.session_parameters['cookie_name'] = 'gotit_session_id'
web.config.session_parameters['cookie_domain'] = "gotit.asia"
web.config.session_parameters['timeout'] = 600, #in seconds
web.config.session_parameters['ignore_expiry'] = True
web.config.session_parameters['ignore_change_ip'] = True
web.config.session_parameters['secret_key'] = 'wqerjkhbasdfhsdakyarweqr'
web.config.session_parameters['expired_message'] = '您需要重新登录！'


# end sessions

render = render_jinja('templates', encoding='utf-8', globals={'context':session})

class old_index:
    '''
    索引页面
    '''
    def GET(self):
        return render.old_index(alert=zheng_alert)

class index:
    '''
    new  索引页面
    '''
    # @memorize(index_cache)
    def GET(self):
        return render.index()

class login:
    '''
    正方教务系统登录，成绩、课表、考试时间查询
    '''
    def GET(self):
        global allclients
        try:
            time_md5= get_time_md5()
        except URLError:
            return "can not touch zhengfang!"
        session['time_md5'] = time_md5
        form = get_index_form(time_md5)

        r = init_redis()
        checkcode = "data:image/gif;base64,"+r.hget('checkcode',time_md5)
        return render.login(alert=zheng_alert, form=form, checkcode=checkcode)

    def POST(self):
        content = web.input()

        time_md5=session['time_md5']
        session['xh']=content['xh']

        try:
            zf, ret = zf_login(content, time_md5)
        except KeyError:
            return render.key_error()

        if ret.find('欢迎您') != -1:
            pass
        elif ret.find('密码错误') != -1:
            return render.pw_error()

        elif ret.find('验证码不正确') != -1:
            return render.recg_error()
        else:
            return render.ufo_error()
        session.logged_in=True
        raise web.seeother('/succeed')

class succeed:
    """
    登录成功界面
    """
    def GET(self):

        if session['logged_in']==False:
            raise web.seeother('/login')

        try:
            xh=session['xh']
        except KeyError:
            return render.key_error()

        gpa=get_gpa(xh)

        session['name']=gpa['name']

        return render.succeed(gpa=gpa)

class logout:
    def GET(self):

        session.kill()
        raise web.seeother('/')

class zheng:
    '''
    正方教务系统登录，成绩、课表、考试时间查询
    '''
    def GET(self):
        global allclients
        time_md5= get_time_md5()
        form = get_index_form(time_md5)

        r = init_redis()
        checkcode = "data:image/gif;base64,"+r.hget('checkcode',time_md5)
        return render.zheng(alert=zheng_alert, form=form,checkcode=checkcode)

    def POST(self):

        content = web.input()
        t = content['type']
        time_md5=content['time_md5']

        try:
            zf, ret = zf_login(content)
        except KeyError:
            return render.key_error()

        if ret.find('欢迎您') != -1:
            pass
        elif ret.find('密码错误') != -1:
            return render.pw_error()

        elif ret.find('验证码不正确') != -1:
            return render.recg_error()
        else:
            return render.ufo_error()

        return zf_result(t, zf, time_md5)



class more:
    """
    查询结果页面， 用于查询更多信息
    """
    def GET(self, t):

        if session['logged_in']==False:
            raise web.seeother('/login')

        time_md5=session['time_md5']

        try:
            zf, xh, time_start = find_login(time_md5)
        except KeyError:
            return render.key_error()

        if t == '4':
            # 全部成绩
            return render.result(score_table=get_score(xh))

        elif t == '5':
            # 往年cet
            table=get_old_cet(xh)
            return render.result(cet_table=table)
        else:
            # 正方相关的查询
            return zf_result(t, zf, time_md5)


class cet:
    """
    四六级成绩查询
    """

    # @memorize(index_cache)
    def GET(self):
        form = cet_form()
        if config.baefetch:
            print form
            return render.cet_bae(form=form)
        else:
            return render.cet(form=form)

    def POST(self):
        form = cet_form()
        if not form.validates():
            return render.cet(form=form)
        else:
            zkzh = form.d.zkzh
            name = form.d.name
            name = name.encode('utf-8')
            items = ["学校", "姓名", "阅读", "写作", "综合", "准考证号",
                     "考试时间", "总分", "考试类别", "听力"]
            cet = CET()
            res = cet.get_last_cet_score(zkzh, name)
            return render.result_dic(items=items, res=res)

class cet_old:
    """
    往年cet成绩查询
    """
    def GET(self):
        form=xh_form
        title='往年四六级成绩'
        return render.normal_form(title=title, form=form)
    def POST(self):
        form = xh_form()
        title='往年四六级成绩'
        if not form.validates():
            return render.normal_form(title=title,form=form)
        else:
            xh = form.d.xh
        table=get_old_cet(xh)
        return render.result(cet_table=table)

class lib:
    '''
    图书馆相关
    '''
    def GET(self):
        form=login_form
        title='图书馆借书查询'
        return render.normal_form(title=title, form=form)
    def POST(self):
        form=login_form()
        title='图书馆借书查询'
        if not form.validates():
            return render.normal_form(title=title,form=form)
        else:
            xh, pw=form.d.xh, form.d.pw
        table=get_book(xh,pw)
        return render.old_result(title=title, just_table=table)


class contact:

    """contact us page"""
    @memorize(index_cache)
    def GET(self):
        return render.contact()


class notice:
    '''
    notice
    '''
    @memorize(index_cache)
    def GET(self):
        return render.notice()



class score:
    '''
    全部成绩
    '''
    # @memorize(index_cache)
    def GET(self):
        form = xh_form()
        return render.score(form=form)

    def POST(self):
        form = xh_form()
        if not form.validates():
            return render.score(form=form)
        else:
            xh = form.d.xh

        return score_result(xh)




class status:
    '''
    网站状态，返回相关值
    '''
    def GET(self):
        clients = get_count()
        used_client= get_client_num(name='used')
        login_client=get_client_num(name='login')
        thread_num=get_enumer_num()
        pics = len(os.listdir("static/pic"))
        return locals()



class help_gpa:
    '''
    平均学分绩点计算说明页面
    '''
    @memorize(index_cache)
    def GET(self):
        return render.help_gpa()



class comment:
    '''
    评论页面, 使用多说评论
    '''

    def GET(self):
        return render.comment()

class what:
    '''
    功能征集页面, 使用多说评论
    '''

    def GET(self):
        return render.what_you_need()




class donate:
    '''
    赞助页面
    '''
    def GET(self):
        import json
        file_name=os.path.join(config.pwd, 'data/sponsor.json')
        with open(file_name) as s_file:
            json_obj=json.load(s_file)
        return render.donate(sponsor=json_obj)



class ttest:
    '''
    阿里妈妈认证
    '''
    def GET(self):
        return render.root()
