#!/usr/bin/env python
#coding=utf-8
import os
i = 1
while i < 100:
    os.system("curl http://210.44.176.132/CheckCode.aspx > "+str(i)+'.gif')
    i = i+1
