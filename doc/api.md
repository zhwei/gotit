# apis
* * *
## 成绩查询系统
+ url: http://gotit.asia/api/score
+ 支持的方法:
	POST
+ 参数
	xh		#学号
	pw		#密码
+ 返回值
	{"科目1":"成绩1",...,...}
	
	若为空则其用户名或密码错误

## 四六级最新成绩查询
+ url: http://gotit.asia/api/cet
+ 支持的方法:
	POST
+ 参数
	nu		#准考证号
	name	#姓名
+ 返回值
	成绩公布(有可能是上一次成绩)
	{
		"num":      考号，字符串,
		"name":     姓名,字符串,
		"school":   学校，字符串
		"type":     类型（四级还是六级），字符串
		"time":     考试时间,字符串
		"total":    总分,字符串
		"listen":   听力成绩,字符串
		"read":     阅读成绩,字符串
		"mix":      综合成绩,字符串
		"write":    写作成绩,字符串
	}
	尚无成绩
	{'error': u'\u5c1a\u65e0\u6210\u7ee9!'}
## 学分绩点查询
+ url: http://gotit.asia/api/gpa
+ 支持的方法:
	POST
+ 参数:
	xh		#学号
+ 返回值:
    {
        "id":           学号,字符串
        "name":         姓名,字符串
        "sex":          性别,字符串
        "year":         年级,字符串
        "collage":      学院,字符串
        "major":        专业,字符串
        "Class":        班级,字符串
        "stu_len":      学制,字符串
        "level":        层次,字符串
        "foreign":      外语,字符串
        "type":         课程类别，列表（每门课程的类别）
        "course":       课程名称,列表(每门课程的名称)
        "credits":      学分,列表(每门课程的学分)
        "score":        成绩,列表(每门课程的成绩)
        "score2":       补考成绩,列表(每门课程的补考成绩)
        "second":       是否是第二专业,列表
        "ave_score":    平均学分基点,浮点数
        "totle_score":  总成绩,浮点数
        "totle_credits":总学分,浮点数
        "not_accept":   至今未通过科目,列表
    }
