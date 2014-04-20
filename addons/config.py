#!/usr/bin/env python
# -*- coding: utf-8 -*- 


## 用户正方cookies过期时间
# 毫秒
COOKIES_TIME_OUT = 600000

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

# 网站运行模式
debug_mode = False
