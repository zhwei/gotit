#!/usr/bin/env python
# -*- coding: utf-8 -*-

from addons.get_CET import CET
from addons.lib import login, getbooklist_table, getbooklist_json

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

import xml.etree.cElementTree as ET
a=ET.ElementTree