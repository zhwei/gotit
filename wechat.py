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

from addons import mongo2s
from addons.zfr import ZF, Login
from addons import redis2s
from addons import errors
from addons.calc_GPA import GPA
from addons.get_CET import CET
from addons.data_factory import get_score_dict
from addons.autocache import redis_memoize

# init redis
rds = redis2s.init_redis()
# init mongoDB
db = mongo2s.init_mongo()

# 账户过期时间(s) 十分钟
EXPIRE_SECONDS = 600
# 微信Token
WEIXIN_TOKEN = "gotitzhangwei"

INDEX_HELP_TEXT = \
"""欢迎使用！
按需求输入下面序号:
1.登陆查询(指令简单)*推荐*
2.快速查询(指令复杂)
3.查询绩点
4.查询往年四六级成绩
- - -
0.显示此帮助菜单
q.删除用户信息
- - -
666.建议or留言
999.官网链接(更多功能)
000.赞助我们"""

LOGGED_HELP_TEXT = \
"""输入下面序号查询相关内容:
1.查询当前学期成绩
2.查询上学期成绩
3.查询绩点
4.查询往年四六级成绩
- - -
00.查看此查询列表
11. 重新查询
q.  取消登录状态"""

FAST_ZF_HELP = \
"""按需求输入下面序号:
查询当前学期成绩:
1&学号&密码&验证码
查询上学期成绩:
2&学号&密码&验证码
- - -
0.显示此帮助菜单
q.删除用户信息
- - -
000.赞助我们"""

class BaseMsg(object):
    """基本信息操作"""

    fromUser= None
    toUser = None

    def text_help(self):
        return INDEX_HELP_TEXT

    def text_success(self):
        return LOGGED_HELP_TEXT

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

    def replay_code(self, uid, content=""):
        if rds.hget(self.fromUser, 'status').startswith('fast'):
            r = '2'
        else: r = 'r'
        text = """
        <xml>
        <ToUserName><![CDATA[{0}]]></ToUserName>
        <FromUserName><![CDATA[{1}]]></FromUserName>
        <CreateTime>{2}</CreateTime>
        <MsgType><![CDATA[news]]></MsgType>
        <ArticleCount>1</ArticleCount>
        <Articles>
            <item>
                <Title><![CDATA[请输入验证码({5}.重新获取)]]></Title>
                <Description><![CDATA[{4}r 重新获取验证码\nPS:距离远一点能看的更清楚\nq.退出查询状态]]></Description>
                <PicUrl><![CDATA[http://gotit.asia/zheng/checkcode?r={2}&uid={3}]]></PicUrl>
                <Url><![CDATA[http://gotit.asia/zheng/checkcode?r={2}&uid={3}]]></Url>
            </item>
        </Articles>
        </xml> """.format(self.fromUser, self.toUser, int(time.time()), uid, content, r)
        return text

