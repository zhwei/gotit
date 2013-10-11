#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
from zf import ZF

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
