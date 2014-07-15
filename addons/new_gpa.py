#!/usr/bin/env python
#coding=utf-8
#学分基点=∑(课程成绩*课程学分)/应修学分
import re
import logging
import json

import requests

import config
import errors
from redis2s import rds

class GPA:
    '''Calculator Grade Point Average'''

    __num = None
    __table = None
    __ret = {}
    page = None

    def __init__(self,num):
        self.__num = num

    def getscore_page(self):
        '''获取成绩页面'''
        param = {'post_xuehao': GPA.__num}
        try:
            self.page = requests.post(url="http://210.44.176.116/cjcx/zcjcx_list.php",
                                        data=param, timeout=5.0).text
        except requests.Timeout:
            raise errors.RequestError('无法连接成绩查询系统')

    # 直接抓取表格内容并返回
    def get_all_score(self):
        '''获取全部成绩（直接返回一个表格）'''
        patten = re.compile('<span class="style3">成绩信息</span>(.*?)</table>',re.M|re.S)
        return patten.findall(self.page)


    def __match_table(self):
        '''正则表达式获取完整表格'''
        par = re.compile('<td scope="col" align=".*" valign="middle" nowrap>&nbsp;(.*?)</td>')
        self.__table = par.findall(page.content)
        return self.__table

    def __calc_score(self):
        '''计算平均学分基点'''
        score_list = []
        for j in [ret[i:i + 16] for i in xrange(13, len(ret), 16)]:
            dic = {
                "year": j[1],           # 学年
                "category": j[3],       # 类别
                "name": j[5],           # 课程名称
                "credit": float(j[7]),  # 学分
                "model": j[8],          # 考核方式
                "initial": j[10],       # 原考成绩
                "makeup": j[11],        # 补考成绩
            }
            score_list.append(dic)
         
        for item in score_list[:]:
            if item['category'] in ("公选课",) or item['model'] in ("第二专业", ):
                score_list.remove(item)
            else:
                # 处理其他分数形式
                convert_dict = {
                    '优秀': 95, '良好': 84, '良': 84, '中等': 73, '免修': 70,
                    '及格': 62,  '已修': 60, '及': 62, '合格': 60,
                    '不及格': 0, '缺考': 0, '禁考': 0, '退学': 0, '-': 0,
                    '休学': 0, '未选': 0, '作弊': 0, '不合格': 0,'取消': 0,
         
                }
                for _t in ('initial', 'makeup'):
                    if item[_t] == "": item[_t] = 0
                    if item[_t] in convert_dict.keys():
                        item[_t] = convert_dict[item[_t]]
         
                stay_list = {'缓考（时': 0, '缓考': 0,}
                if item['initial'] in stay_list:
                    if item['makeup'] >= 60: item['initial'] = float(item['makeup'])
                elif item['makeup'] in stay_list:
                    item["makeup"] = 0
         
         
                # 计算课程绩点
                item["initial"] = 0 if float(item['initial']) < 60 else float(item['initial'])
                item["makeup"] = 60 if float(item['makeup']) >= 60 else 0
         
        score_dict = {}
        for l in score_list:
            if l['name'] in score_dict.keys():
                score_dict[l['name']]['initial'] = max(l['initial'], score_dict[l['name']]['initial'])
                score_dict[l['name']]['makeup']  = max(l['makeup'], score_dict[l['name']]['makeup'])
            else:
                score_dict.update({l['name']:l})
         
         
        sum_course_gpa = float()
        sum_course_credit = float()
        for d in score_dict:
            item = score_dict[d]
            sum_course_gpa += float(max(item['initial'], item['makeup'])) * item['credit']
            sum_course_credit += item['credit']
         
        return sum_course_gpa / sum_course_credit

    def get_dict(self):
        '''通过这个函数调用上面的函数'''
        self.__match_table()
        self.__get_score_info()
        self.__calc_score()
        return GPA.__ret

    def get_gpa(self):
        """返回平均学分绩点"""
        self.getscore_page()
        info = self.get_dict()
        return info["ave_score"]

    def get_allscore_dict(self):
        """ 获取全部成绩信息 字典
        详细格式见`api.markdown`
        """
        self.getscore_page()
        info = self.get_dict()
        data = {info["course"][i]: {"initial": info["score"][i],
                "makeup":info["score2"][i]} for i in range(len(info["course"]))}
        return data
        # return json.dumps(data, ensure_ascii=False)

# if __name__=='__main__':
#     num = raw_input("请输入你的学号: ")
#     gpa = GPA(num)
#     print gpa.get_score_json()
#     gpa.getscore_page()
#     info = gpa.get_dict()
#     for i in range(len(info["course"])):
#         print info["course"][i], info["score"][i], info["score2"][i]
