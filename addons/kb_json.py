#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json

# just for test
#import pickle
#inp = open('kbb.list')
#kb = pickle.load(inp)


class KBJSON:

    """
    用于生成课表json, 输出为字典列表，需要传入课表html列表，
    html由bs3从正方系统解析获得
    """

    course_re = (
        '<td align="Center" rowspan="2" width="7%">(.*?)<br />(.*?)<br />(.*?)<br />(.*?)</td>',
        '<td align="Center" rowspan="2">(.*?)<br />(.*?)<br />(.*?)<br />(.*?)</td>',
        '<td class="noprint" align="Center" rowspan="2">(.*?)<br />(.*?)<br />(.*?)<br />(.*?)</td>'
        )
    time_re = '(..)第(\d+),(\d+)节{第(\d+)-(\d+)'.decode('utf-8')
    odd_re = '\|(.)周}'.decode('utf-8')

    list_course = []

    def __init__(self, kb_html_list):

        self.kb_html_list = kb_html_list

    def __json_err(content):
        """用于生成json error内容"""
        dic = {'error': content}
        json_object = json.dumps(dic)
        return json_object


    def __create_course_dict(self, tu_course):
        '''
        传入的是课程元组, 输出课程字典

        课程字典详解：
        {
            "code": "BX02080014",（课程编号）
            "credit": "2.0",
            "location": "东B302",
            "name": "媒体策划与数字编辑（通识课）",
            "plan": "星期一 7-9 节/东B302（2-12 周）",
                    （原始字符串，用于检测解析是否准确）
            "teacherName": "鞠英辉",
            "dayOfWeek": "MON",（周一到周日，也可以1234567这样子）
            "oddEvenFlag": 0,（单周为1，双周为2，不分单双周为0）
            "sectionFrom": "7",（节次）
            "sectionTo": "9",
            "weekFrom": "2",（开始上课周次）
            "weekTo": "12 "
        }
        '''



        try:
            odd = re.compile(self.odd_re).findall(tu_course[1])[0].encode('utf-8')
            if odd == '双':
                odd_flag = 2
            elif odd == '单':
                odd_flag = 1
            else:
                odd_flag = 0

        except IndexError, ValueError:
            odd_flag = 0

        try:

            schedule = re.compile(self.time_re).findall(tu_course[1])
            day_of_week, section_from, section_to, week_from, week_to = schedule[0]
            dict_course = {
                    "location":tu_course[3],
                    "name":tu_course[0],
                    "plan":tu_course[1],
                    "teacherName":tu_course[2],
                    "dayOfWeek": day_of_week,
                    "oddEvenFlag":odd_flag,
                    "sectionFrom": section_from,
                    "sectionTo":section_to,
                    "weekFrom":week_from,
                    "weekTo":week_to,
                    }

            return dict_course

        except ValueError:
            return False

    def get_json(self):

        for li in self.kb_html_list:

            for co_re in self.course_re:
                parm = re.compile(co_re)
                re_result = parm.findall(str(li).decode('utf-8'))

                for res in re_result:
                    try:
                        course_dict = self.__create_course_dict(res)
                    except IndexError:
                        pass
                    else:
                        if course_dict:
                            self.list_course.append(course_dict)
                        else:
                            return self.__json_err('some lession error, please contact admin')

        json_object = json.dumps(self.list_course)

        return json_object





#k = KbJson(kb)
#print k.get_json()















