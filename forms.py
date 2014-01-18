#!/usr/bin/env python
# -*- coding: utf-8 -*-

from web import form

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
