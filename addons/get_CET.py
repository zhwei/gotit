#!/usr/bin/env python
#coding=utf-8
import re
import os
import urllib
import logging
import urllib2
from time import ctime

import requests

import errors
from redis2s import rds
DIR = os.path.abspath(os.path.dirname(__file__))


def get_proxy():
    proxy_file = file(DIR + "/proxy.txt")
    line = proxy_file.readlines()
    second = int(str(ctime())[-7:-5])
    proxy = line[second].strip()
    return proxy

def get_cet_fm_jae(number, name):
    """ 从jae抓取数据 """
    import json
    header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
    url = "http://gotitasia.jd-app.com/cet"
    data = {'number': number, 'name':name}
    json_object = requests.post(url, data, headers=header).text
    js = json.loads(json_object)
    return js.get('raw', None)



class CET:
    '''Get CET score'''
    def get_last_cet_score(self,num,name):
        '''从官方网站获取最新四六级成绩'''
        header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6','Referer':'http://www.chsi.com.cn/cet/'}
        url = "http://www.chsi.com.cn/cet/query"
        ####################################
        proxy = get_proxy()
        proxy_support = urllib2.ProxyHandler({'http':proxy})
        opener = urllib2.build_opener(proxy_support,urllib2.HTTPHandler)
        ####################################
        params = urllib.urlencode({'zkzh':num,'xm':name})
        req = urllib2.Request(url,data=params,headers= header)
        page = opener.open(req).read()#.decode('utf-8')
        #page = urllib2.urlopen(req).read().decode('utf-8')
        #解析
        ret = {}
        try:
            ret['name'], ret['school'], ret['type'], ret['num'], ret['time'] = re.findall("<td>(.*)</td>",page)[0:5]
            ret['total'] = re.findall('<span style="color: #F00;">(\d*)</span>',page)[0]
            ret['listen'],ret['read'],ret['mix'] =re.findall('</span>(\d*)&nbsp;&nbsp;<',page)[1:4]
            ret['write'] = re.findall('</span>(\d*)</strong></td>',page)[0]
            return ret
        except:
            ret["error"] = u"暂无成绩"
            return ret


    def get_cet_table(self,num):
        '''获取四六级成绩（直接返回一个表格）'''
        param = {'post_xuehao':num}
        try:
            page = requests.post(
                url = 'http://210.44.176.116/cjcx/stkcjcx_list.php',
                data = param,
                timeout=0.5
                ).text
        except requests.Timeout:
            raise errors.RequestError('无法连接成绩查询系统！')
        try:
            patten = re.compile("</caption>(.*?)</table>",re.M|re.S)
            #re.M表示多行匹配，re.S表示点任意匹配模式，改变'.'的行为
            ret = patten.findall(page)[1]
        except IndexError:
            rds.hset('error_score_cant_get_info', num, page)
            raise errors.PageError('找不到您的成绩单!')
        return ret

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

    def get_cet_json(self, xh):
        """获取往年四六级成绩"""
        _dic = self.get_cet_dict(xh)
        ret = dict()
        for i in range(_dic.get('total')):
            ret["{}-{}".format(_dic['cet_time'][i][:6],
                _dic['cet_type'][i])] = _dic['cet_score'][i]
        return ret

# if __name__=='__main__':
#     num = raw_input("请输入你的学号: ")
#     cet = CET()
#     print cet.get_cet_json(num)
    # info =  cet.get_cet_dict(num)
    # for i in  range(info['total']):
    #     print info['num'],info['name'],
    #     print info['cet_num'][i],info['cet_time'][i],
    #     print info['cet_type'][i],info['cet_score'][i]
