#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PageError(Exception):
    """页面有弹出警告
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ZfError(Exception):
    """正方系统异常时
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
