#!/usr/bin/env python
#coding=utf-8
import re
import urllib
import urllib2
class ALL_SCORE():
    def get_all_score(self,num):
        '''获取四六级成绩（直接返回一个表格）'''
        param = urllib.urlencode({'post_xuehao':num})
        page = urllib2.urlopen(
            url = 'http://210.44.176.116/cjcx/zcjcx_list.php',
            data = param,
            timeout=10
            ).read()
        patten = re.compile('<span class="style3">成绩信息</span>(.*?)</table>',re.M|re.S)  
        #re.M表示多行匹配，re.S表示点任意匹配模式，改变'.'的行为 
        return patten.findall(page)

if __name__=='__main__':
    a = ALL_SCORE()
    num = "1111051046"
    out =  a.get_all_score(num)
    #print out
    for i in out:
        print i

