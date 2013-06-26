#!/usr/bin/env python
#coding=utf-8
import re
import urllib
import urllib2
import config

class ALL_SCORE():
    def get_all_score(self,num):
        '''获取全部成绩（直接返回一个表格）'''
        param = urllib.urlencode({'post_xuehao':num})
        try:
            page = urllib2.urlopen(url = config.score_url, data = param,).read()
        except urllib2.URLError:
            return "can not reach"
        patten = re.compile('<span class="style3">成绩信息</span>(.*?)</table>',re.M|re.S)  
        #re.M表示多行匹配，re.S表示点任意匹配模式，改变'.'的行为 
        return patten.findall(page)

if __name__=='__main__':
    a = ALL_SCORE()
    num = raw_input()
    out =  a.get_all_score(num)
    for i in out:
        print i

