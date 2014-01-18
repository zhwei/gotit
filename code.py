#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import web
from web import form
from web.contrib.template import render_jinja

# addons
from addons.calc_GPA import GPA
from addons.get_CET import CET
from addons.zfr import ZF, Login
from addons.get_all_score import ALL_SCORE
from addons.autocache import memorize
from addons import config
from addons.config import index_cache, debug_mode, sponsor, zheng_alert
from addons.RedisStore import RedisStore
from addons.utils import init_redis

web.config.debug = debug_mode

import apis
import manage


urls = (
    '/', 'index',
    '/zheng', 'zheng',
    '/score', 'score',
    '/cet', 'cet',
    '/api', apis.apis,
    '/manage', manage.manage,
    '/contact.html', 'contact',
    '/notice.html', 'notice',
    '/help/gpa.html', 'help_gpa',
    '/comment.html', 'comment',
    '/donate.html', 'donate',
    '/root.txt', 'ttest',
)

# main app
app = web.application(urls, globals(),autoreload=False)


# session
if web.config.get('_session') is None:
    session = web.session.Session(app, RedisStore(), {'count': 0})
    web.config._session = session
else:
    session = web.config._session

# render templates
render = render_jinja('templates', encoding='utf-8',globals={'context':session})

# forms
cet_form = form.Form(
    form.Textbox(
        "zkzh",
        description="准考证号:",
        class_="span3",
        pre="&nbsp;&nbsp;"),
    form.Textbox(
        "name",
        description="姓名:",
        class_="span3",
        pre="&nbsp;&nbsp;"),
    validators=[
        form.Validator('输入不合理!', lambda i:int(i.zkzh) != 15)]
)

xh_form = form.Form(
    form.Textbox(
        "xh",
        description="学号:",
        class_="span3",
        pre="&nbsp;&nbsp;")
)


# 首页索引页
class index:

    @memorize(index_cache)
    def GET(self):
        return render.index(alert=zheng_alert)


# 成绩查询
class zheng:

    def GET(self):

        zf = ZF()
        time_md5 = zf.pre_login()
        session.time_md5 = time_md5

        r = init_redis()
        checkcode = r.hget(time_md5, 'checkcode')

        return render.zheng(alert=zheng_alert, checkcode=checkcode)

    def POST(self):
        content = web.input()
        self.xh = content['xh']
        self.pw = content['pw']
        t = content['type']
        yanzhengma = content['verify'].decode("utf-8").encode("gb2312")
        time_md5 = session.time_md5

        zf = Login(time_md5, self.xh, self.pw, yanzhengma)
        ret = zf.text

        # deal with errors
        import re
        #regs = (
        #        "\<script language=\'javascript\' defer\>alert\(\'(.+)\'\)\;\<\/script\>",
        #        "\<script\>alert\(\'(.+)\'\)\;\<\/script\>",
        #        )
        res = ">alert\(\'(.+)\'\)\;"
        _m = re.search(res, ret)
        if _m:
            return render.alert_err(error=_m.group(1), url='/zheng')

        if t == "1":
            table = zf.get_score()
        elif t == "2":
            table = zf.get_kaoshi()
        elif t == "3":
            table = zf.get_kebiao()
        else:
            return render.input_error()

        if table:
            return render.result(table=table)
        else:
            error = "can not find your index table"
            return render.result(error=error)

# cet

class cet:

    @memorize(index_cache)
    def GET(self):
        form = cet_form()
        if config.baefetch:
            return render.cet_bae(form=form)
        else:
            return render.cet(form=form)
        # return render.cet_raise()

    def POST(self):
        form = cet_form()
        if not form.validates():
            return render.cet(form=form)
        else:
            zkzh = form.d.zkzh
            name = form.d.name
            name = name.encode('utf-8')
            items = [
                "学校",
                "姓名",
                "阅读",
                "写作",
                "综合",
                "准考证号",
                "考试时间",
                "总分",
                "考试类别",
                "听力"]
            cet = CET()
            res = cet.get_last_cet_score(zkzh, name)
            # s = ""
            # for i in res.keys():
            #    s = "%s%s\n%s\n"%(s,i,res[i])
            # return s
            return render.result_dic(items=items, res=res)

# contact us


class contact:

    """contact us page"""
    @memorize(index_cache)
    def GET(self):
        return render.contact()

# notice


class notice:

    @memorize(index_cache)
    def GET(self):
        return render.notice()


# 全部成绩
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
            gpa.getscore_page()
            # table = gpa.get_all_score()
            jidian = gpa.get_gpa()["ave_score"]

            if table:
                return render.result(table=table, jidian=jidian)
            else:
                table = None
                error = "can not get your score"
            return render.result(table=table, error=error)
            # else:
            #    return "成绩查询源出错,请稍后再试!"

# 平均学分绩点计算说明页面


class help_gpa:

    @memorize(index_cache)
    def GET(self):
        return render.help_gpa()

# 评论页面, 使用多说评论


class comment:

    def GET(self):
        return render.comment()

# 赞助页面


class donate:

    def GET(self):
        return render.donate(sponsor=sponsor)

# 阿里妈妈认证


class ttest:

    def GET(self):
        return render.root()




def session_hook():
    """ share session with sub apps
    """
    web.ctx.session = session
app.add_processor(web.loadhook(session_hook))

# for gunicorn
application = app.wsgifunc()
