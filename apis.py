#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import web
import json

from web import ctx
from web.contrib.template import render_jinja

from addons.get_CET import CET
from addons.calc_GPA import GPA
from addons.zfr import ZF, Login
from addons.data_factory import KbJson, get_score_dict
from addons import errors

render = render_jinja('templates', encoding='utf-8')

urls = (
    '$', 'api_index',
    '/score', 'api_zheng',
    '/kb', 'api_kb',
    '/cet', 'api_cet',
    '/gpa', 'api_gpa',
)

# api

def json_err(content):
    """用于生成json error内容"""
    dic = {'error': content}
    json_object = json.dumps(dic)
    return json_object

class api_index:

    def GET(self):
        return render.apis()

class api_kb:

    def GET(self):
        return 'Hello kb!'

    def POST(self):
        data = web.input()
        _xh = data.xh
        _pw = data.pw
        zheng = ZF(_xh, _pw, 'xskbcx')
        json_object = zheng.get_json('xskbcx')
        return json_object



class api_zheng:

    def GET(self):

        try:
            zf = ZF()
            time_md5 = zf.pre_login()
        except errors.ZfError, e:
            return render.serv_err(err=e.value)
        ctx.session['time_md5'] = time_md5
        # get checkcode
        dic = {'time_md5': time_md5}
        json_object = json.dumps(dic)
        return json_object

    #def __score_get_json(self, table):
    #    """
    #    成绩正则匹配为json格式
    #    """
    #    score_re = re.compile('<td>.*</td><td>.</td><td>.*</td><td>(.*)</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>(.*)</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td>')
    #    result = score_re.findall(str(table).decode('utf-8'))
    #    dic = {}
    #    for i in result:
    #        (key,value) = i
    #        dic[key] = value
    #    json_object = json.dumps(dic)
    #    return json_object

    def __kb_get_json(self, table):
        pass

    def POST(self):
        content = web.input()
        t, time_md5 = content.t, content.time_md5

        try:
            zf = Login()
            zf.login(time_md5, content)
            #__dic = {
            #        '1': zf.get_score,
            #        '2': zf.get_kaoshi,
            #        '3': zf.get_kebiao,
            #        }
            #if t not in __dic.keys():
            #    return json_err('data error')
            #return render.result(table=__dic[t]())

            if t == "1":
                _dic=get_score_dict(zf.get_score())
                json_object = json.dumps(_dic)
            elif t == "2":
                return json_err("please contact admin")
                #table = zf.get_kaoshi()
            elif t == "3":
                table = zf.get_kebiao()
                k = KbJson(table)
                json_object = k.get_json()
            else:
                return json_err("can not find your t")

            web.header('Content-Type','application/json')
            return json_object

        except errors.PageError, e:
            return json_err(e.value)


class api_cet:

    def GET(self):
        return 'cet'

    def POST(self):
        data = web.input()
        try:
            nu = data.nu
            name = data.name.encode('utf-8')
        except AttributeError:
            return json_err("can not find your post content")
        cet = CET()
        result = cet.get_last_cet_score(nu, name)
        result = json.dumps(result)
        return result


class api_gpa:

    def GET(self):
        return 'gpa'

    def POST(self):
        data = web.input()
        try:
            xh = data.xh
        except AttributeError:
            return json_err("The id is xh")
        gpa = GPA(xh)
        gpa.getscore_page()
        result = gpa.get_gpa()
        if result == -1:
            return json_err("can not find your xh")
        result = json.dumps(result)
        return result

apis = web.application(urls, locals())
