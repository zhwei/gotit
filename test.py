#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import pickle

inp = open('kbb.list')

kb = pickle.load(inp)


course_re = (
    '<td align="Center" rowspan="2" width="7%">(.*?)<br />(.*?)<br />(.*?)<br />(.*?)</td>',
    '<td align="Center" rowspan="2">(.*?)<br />(.*?)<br />(.*?)<br />(.*?)</td>',
    '<td class="noprint" align="Center" rowspan="2">(.*?)<br />(.*?)<br />(.*?)<br />(.*?)</td>'
    )

course_list = []

for l in kb:

    for co_re in course_re:
        parm = re.compile(co_re)
        re_result = parm.findall(str(l).decode('utf-8'))

        for a in re_result:
            #course_list.append(a)
            for i in a:
                print i
