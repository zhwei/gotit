#!/usr/bin/python2.7
#encoding=utf-8
#   从http://www.site-digger.com/html/articles/20110516/proxieslist.html抓取代理服务器列表生成
#   proxy.txt文件


import urllib2
import re

url = "http://www.site-digger.com/html/articles/20110516/proxieslist.html"

page = urllib2.urlopen(url).read()

result = re.findall("<td>(.*)</td>",page)

#print result
f = file("proxy.txt","w")

i = 0

try:
    while i < 600:
        f.write(result[i] + "\n")
        i = i + 2
except IndexError:
    print "end"
    #print i
    print "已在当前目录生成proxy.txt文件"
