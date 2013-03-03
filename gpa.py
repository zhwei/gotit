#!/usr/bin/env python
#coding=utf-8
#学分基点=∑(课程成绩*课程学分)/应修学分
import re
import urllib
import urllib2
def getscore_page(num=0):
    param = urllib.urlencode({'post_xuehao':num})
    page = urllib2.urlopen(
        url = 'http://210.44.176.116/cjcx/zcjcx_list.php',
        data = param,
        timeout=10
        ).read()
    return page

def calc_score(num=0):
    page = getscore_page(num)
    patten = re.compile('<td scope="col" align=".*" valign="middle" nowrap>&nbsp;(.*)</td>')
    td = patten.findall(page)
    ret={}
    try:
        ret["id"] = td[0]      #学号
        ret["name"] = td[1]	
        ret["collage"] = td[4]	#学院
        ret["major"] = td[5]	#专业
        ret["Class"] = td[6]	#班级
    except:
        print "cannot get info"
        return 0
    type=[]     #类别
    course = [] #课程名称
    credits = []#学分
    score = []  #成绩
    score2 = [] #补考成绩
    second = [] #第二专业
    sc_dict={   #成绩转换
        '合格':60,
        '不合格':0,
        '优秀':95,
        '良好':84,
        '中等':73,
        '及格':62,
        '不及格':0,
        '缺考':0,
        '禁考':0,
        '退学':0,
        '缓考（时':0,
        '缓考':0,
        '休学':0,
        '未选':0,
        '作弊':0,
        '取消':0,
        '免修':60,
        '-':0,
        '':0
    }

    all = len(td)
    i = 13
    while(i+16<all):
        type.append(td[i+3].replace(' ',''))
        course.append(td[i+5].replace(' ',''))
        credits.append(td[i+7].replace(' ',''))
        second.append(td[i+8].replace(' ',''))
        score.append(td[i+10].replace(' ',''))
        score2.append(td[i+11].replace(' ',''))
        i+=16
    ret['type']=type
    ret['course']=course
    ret['credits']=credits
    ret['second']=second
    ret['score']=score
    ret['score2']=score2
    not_accept=[]       #没有通过
    totle_credits = 0   #总学分
    totle_score = 0     #总成绩
    ave_score = 0       #平均成绩
    i = 0
    all = len(type)
    while(i<all):
#        print score[i],credits[i],totle_score,totle_credits
        if type[i]=='公选课':   #公选课不计算成绩
            i+=1
            continue
        s=-1    #第一次考试转换后的成绩
        s2=-1   #补考转换后的成绩

        if credits[i]=='': #学分一项位空
            credits[i]='0'

        try:
            s = sc_dict[score[i]]   #将成绩五级成绩等转换成百分成绩
        except:     #转换出错
            try:
                float(score[i])    #判断成绩是不是数字
            except:
                print score[i]
                raw_input()

        try:
            s2 = sc_dict[score2[i]]
        except:
            try:
                float(score2[i])
            except:
                print score2[i]
                raw_input()

        totle_credits+=float(credits[i]) #总学分
        if s == -1:     #百分制成绩
            if float(score[i])<60:          #成绩小于60
                if s2 == -1:
                    if float(score2[i]) >= 60: #补考通过成绩为60
                        totle_score+=float(credits[i])*60
                    else:
                        not_accept.append(course[i])
                elif s2 >= 60:
                    totle_score+=float(credits[i])*60 #补考通过为60分
                else:
                    not_accept.append(course[i])
                i+=1
                continue
            totle_score+=float(credits[i])*float(score[i])
        else:
            if s<60:
                if s2==-1:
                    if float(score2[i]) >= 60:
                        totle_score+=float(credits[i])*60
                    else:
                        not_accept.append(course[i])
                elif s2 >= 60:
                    totle_score+=float(credits[i])*60 #补考通过为60分
                else:
                    not_accept.append(course[i])

                i+=1
                continue
            totle_score+=float(credits[i])*s
        i+=1

    if totle_credits==0: #总学分为0
        ave_score = 0
    else:
    
        ave_score = totle_score/totle_credits   #计算平均学分基点
    ret['ave_score']=ave_score
    ret['totle_score']=totle_score
    ret['totle_credits']=totle_credits
    ret['not_accept']=not_accept
    return ret
