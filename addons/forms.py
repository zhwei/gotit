#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


from web import form



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


def get_index_form(time_md5):
    index_form = '\
            <table><tr><th><label for="xh">学号:</label></th><td>&nbsp;&nbsp;<input type="text" id="xh" name="xh" class="span3"/></td></tr>\
            <tr><th><label for="pw">密码:</label></th><td>&nbsp;&nbsp;<input type="password" id="pw" name="pw" class="span3"/></td></tr>\
            <tr><th><label for="number">验证码:</label></th>\
            <td>&nbsp;&nbsp;<span><input type="text" id="verify" name="verify"/></span>&nbsp;<span><img style="position:absolute;" src="/static/pic/%s.gif" alt="" height="35" width="92"/></span></td>\
                <td></td>\
                </tr>\
            <tr><th><tr><th><label for="Type">查询类型:</label></th><td>&nbsp;&nbsp;<select id="type" name="type">\
                <option value="1">成绩查询</option>\
                <option value="2">考试时间查询</option>\
                <option value="3">课表查询</option></select></td></tr>\
            <input type="hidden" value="%s" name="time_md5"/></table>' % (time_md5, time_md5)
    return index_form

login_form = form.Form(
    form.Textbox(
        "xh",
        description="学号:",
        class_="span3",
        pre="&nbsp;&nbsp;"),
    form.Password(
        "pw",
        description="密码:",
        class_="span3",
        pre="&nbsp;&nbsp;"),
    validators=[
        form.Validator('输入不合理!', lambda i:int(i.xh) != 10 or int(i.xh) != 11)]
)
