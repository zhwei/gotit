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
from addons.zfr import ZF, Login
from addons import redis2s
from addons import errors

rds = redis2s.init_redis()

render = render_jinja('templates', encoding='utf-8')


# init mongoDB
db = mongo2s.init_mongo()

urls = (
        '/weixin', 'WeixinInterface',
        )

weixin = web.application(urls, locals())

class BaseMsg(object):

    fromUser= None
    toUser = None

    def replay_text(self, content):
        """返回xml文本信息"""
        text = """
        <xml>
        <ToUserName><![CDATA[{0}]]></ToUserName>
        <FromUserName><![CDATA[{1}]]></FromUserName>
        <CreateTime>{2}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{3}]]></Content>
        </xml>
        """.format(self.fromUser, self.toUser, int(time.time()), content)
        return text
    
    def replay_code(self, time_md5):
        text = """
        <xml>
        <ToUserName><![CDATA[{0}]]></ToUserName>
        <FromUserName><![CDATA[{1}]]></FromUserName>
        <CreateTime>{2}</CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>1</ArticleCount>
        <Articles>
            <item>
                <Title><![CDATA[验证码]]></Title> 
                <Description><![CDATA[看不清输入 r 重新获取验证码\nPS:距离远一点能看的更清楚]]></Description>
                <PicUrl><![CDATA[http://wt.gotit.asia/zheng/checkcode?r={2}&time_md5={3}]]></PicUrl>
            </item>
        </Articles>
        </xml> """.format(self.fromUser, self.toUser, int(time.time()), time_md5)
        return text

class WeixinInterface(BaseMsg):

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

    def event_unsub(xml):

        return "欢迎再来"

    def text_help(content=None):

        text = """1.成绩查询\n0.显示帮助\nq.删除用户信息\np.打赏我们"""

        return text

    def text_repeat(content):

        return content

    event_dict={
        "subscribe": "欢迎使用Gotit微信服务，您的支持是我们最大的动力！\n"+text_help(),
        "unsubscribe": "See you"
    }

    text_dict={
        "default": text_help,
        "help": text_help,
        "repeat": text_repeat,
        "p": "https://me.alipay.com/zhweifcx",
        #"1": "输入：cj&学号&密码&验证码",
    }

    def zf(self, init=True, fast=False):

        _tu = {
                'xh':'学号',
                'pw':'密码',
                'verify':'验证码',
                }
        if init:
            st = rds.hget(self.fromUser, 'status')
            print st
            if st in (None,):
                rds.hset(self.fromUser, 'status', 'xh')
                return self.replay_text('请输入学号')
            if st == 'xh':
                rds.hset(self.fromUser, 'xh', self.content)
                rds.hset(self.fromUser, 'status', 'pw')
                return self.replay_text('请输入密码')
            elif st == 'pw':
                rds.hset(self.fromUser, 'pw', self.content)
                rds.hset(self.fromUser, 'status', 'verify')
                # before login
                zf = ZF()
                time_md5 = zf.pre_login()
                rds.expire(self.fromUser, 600)
                rds.hset(self.fromUser, 'time_md5', time_md5)
                rds.hset(self.fromUser, 'status', 'verify')
                return self.replay_code(time_md5) # return checkcode msg

            elif self.content == 'r':
                rds.hset(self.fromUser, 'status', 'verify')
                time_md5=rds.hget(self.fromUser, 'time_md5')
                return self.replay_code(time_md5) # return checkcode msg

            elif st == 'verify':
                zf = Login()
                print "logging..."
                data = {
                        "xh": rds.hget(self.fromUser, 'xh'),
                        "pw": rds.hget(self.fromUser, 'pw'),
                        "verify": self.content,
                        }
                time_md5=rds.hget(self.fromUser, "time_md5")
                try:
                    zf.login(time_md5, data)
                    rds.hset(self.fromUser, 'status', 'logged')
                    return self.replay_text('登录成功！\n1.查询当前学期成绩\n2.查询上学期 \
                            成绩\nq.取消登录状态\n(输入对应序号)')
                except errors.PageError, e:
                    return self.replay_text("Error:{0}\n输入q退出查询过程".format(e.value))
            else:
                return self.replay_text(self.text_help())

        else:
            zf = Login()
            __dic = { # just call
                    '2': zf.get_score,
                    '3': zf.get_last_score,
                    }
            _time_md5 = rds.hget(self.fromUser, 'time_md5')
            _xh = rds.hget(self.fromUser, 'xh')
            zf.init_after_login(_time_md5, _xh)
            #score=zf.get_last_score()[0]
            score = __dic[self.content]()[0]
            from addons.data_factory import get_score_dict
            _dic = get_score_dict(score)
            ret =""
            for i in _dic:
                ret+="{} <{}>\n".format(i, _dic[i])
            if ret == "": ret = "暂无"
            return self.replay_text(ret)

        if fast: # 使用指令快速查询

            tu = self.content.split("&")
            xh = tu[1]
            pw_l = tu[2:-1]
            if len(pw_l) == 1:
                pw = pw_l[0]
            else:
                pw = "&".join(pw_l)
            verify = tu[-1]
            data = {
                    "xh": xh,
                    "pw": pw,
                    "verify": verify,
                    }
            time_md5=rds.hget(fromUser, "time_md5")
            try:
                zf.login(time_md5, data)
                score=zf.get_last_score()[0]
            except errors.PageError, e:
                return e.value
            from addons.data_factory import get_score_dict
            _dic = get_score_dict(score)
            ret =""
            for i in _dic:
                ret+="{} {}\n".format(i, _dic[i])
            return self.replay(ret)

    def POST(self):
        """响应微信
        """
        str_xml = web.data() #获得post来的数据

        xml = etree.fromstring(str_xml)#进行XML解析
        msgType=xml.find("MsgType").text
        self.fromUser=xml.find("FromUserName").text
        self.toUser=xml.find("ToUserName").text

        # MsgId=xml.find("MsgId").text
        if msgType == "event":
            mscontent = xml.find("Event").text
            replayText = self.event_dict.get(mscontent, self.text_help())
        elif msgType == "text":
            self.content =xml.find("Content").text
            _s = rds.hget(self.fromUser, 'status')
            if self.content == "q":
                rds.delete(self.fromUser)
                return self.replay_text('已清空用户信息,退出查询过程.')

            elif _s in ('logged',) and self.content in ('1','2'):
                return self.zf(init=False)
            elif self.content == "1" or _s in ('xh', 'pw', 'verify', 'login'):
                return self.zf(init=True)
            else:
                try:
                    _r = self.text_dict[self.content]
                    if callable(_r):
                        replayText = _r(self.content)
                    elif isinstance(_r, str):
                        replayText = _r
                except KeyError:
                    replayText = self.text_dict['default'](self.content)
        else:
            replayText = "不接受该类型信息，谢谢支持！"

        return self.replay_text(replayText)
