#!/usr/bin/env python
#coding=utf-8
import re
import urllib
import urllib2
import logging

class CET:
    '''Get CET score'''
    def get_last_cet_score(self,num,name):
        '''从官方网站获取最新四六级成绩'''
        header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6','Referer':'http://www.chsi.com.cn/cet/'}
        url = 'http://www.chsi.com.cn/cet/query'
        params = urllib.urlencode({'zkzh':num,'xm':name})
        req = urllib2.Request(url,data=params,headers= header)
        page = urllib2.urlopen(req).read()
        #解析
        ret = {}
        try:
            ret['name'], ret['school'], ret['type'], ret['num'], ret['time'] = re.findall("<td>(.*)</td>",page)[0:5]
            ret['total'] = re.findall('<span style="color: #F00;">  (\d*)  </span>',page)[0]
            ret['listen'],ret['read'],ret['mix'] =re.findall('(\d*) &nbsp;&nbsp;<span class="color01">',page)[1:4]
            ret['write'] = re.findall('(\d*)   </strong></td>',page)[0]
            print ret
            return ret
        except:
            ret["error"] = u"尚无成绩!"
            return ret


    def get_cet_table(self,num):
        '''获取四六级成绩（直接返回一个表格）'''
        param = urllib.urlencode({'post_xuehao':num})
        page = urllib2.urlopen(
            url = 'http://210.44.176.116/cjcx/stkcjcx_list.php',
            data = param,
            timeout=10
            ).read()
        patten = re.compile("</caption>(.*?)</table>",re.M|re.S)  
        #re.M表示多行匹配，re.S表示点任意匹配模式，改变'.'的行为 
        return patten.findall(page)[1]

    def get_cet_dict(self,num):
        '''获取四六级成绩（返回一个字典）'''
        param = urllib.urlencode({'post_xuehao':num})
        page = urllib2.urlopen(
            url = 'http://210.44.176.116/cjcx/stkcjcx_list.php',
            data = param,
            timeout=10
            ).read()
        patten = re.compile('<td scope="col" align="center" valign="middle" nowrap>&nbsp;(.*)</td>') 
        res =  patten.findall(page)
        ret = {}
        try:
            ret['num']=res[0]       #学号
            ret['name']=res[1]      #姓名
            ret['sex']=res[2]       #性别
            ret['year']=res[3]      #年级
            ret['collage']=res[5]   #学院
            ret['class']=res[6]     #班级
            ret['foreign']=res[11]  #外语类型
        except:
            logging.error("cannot get info")
            return -1
        total = (len(res)-13)/7
        cet_num=[]      #四六级考号
        cet_time=[]     #四六级考试时间
        cet_type=[]     #四六级考试类型
        cet_score=[]    #四六级成绩
        for i in range(total):
            cet_num.append(res[16+i*7])
            cet_time.append(res[17+i*7])
            cet_type.append(res[18+i*7])
            cet_score.append(res[19+i*7])
        ret['total']=total
        ret['cet_num']=cet_num
        ret['cet_time']=cet_time
        ret['cet_type']=cet_type
        ret['cet_score']=cet_score
        return ret

if __name__=='__main__':
    cet_num = "371012122112608"
    # cet_num = "371012121210906"
    # name = "马伟伟"
    name = "张卫"
    cet = CET()
    ret = cet.get_last_cet_score(cet_num, name)

    if type(ret) == dict:
        for key in ret.keys():
            print key,ret[key]
    else:
        print "aaaa"


    # num = raw_input("请输入你的学号: ")
    # cet = CET()
    # info =  cet.get_cet_dict(num)
    # for i in  range(info['total']):
    #     print info['num'],info['name'],
    #     print info['cet_num'][i],info['cet_time'][i],
    #     print info['cet_type'][i],info['cet_score'][i]
