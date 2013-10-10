#!/usr/bin/env python
# -*- coding: utf-8 -*-

import apis

urls = (
    '/', 'index',
    '/login', 'login',
    '/logout', 'logout',
    '/succeed', 'succeed',

    '/old', 'old_index',
    '/zheng', 'zheng',
    '/more/([1-5])', 'more',
    '/score', 'score',
    '/cet', 'cet',
    '/cet/old', 'cet_old',
    '/lib', 'lib',
    '/api', apis.apis,

    '/contact.html', 'contact',
    '/notice.html', 'notice',
    '/help/gpa.html', 'help_gpa',
    '/comment.html', 'comment',
    '/what_you_need.html', 'what',
    '/donate.html', 'donate',
    '/root.txt', 'ttest',
    '/status', 'status'
)

