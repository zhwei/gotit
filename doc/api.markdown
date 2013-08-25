# apis
## 成绩查询系统

### 使用方法

  1. **GET**:  先进行一次GET获取 `time_md5` 值(用户识别码), 用于区分不同的用户. 验证码链接为`http://gotit.asia/static/pic/**time_md5**.gif`,需要供用户识别并输入中文验证码, POST时需要提供, 注意:验证码图片会在五分钟后被删除

  1. **POST**: POST的数据有: 学号, 密码, 查询种类(最新成绩, 本学期课表, 考试时间), 中文验证码(utf-8), `time_md5`

### url 

  [**http://gotit.asia/api/score**](http://gotit.asia/api/score)

### 支持的方法:

        GET + POST

### POST参数

        xh        #学号
        pw        #密码
        time_md5  #用户识别码(之前得到的
        verify    #验证码(用户识别后的中文验证码, 两位汉字)
        t         #查询种类

#### t值对应查询种类

            值      查询内容

            1       最新成绩
            2       考试时间 (json格式错误, 暂时不能使用)
            3       本学期课表 (json格式错误, 暂时不能使用)

### 返回值(utf-8)

        **正常返回值**
        {"科目1":"成绩1",...,...}
        正常

        **错误类型**
        {"error":"can not find target time_md5"}
        time_md5值错误
        {"error":"password wrong"}
        密码错误
        {"error":"verify code wrong"}
        验证码错误
        {"error":"server is sleeping ... "}
        服务端挂起
        {"error":"can not find your t"}
        查询类型错误
        {"error":"can not find your contents"}
        无法匹配该用户的内容

## 四六级最新成绩查询

### url

[**http://gotit.asia/api/cet**](http://gotit.asia/api/cet)

### 支持的方法:  
        POST

### 参数
      nu		#准考证号
      name		#姓名

### 返回值  
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
        
####尚无成绩

      {'error': u'\u5c1a\u65e0\u6210\u7ee9!'}  

## 学分绩点查询

### url

[http://gotit.asia/api/gpa](http://gotit.asia/api/gpa)

### 支持的方法:

      POST

### 参数:  

     xh		#学号

### 返回值:
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
        
