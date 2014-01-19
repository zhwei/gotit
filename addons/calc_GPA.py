#!/usr/bin/env python
#coding=utf-8
#学分基点=∑(课程成绩*课程学分)/应修学分
import re
import urllib
import urllib2
import logging

import config
import errors

class GPA:
    '''Calculator Grade Point Average'''
    __num = 0
    __table = None
    __ret = {}
    page = None

    def __init__(self,num):
        GPA.__num = num

    def getscore_page(self):
        '''获取成绩页面'''
        param = urllib.urlencode({'post_xuehao':GPA.__num})
        try:
            self.page = urllib2.urlopen( url = config.score_url, data = param, timeout=5).read().decode('utf-8')
        except urllib2.URLError:
            return None

    # 直接抓取表格内容并返回
    def get_all_score(self):
        page = self.page
        patten = re.compile('<span class="style3">成绩信息</span>(.*?)</table>',re.M|re.S)  
        return patten.findall(page)


    def __match_table(self):
        '''正则表达式获取完整表格'''
        page = self.page
        patten = re.compile('<td scope="col" align=".*" valign="middle" nowrap>&nbsp;(.*)</td>')
        GPA.__table = patten.findall(page)
        return 0

    def __get_basic_info(self):
        '''获取学生基本信息'''
        try:
            GPA.__ret["id"] = GPA.__table[0]        #学号
            GPA.__ret["name"] = GPA.__table[1]	    #姓名
            GPA.__ret["sex"] = GPA.__table[2]       #性别
            GPA.__ret["year"] = GPA.__table[3]		#年级
            GPA.__ret["collage"] = GPA.__table[4]	#学院
            GPA.__ret["major"] = GPA.__table[5]  	#专业
            GPA.__ret["Class"] = GPA.__table[6]	    #班级
            GPA.__ret["level"] = GPA.__table[8]     #层次
            GPA.__ret["stu_len"] = GPA.__table[9]   #学制
            GPA.__ret["foreign"] = GPA.__table[11]  #外语
            return 0
        except:
            logging.error("cannot get info of %s"%GPA.__num)
            return -1


    def __get_score_info(self):
        '''获取表格中的所有相关信息'''
        type=[]         #类别
        course = []     #课程名称
        credits = []    #学分
        score = []      #成绩
        score2 = []     #补考成绩
        second = []     #第二专业
        td = GPA.__table
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
        GPA.__ret['type']=type            #类别
        GPA.__ret['course']=course        #课程名称
        GPA.__ret['credits']=credits      #学分
        GPA.__ret['second']=second        #第二专业
        GPA.__ret['score']=score          #成绩
        GPA.__ret['score2']=score2        #补考成绩
        return 0

    def __score2number(self,text):
        '''将二级和五级成绩转换成数字成绩,或者将成绩转换成浮点型'''
        sc_dict={
            u'合格':60,
            u'不合格':0,
            u'优秀':95,
            u'优':95,
            u'良':84,
            u'良好':84,
            u'中等':73,
            u'中':73,
            u'及格':62,
            u'不及格':0,
            u'缺考':0,
            u'禁考':0,
            u'退学':0,
            u'缓考（时':0,
            u'缓考':0,
            u'休学':0,
            u'未选':0,
            u'作弊':0,
            u'取消':0,
            u'免修':60,
            '-':0,
            '':0
        }
        try:
            num = sc_dict[text]
            return num
        except:
            try:
                num = float(text)   
                return num
            except:
                logging.error("cannot change %s into number"%text)
                return -1
    
    def __calc_score(self):
        '''计算平均学分基点'''
        not_accept=[]       #没有通过
        totle_credits = 0   #总学分
        totle_score = 0     #总成绩
        ave_score = 0       #平均成绩
        type = GPA.__ret['type']
        course=GPA.__ret['course']        #课程名称
        credits=GPA.__ret['credits']      #学分
        score=GPA.__ret['score']          #成绩
        score2=GPA.__ret['score2']        #补考成绩
        set_course = []
        set_score = []
        set_credit = []
        i = 0
        all = len(type)
        while(i<all):
            if type[i]== u'公选课':   #公选课不计算成绩
                i+=1
                continue

            if credits[i]=='': #学分一项位空
                credits[i]='0'

            s = self.__score2number(score[i])   #将成绩五级成绩等转换成百分成绩
            s2 = self.__score2number(score2[i]) #将成绩五级成绩等转换成百分成绩
            if s > s2:
                max = s
            else:
                max = s2
            if course[i] in set_course:    #重修则只计算两次成绩的最大值
                position = set_course.index(course[i]) #获取这门课程在列表中的位置
                if max < 60: #重修成绩不足60分直接忽略
                    i += 1
                    continue
                if max >float(set_score[position]): #重修成绩比原来成绩高的话删除原来成绩，计算重修成绩
                    totle_credits -= float(set_credit[position])
                    totle_score -= float(set_score[position])*float(set_credit[position])
                    set_score[position] = max
                else:
                    i += 1
                    continue
            else:
                set_course.append(course[i])
                set_score.append(max)
                set_credit.append(credits[i])
            totle_credits+=float(credits[i])  #总学分
            if s<60:          #成绩小于60
                if s2 >= 60:
                    totle_score+=float(credits[i])*60 #补考通过为60分
                else:
                    not_accept.append(course[i])
            else:
                totle_score+=float(credits[i])*s
            i+=1

        if totle_credits==0: #总学分为0
            ave_score = 0
        else:
            ave_score = totle_score/totle_credits   #计算平均学分基点

        GPA.__ret['ave_score']=ave_score          #平均学分基点
        GPA.__ret['totle_score']=totle_score      #总成绩
        GPA.__ret['totle_credits']=totle_credits  #总学分
        GPA.__ret['not_accept']=not_accept        #至今未通过科目
        return 0

    def get_gpa(self):
        '''通过这个函数调用上面的函数'''
        self.__match_table()
        if self.__get_basic_info() == -1:
            raise errors.PageError('没有该学号的成绩信息')
        self.__get_score_info()
        self.__calc_score()
        return GPA.__ret



#if __name__=='__main__':
#    num = raw_input("请输入你的学号: ")
#    gpa = GPA(num)
#    info = gpa.get_gpa()
#    if info == -1:
#        print "error"
#    else:
#        print "学号\t\t姓名\t\t专业\t\t班级\t\t学分基点\t总基点\t\t总学分\t至今未通过科目"
#        print "%s\t%s\t%s\t%s\t%s\t\t%s\t\t%s\t%d"%(info['id'],info['name'],info['major'],info['Class'],info['ave_score'],info['totle_score'],info['totle_credits'],len(info['not_accept']))
