#!/usr/bin/env python
#coding=utf-8

import cookielib
import urllib
import urllib2
import json
import re

import errors

cookies = cookielib.LWPCookieJar()
handlers = [
    urllib2.HTTPHandler(),
    urllib2.HTTPSHandler(),
    urllib2.HTTPCookieProcessor(cookies)
    ]
opener = urllib2.build_opener(*handlers)

def login(number,pwd):
    '''登陆'''
    login_url = 'http://222.206.65.12/reader/redr_verify.php'
    data = {
        'number':number,
        'passwd':pwd,
        'returnUrl':'',
        'select':'cert_no',
    }
    data = urllib.urlencode(data)
    req = urllib2.Request(url=login_url, data=data)
    login_ret = opener.open(req).read()
    if login_ret.find('密码错误') > 0:
        return False
    elif login_ret.find('您尚未完成身份认证') > 0:
        raise errors.PageError('您尚未完成图书馆身份认证！') 
    elif login_ret.find("证件信息") > 0:
        return True

def getbooklist_table():
    '''获取图书列表(表格)'''
    booklist_url = 'http://222.206.65.12/reader/book_lst.php'
    req = urllib2.Request(booklist_url)
    ret = opener.open(req).read()
    if ret.find('您的该项记录为空！'):
        return ("您没有借书记录")
    patten = re.compile("<table.*?</table>",re.M|re.S)  
    book_table = patten.findall(ret)
    return book_table

def getbooklist_json():
    '''获取图书列表(json格式)'''
    all = {}
    table = getbooklist_table()
    patten_th = re.compile('<td bgcolor="#d8d8d8" class="greytext">(.*?)</td>')
    th = patten_th.findall(table)
    for i in th[:-1]:
        all[i] = []
    patten_td = re.compile('<td bgcolor="#FFFFFF" class="whitetext" width=".*?">(.*?)</td>')
    td = patten_td.findall(table)
    i = 0
    patten_bookname = re.compile('">(.*?)<')
    patten_date_end = re.compile('<font color=>(.*?)        </font>')
    while i + 6 < len(td):
        all['条码号'].append(td[i])
        book_name = patten_bookname.findall(td[i+1])[0]
        book_name = unescape(book_name)
        all['题名'].append(book_name)
        all['责任者'].append(unescape(td[i+2]))
        all['借阅日期'].append(td[i+3])
        date_end = patten_date_end.findall(td[i+4])[0]
        all['应还日期'].append(date_end)
        all['馆藏地'].append(td[i+5])
        all['附件'].append(td[i+6])
        i += 7
    all['total'] = len(all['条码号'])
    return json.dumps(all)

def unescape(text):
    """Removes HTML or XML character references 
    and entities from a text string.
    keep &amp;, &gt;, &lt; in the source code.
    from Fredrik Lundh
    http://effbot.org/zone/re-sub.htm#unescape-html
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                print "erreur de valeur"
                pass
        else:
            # named entity
            try:
                if text[1:-1] == "amp":
                    text = "&amp;amp;"
                elif text[1:-1] == "gt":
                    text = "&amp;gt;"
                elif text[1:-1] == "lt":
                    text = "&amp;lt;"
                else:
                    print text[1:-1]
            except KeyError:
                print "keyerror"
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

# if __name__=='__main__':
#     number = raw_input('学号：')
#     pwd = raw_input('密码：')
#     if login(number,pwd) is True:
#         print getbooklist_table()
#         print getbooklist_json()

def get_book(xh, pw):
    if login(xh,pw) is True:
        return getbooklist_table().replace("../opac/","http://222.206.65.12/opac/")
