#!/usr/bin/env python
# -*- coding: utf-8 -*-

from addons.get_CET import CET
from addons.lib import login, getbooklist_table
from addons.calc_GPA import GPA
from addons.get_all_score import ALL_SCORE

def get_old_cet(xh):

    """
    查询往年四六级成绩
    """
    c=CET()
    table = c.get_cet_table(xh)
    return table


def get_book(xh, pw):
    '''
    图书馆借书查询
    '''
    if login(xh,pw) is True:
        return getbooklist_table()


def get_gpa(xh):
    """
    提供学号
    返回学分基点
    """
    gpa_obj = GPA(xh)
    gpa_obj.getscore_page()
    gpa = gpa_obj.get_gpa()#["ave_score"]

    return gpa

def get_score(xh):
    """
    提供学号
    返回全部成绩表
    """
    score_obj = ALL_SCORE()
    score = score_obj.get_all_score(xh)

    return score
















