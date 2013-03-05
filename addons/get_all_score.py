#!/usr/bin/env python
#coding=utf-8
import re
import urllib
import urllib2
class ALL_SCORE():
    def get_cet_table(self,num):
        '''获取四六级成绩（直接返回一个表格）'''
        param = urllib.urlencode({'post_xuehao':num})
        page = urllib2.urlopen(
            url = 'http://210.44.176.116/cjcx/zcjcx_list.php',
            data = param,
            timeout=10
            ).read()
        patten = re.compile("</caption>(.*?)</table>",re.M|re.S)  
        #re.M表示多行匹配，re.S表示点任意匹配模式，改变'.'的行为 
        return patten.findall(page)

if __name__=='__main__':
    a = ALL_SCORE()
    num = raw_input()
    out =  a.get_cet_table(num)
    for i in out:
        print i