class ProcessMsg(object):
    """处理查询操作"""

    def get_gpa(self, xh):
        """ 获取绩点
        """
        gpa = GPA(xh)
        try:
            gpa.getscore_page()
            jidi = gpa.get_gpa()
            ret = "学分绩点: {}\n".format(jidi)
        except errors.PageError, e:
            ret = e
        return ret

    def get_former_cet(self, xh):
        """获取往年四六级成绩"""
        cet = CET()
        _dic = cet.get_cet_dict(xh)
        ret = ""
        for i in range(_dic.get('total')):
            ret += "<{}-{}>  {}\n".format(_dic['cet_time'][i][:6],
                    _dic['cet_type'][i], _dic['cet_score'][i])
        return ret

    def get_zf_score(self, t):
        """
        根据序号获取正方成绩
        序号默认为 self.content
        条件: fromUser 必须是已经登录成功的
        """
        ret = ""
        zf = Login()
        _zf_dic = { # just call
                '1': zf.get_score,
                '2': zf.get_last_score,
                }
        _uid = rds.hget(self.fromUser, 'uid')
        _xh = rds.hget(self.fromUser, 'xh')
        zf.init_after_login(_uid, _xh)
        try:
            score = _zf_dic[t]()[0] # 条件选择
            rds.expire(self.fromUser, EXPIRE_SECONDS) # 延长过期时间
        except KeyError:
            return self.text_success()
        _dic = get_score_dict(score)
        for i in _dic:
            ret+="<{}> {}\n".format(i, _dic[i])
        if ret == "": ret = "暂无\n"
        return ret

    def zf_process(self, init=True, fast=False):
        _tu = {
                'xh':'学号',
                'pw':'密码',
                'verify':'验证码',
                }
        if init:
            """引导输入学号等信息"""
            st = rds.hget(self.fromUser, 'status')
            if st not in ('xh','pw','verify') or self.content == '11':
                rds.hset(self.fromUser, 'status', 'xh')
                return self.replay_text('请输入学号:\n(q.退出查询状态)')
            if st == 'xh':
                rds.hset(self.fromUser, 'xh', self.content)
                rds.hset(self.fromUser, 'status', 'pw')
                __egg = '请输入密码:\n(q.退出查询状态)'
                if self.content == '1112051112': __egg+="\n love you, my x!"
                return self.replay_text(__egg)
            elif st == 'pw':
                rds.hset(self.fromUser, 'pw', self.content)
                rds.hset(self.fromUser, 'status', 'verify')
                # before login
                zf = ZF()
                uid = zf.pre_login()
                rds.expire(self.fromUser, EXPIRE_SECONDS)
                rds.hset(self.fromUser, 'uid', uid)
                rds.hset(self.fromUser, 'status', 'verify')
                return self.replay_code(uid) # return checkcode msg
            elif self.content == 'r':
                # 再次获取验证码
                rds.hset(self.fromUser, 'status', 'verify')
                uid=rds.hget(self.fromUser, 'uid')
                return self.replay_code(uid) # return checkcode msg
            elif st == 'verify':
                zf = Login()
                data = {
                        "xh": rds.hget(self.fromUser, 'xh'),
                        "pw": rds.hget(self.fromUser, 'pw'),
                        "verify": self.content,
                        }
                uid=rds.hget(self.fromUser, "uid")
                try:
                    zf.login(uid, data)
                    rds.hset(self.fromUser, 'status', 'logged')
                    return self.replay_text('登录成功！十分钟内无操作删除用户信息。\n{}'.format(self.text_success()))
                except errors.PageError, e:
                    return self.replay_text("错误:{0}\n- - - \nr.  重新获取验证码\n11.重新查询\nq. 退出查询过程".format(e.value))
            else:
                return self.replay_text(self.text_help())
        else:
            """登录成功后的操作"""
            if self.content == "00":
                # 内容列表
                return self.replay_text(self.text_success())
            elif self.content in ('1', '2'):
                # 正方系统相关
                try:
                    ret = self.get_zf_score(t=self.content)
                except KeyError:
                    return self.replay_text(self.text_success())
            elif self.content in ('3', '4'):
                # 绩点 & 往年四六级成绩
                _dic = {
                        '3': self.get_gpa,
                        '4': self.get_former_cet,
                        }
                _xh = rds.hget(self.fromUser, 'xh')
                rds.expire(self.fromUser, EXPIRE_SECONDS)
                ret = _dic[self.content](_xh)
            else:
                ret = ""

            ret += "- - -\n00.查看查询列表"
            return self.replay_text(ret)

    def fast_zf(self, init=True):
        """通过指令快速查询"""
        if self.content == '00':
            return self.replay_text(FAST_ZF_HELP)
        if init==True:
            z = ZF()
            uid = z.pre_login()
            rds.expire(self.fromUser, EXPIRE_SECONDS)
            rds.hset(self.fromUser, 'uid', uid)
            rds.hset(self.fromUser, 'status', 'fast1')
            return self.replay_code(uid, content=FAST_ZF_HELP) # return checkcode msg
        else:
            try:
                tu = self.content.split("&")
                _xh, pw_l, _verify   = tu[1], tu[2:-1], tu[-1]
            except IndexError:
                return self.replay_text(FAST_ZF_HELP)
            if len(pw_l) == 1: _pw = pw_l[0]
            else: _pw = "&".join(pw_l)
            _data = {
                    "xh": _xh,
                    "pw": _pw,
                    "verify": _verify,
                    }
            uid=rds.hget(self.fromUser, "uid")
            zf = Login()
            try:
                zf.login(uid, _data)
                rds.hset(self.fromUser, 'xh', _xh)
                ret = self.get_zf_score(tu[0])
            except KeyError:
                ret = "前缀错误\n{}".format(FAST_ZF_HELP)
            except errors.PageError, e:
                ret = e.value
            rds.hset(self.fromUser, 'status', None)
            ret += "- - - \n {}".format(FAST_ZF_HELP)
            return self.replay_text(ret)

    def cet_jidi(self, xh=False):
        """获取绩点或者往年cet成绩"""
        if xh is False:
            # self.content must be 3 or 4
            rds.hset(self.fromUser, 'status', self.content)
            return self.replay_text('请输入学号:\nq.退出查询过程')
        _dic = {
                '3': self.get_gpa,
                '4': self.get_former_cet,
                }
        _t = rds.hget(self.fromUser, 'status')
        try:
            ret = _dic[_t](xh)
            rds.hset(self.fromUser, 'status', None)
        except errors.RequestError, e:
            ret = e.value
        return self.replay_text(ret)

    def comment(self, init=True):
        """留言"""
        if init:
            rds.hset(self.fromUser, 'status', 'comment')
            text = "格式: ly#内容\n谢谢支持！"
            return self.replay_text(text)
        if self.content.startswith('ly#') is False:
            rds.hset(self.fromUser, 'status', None)
            return self.replay_text("格式错误, 留言结束,谢谢支持。")
        _data = {
                'user': self.fromUser,
                'content': self.content[3:],
                'datetime': datetime.datetime.now(),
                }
        db.wxcomment.insert(_data)
        rds.hset(self.fromUser, 'status', None)
        return self.replay_text("提交成功，谢谢您的支持！")

    def clear_user(self):
        # 清空用户状态
        rds.delete(self.fromUser)
        return self.replay_text('已清空用户信息,退出查询过程.\n{}'.format(self.text_help()))


