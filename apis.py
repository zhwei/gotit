#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import web
import json

from web.contrib.template import render_jinja

from addons.calc_GPA import GPA
from addons.get_CET import CET
from addons.zf import ZF
from addons.kb_json import KBJSON

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


from addons.tools import init_redis
from addons.zf_cache import get_time_md5, zf_login

class api_zheng:

    def GET(self):

        time_md5=get_time_md5()
        r = init_redis()
        checkcode = "data:image/gif;base64,"+r.hget('checkcode',time_md5)
        dic = {'time_md5': time_md5, 'checkcode':checkcode}
        json_object = json.dumps(dic)
        return json_object


    def __score_get_json(self, table):
        """
        成绩正则匹配为json格式
        """
        score_re = re.compile('<td>.*</td><td>.</td><td>.*</td><td>(.*)</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>(.*)</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td><td>.*</td>')
        result = score_re.findall(str(table).decode('utf-8'))
        dic = {}
        for i in result:
            (key,value) = i
            dic[key] = value
        json_object = json.dumps(dic)
        return json_object

    def __kb_get_json(self, table):
        pass

    def POST(self):
        data = web.input()

        self.xh, self.pw = data.xh, data.pw
        t, time_md5 = data.t, data.time_md5

        try:

            zf, ret = zf_login(data, time_md5)
            #value = all_client.pop(time_md5)
            #zf, viewstate = value

        except KeyError:
            return json_err("can not find target time_md5")


        if ret.find('欢迎您') != -1:
            pass
        elif ret.find('密码错误') != -1:
            return json_err("password wrong")
        elif ret.find('验证码不正确') != -1:
            return json_err("verify code wrong")
        else:
            return json_err("server is sleeping ...")

        if t == "1":
            table = zf.get_score()
            json_object = self.__score_get_json(table)
        elif t == "2":
            return json_err("please contact admin")
            #table = zf.get_kaoshi()
        elif t == "3":
            #return json_err("please contact admin")
            table = zf.get_kebiao()
            k = KBJSON(table)
            json_object = k.get_json()
        else:
            return json_err("can not find your t")

        if json_object:
            return json_object
        else:
            return json_err("can not find your contents")


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
