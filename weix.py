#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import hashlib
import lxml
import time
import os
import urllib2,json
from lxml import etree
import web
from web import ctx
from web.contrib.template import render_jinja



from addons import mongo2s

render = render_jinja('templates', encoding='utf-8')


# init mongoDB
db = mongo2s.init_mongo()

urls = (
    '$weixin', 'WeixinInterface',
)

weixin = web.application(urls, locals())


class w_index:

    def GET(self):
        return 'ok'

class WeixinInterface:

    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
        #自己的token
        token="gotitzhangwei" #这里改写你在微信公众平台里输入的token
        #字典序排序
        li=[token,timestamp,nonce]
        li.sort()
        sha1=hashlib.sha1()
        map(sha1.update,list)
        hashcode=sha1.hexdigest()
        #sha1加密算法        

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr

    def POST(self):        
            str_xml = web.data() #获得post来的数据
            xml = etree.fromstring(str_xml)#进行XML解析
            content=xml.find("Content").text#获得用户所输入的内容
            msgType=xml.find("MsgType").text
            fromUser=xml.find("FromUserName").text
            toUser=xml.find("ToUserName").text
            return self.render.reply_text(fromUser,toUser,int(time.time()), u"我现在还在开发中，还没有什么功能，您刚才说的是："+content)