urls = (
        '/', 'WeixinIndex',
        '/weixin', 'WeixinInterface',
        )

app = web.application(urls, locals())

class WeixinIndex:

    @redis_memoize('weixin')
    def GET(self):
        from web.contrib.template import render_jinja
        render = render_jinja('templates', encoding='utf-8')
        from addons.config import domains
        return render.weixin(domains=domains)

class WeixinInterface(BaseMsg, ProcessMsg):

    def GET(self):
        #获取输入参数
        try:
            data = web.input(_method="GET")
            signature, timestamp = data.signature,data.timestamp
            nonce, echostr = data.nonce,data.echostr
        except AttributeError:
            return 't'
        token= WEIXIN_TOKEN
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

    # 基本事件响应信息
    event_dict={
        "subscribe": "欢迎使用Gotit微信服务，您的支持是我们最大的动力！\n"+INDEX_HELP_TEXT,
        "unsubscribe": "See you !"
    }

    def POST(self):
        """响应微信
        """
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        msgType=xml.find("MsgType").text
        self.fromUser=xml.find("FromUserName").text
        self.toUser=xml.find("ToUserName").text

        if msgType == "event":
            mscontent = xml.find("Event").text
            replayText = self.event_dict.get(mscontent, self.text_help())
        elif msgType == "text":
            self.content =xml.find("Content").text
            # 基本文本响应信息
            text_dict={
                "help": INDEX_HELP_TEXT,
                "000": "谢谢您的支持！\nhttps://me.alipay.com/zhweifcx",
                "999": "欢迎使用Gotit！\nhttp://gotit.asia/",
                "666": self.comment,
                "q": self.clear_user,
                "auth": "zhwei\nhttp://zhangweide.cn",
                "py": "I love python",
            }
            try:
                _r = text_dict[self.content]
                if callable(_r): return _r()
                elif isinstance(_r, str):
                    return self.replay_text(_r)
            except KeyError:
                pass
            # 获取用户状态
            _s = rds.hget(self.fromUser, 'status')
            # 引导查询操作
            if _s in ('logged',) and self.content != '11':
                return self.zf_process(init=False)
            elif self.content in ('1', '11')  or _s in ('xh', 'pw', 'verify',):
                return self.zf_process(init=True)
            # 快速指令查询
            elif self.content in ('2',):
                return self.fast_zf()
            elif str(_s).startswith('fast'):
                return self.fast_zf(init=False)
            # gpa and old cet
            elif self.content in ('3', '4'):
                return self.cet_jidi()
            elif _s in ('3', '4'):
                return self.cet_jidi(self.content)
            # comment
            elif _s == 'comment':
                return self.comment(False)

        replayText = self.text_help()
        return self.replay_text(replayText)
