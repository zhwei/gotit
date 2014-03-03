#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import datetime
import hashlib
import time
import json
from lxml import etree

import requests
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


def reply_text(toUser, fromUser, createTime, content):
    """返回xml文本信息"""
    text = """
    <xml>
    <ToUserName><![CDATA[{0}]]></ToUserName>
    <FromUserName><![CDATA[{1}]]></FromUserName>
    <CreateTime>{2}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{3}]]></Content>
    </xml>
    """.format(toUser, fromUser, createTime, content)
    return text

def process_msg(msg):

    pass

class WeixinInterface:

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

    def test_func():
        return 1

    def event_sub(xml):
        #mscontent = xml.find("Event").text
        return "欢迎注册"

    def event_unsub(xml):

        return "欢迎再来"

    def text_help(content=None):

        return """1. 你好\n2.显示帮助\n"""

    def text_repeat(content):

        return content


    event_dict={
        "subscribe":event_sub,
        "unsubscribe":event_unsub
    }

    text_dict={
        "default": text_help,
        "help": text_help,
        "repeat": text_repeat,
    }

    def POST(self):
        """响应微信
        """
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        msgType=xml.find("MsgType").text
        fromUser=xml.find("FromUserName").text
        toUser=xml.find("ToUserName").text
        # MsgId=xml.find("MsgId").text
        if msgType == "event":
            mscontent = xml.find("Event").text
            replayText = self.event_dict.get(mscontent, self.text_help)(xml)
        elif msgType == "text":
            content =xml.find("Content").text
            try:
                _r = self.text_dict[content]
                if callable(_r):
                    replayText = _r(content)
                elif _r is str:
                    replayText = _r
            except KeyError:
                replayText = self.text_dict['repeat'](content)
        return reply_text(fromUser, toUser, int(time.time()), "{}-{}".format(fromUser, replayText))
