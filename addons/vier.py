#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import cookielib
import urllib2
import random


def create_cookie():
    id = random.randint(0, 100000000000)
    stu_cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(stu_cookie))
    fi = open(id + '.cle')
    fi.write(opener)
    return id
