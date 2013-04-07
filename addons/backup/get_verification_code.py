#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
def get_code(url):
    html = urllib2.urlopen(url).read()
    return html

#get_code("http://210.44.176.132/CheckCode.aspx")
