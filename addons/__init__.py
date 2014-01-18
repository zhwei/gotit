#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'zhwei maweiwei'

from addons.get_CET import CET
from addons.library import login, getbooklist_table

def get_old_cet(xh):

    """
    查询往年四六级成绩
    """
    c=CET()
    table = c.get_cet_table(xh)
    return (table, )

def get_book(xh, pw):
    '''
    图书馆借书查询
    '''
    if login(xh,pw) is True:
        table = getbooklist_table()
        table=table.replace("../opac/","http://222.206.65.12/opac/")
        return (table,)
