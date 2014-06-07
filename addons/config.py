#!/usr/bin/env python
# -*- coding: utf-8 -*- 


## 用户正方cookies过期时间
# 毫秒
COOKIES_TIME_OUT = 600000

# 网站运行模式
DEBUG = True

domains = {
    "main": "gotit.asia",
    "www": "www.gotit.asia",
    "api": "api.gotit.asia",
    "wechat": "wechat.gotit.asia",
    "manage": "manage.gotit.asia",
}

if DEBUG:
    domains = {
        "main": "www.t.gotit.asia",
        "www": "www.t.gotit.asia",
        "api": "api.t.gotit.asia",
        "wechat": "wechat.t.gotit.asia",
        "manage": "manage.t.gotit.asia",
    }

# 配置参数
# ---------------------------
# 正方教务系统
# 教务系统url,注意不要忘记最后的"/"
zf_url = "http://210.44.176.132/"
# url中是否有随机字符串
random = False

WEIBO_APP_KEY = '4001516920'
WEIBO_APP_SECRET = "44a4fb573339e30a901249978a1322b9"
ADMIN_WEIBO_ID = 2674044833


MONGO_DUMP_PATH = "/home/group/.bin/mongodump"
LOG_FILE_PATH = {
    "stderr":"/home/group/gotit/log/stderr.log",
    "stdout":"/home/group/gotit/log/stdout.log",
    "nginx_error":"/home/group/gotit/log/nginx-error.log",
    "nginx_access":"/home/group/gotit/log/nginx-access.log",
}
