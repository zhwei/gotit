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
    '/weixin', 'WeixinInterface',
)

weixin = web.application(urls, locals())


class w_index:

    def GET(self):
        return 'ok'

def reply_text(toUser, fromUser, createTime, content):
    """返回xml文本信息"""
    text = """<xml>
<ToUserName><![CDATA[{0}]]></ToUserName>
<FromUserName><![CDATA[{1}]]></FromUserName>
<CreateTime>{2}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{3}]]></Content>
</xml>
""".format(toUser, fromUser, createTime, content)
    return text

class WeixinInterface:

    #def __init__(self):
    #    self.app_root = os.path.dirname(__file__)
    #    self.templates_root = os.path.join(self.app_root, 'templates')
    #    self.render = web.template.render(self.templates_root)

    def GET(self):
        #获取输入参数
        try:
            data = web.input(_method="GET")
            signature, timestamp = data.signature,data.timestamp
            nonce, echostr = data.nonce,data.echostr
        except AttributeError:
            return 't'
        #自己的token
        token="gotitzhangwei" #这里改写你在微信公众平台里输入的token
        #字典序排序
        li=[token, timestamp, nonce]
        li.sort()
        sha1=hashlib.sha1()
        map(sha1.update, li)
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
        MsgId=xml.find("MsgId").text
        return reply_text(fromUser,toUser,int(time.time()), u"您刚才说的是：{},id is {}".format(content, MsgId))
