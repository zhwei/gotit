#!/usr/bin/env python
# -*- coding: utf-8 -*-

## code.py目录

pwd = '/home/bak/apps/gotit/'

## 是否启用多线程加速（正方）
zf_accelerate=True


## 正方 说明/警告
zheng_alert = ""


# 正方教务系统
# 教务系统url,注意不要忘记最后的"/"
zf_url = "http://210.44.176.133/"
# url中是否有随机字符串
random = True
# 成绩查询网址
score_url = "http://210.44.176.116/cjcx/zcjcx_list.php"

# 四六级成绩查询
# POST地址
cet_url = "http://www.chsi.com.cn/cet/query"
# 是否使用bae查询
baefetch = True
# 查询页缓存时间(秒)
index_cache = 1000
# 网站运行模式
debug_mode = True
