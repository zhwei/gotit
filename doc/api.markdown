# Gotit 开放接口文档

+ _更新时间: 2014-04-15_  
+ _数据格式均为`JSON`_  

+ 接口说明:  
    1. 由于中文验证码的存在, 接口或许有点另类, 希望见谅.  
    2. 验证类接口需要登录后才能使用, 如果仅查询单项信息推荐使用下面的成绩类或课表类接口  
    3. 希望开发者在使用接口前先通过<a href="mailto:zhwei@gotit.asia">邮件</a>联系作者, 如果有很好的建议或者哪些地方不理解也可以通过邮件联系.  

## 验证类

### 登录
+ 功能  
登录后可以直接获取下面所有接口的结果, 仅需要提供用户识别码(UID)
+ 接口地址  
[/user/login.json](http://api.gotit.asia/user/login.json)
+ 请求方式  
`GET` + `POST`  
    + 使用说明  
        1. **GET**:  先进行一次GET获取 `UID` 值(用户识别码), 用户的唯一标识. 
        2. 通过`UID`获取验证码, 验证码链接为`http://api.gotit.asia/zheng/checkcode?=[UID]`.
        3.  **POST**: POST的数据有: 学号, 密码, 中文验证码(utf-8), 用户识别码`UID`

    + GET 结果示例

    ```json

        {
            "status": {
                "code": 200,
                "message": "Success",
            },
            "data": {
                "uid": "user_067e11ac790844c08e068c96fb5b023b"
            }
        }
    ```
    + POST 示例

    参数: `data`

    ```json

        {
            "uid": "user_067e11ac790844c08e068c96fb5b023b",
            "xh": "1111123456",
            "pw": "password",
            "verify": "疫讨",
        }
    ```

+ 返回值示例

```json

    {
        {
            "status": {
                "code": 200,
                "message": "Login Success",
            },
            "data": {
                "uid": "user_067e11ac790844c08e068c96fb5b023b"
            }
        }
    }
```

### 查询接口列表(需登录)
_下面表格中接口请求方式与请求数据相同_  
+ 请求方式  
`POST`
+ 请求数据  
参数: data
```json

    {
        "uid": "user_067e11ac790844c08e068c96fb5b023b"
    }
```
+ 返回值  
返回值与下方对应内容相同

+ 注意  
_登录状态在完成**最后一次查询操作**五分钟后失效_

+ 接口列表

<table>
    <thead>
        <tr>
            <th>接口名称</th>
            <th>接口地址</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>当前学期成绩</td>
            <td><a href="http://api.gotit.asia/user/score/current_semester.json">/user/score/current_semester.json</a></td>
        </tr>
        <tr>
            <td>全部成绩</td>
            <td><a href="http://api.gotit.asia/user/score/all.json">/user/score/all.json</a></td>
        </tr>
        <tr>
            <td>学分绩点</td>
            <td><a href="http://api.gotit.asia/user/score/gpa.json">/user/score/gpa.json</a></td>
        </tr>
        <tr>
            <td>往年四六级成绩</td>
            <td><a href="http://api.gotit.asia/user/score/former_cet.json">/user/score/former_cet.json</a></td>
        </tr>
        <tr>
            <td>当前学期课表</td>
            <td><a href="http://api.gotit.asia/user/timetable/current_semester.json">/user/timetable/current_semester.json</a></td>
        </tr>
        <tr>
            <td>当前学期课表(原始html)</td>
            <td><a href="http://api.gotit.asia/user/timetable/current_semester/raw.json">/user/timetable/current_semester/raw.json</a></td>
        </tr>
    </tbody>
</table>

## 成绩类

### 当前学期成绩

+ 功能  
查询当前学期成绩, 跟随正方教务系统, 实时获取.
+ 接口地址  
[/score/current_semester.json](http://api.gotit.asia/score/current_semester.json)
+ 支持格式  
JSON  
+ 请求方式  
`GET` + `POST`  
    + 使用说明  
        1. **GET**:  先进行一次GET获取 `UID` 值(用户识别码), 用户的唯一标识. 
        2. 通过`UID`获取验证码, 验证码链接为`http://api.gotit.asia/zheng/checkcode?=[UID]`.
        3.  **POST**: POST的数据有: 学号, 密码, 中文验证码(utf-8), 用户识别码`UID`

    + GET 结果示例

    ```json

        {
            "status": {
                "code": 200,
                "message": "Success",
            },
            "data": {
                "uid": "user_067e11ac790844c08e068c96fb5b023b"
            }
        }
    ```
    + POST 示例

    参数: `data`

    ```json

        {
            "uid": "user_067e11ac790844c08e068c96fb5b023b",
            "xh": "1111123456",
            "pw": "password",
            "verify": "疫讨",
        }
    ```


+ 返回值示例

```json

    {
        {
            "status": {
                "code": 200,
                "message": "Login Success",
            },
             "data": {
                "大学英语": "60",
                "大学物理": "99",
                \\ ...
            }
        }
    }
```

### 全部成绩

+ 功能  
查询入学以来全部成绩, 包括补考成绩
+ 接口地址  
[/score/all.json](http://api.gotit.asia/score/all.json)
+ 请求方式  
`GET` + `POST`  
    + 使用说明  
        1. **GET**:  先进行一次GET获取 `UID` 值(用户识别码), 用户的唯一标识. 
        2. 通过`UID`获取验证码, 验证码链接为`http://api.gotit.asia/zheng/checkcode?=[UID]`.
        3.  **POST**: POST的数据有: 学号, 密码, 中文验证码(utf-8), 用户识别码`UID`

    + GET 结果示例

    ```json

        {
            "status": {
                "code": 200,
                "message": "Success",
            },
            "data": {
                "uid": "user_067e11ac790844c08e068c96fb5b023b"
            }
        }
    ```
    + POST 示例

    参数: `data`

    ```json

        {
            "uid": "user_067e11ac790844c08e068c96fb5b023b",
            "xh": "1111123456",
            "pw": "password",
            "verify": "疫讨",
        }
    ```

+ 返回值示例

```json

    {   
        "status" : {
            "code": 200,
            "message": "Success"
        },
        "data" : {
            "大学物理":{
                "initial": "90", // 原考成绩
                "makeup": ""     // 补考成绩
            },
            "大学英语":{
                "initial": "59.8",
                "makeup": "60"
            }
        }
    }
```

### 绩点

+ 功能  
查询学分绩点
+ 接口地址  
[/score/gpa.json](http://api.gotit.asia/score/gpa.json)
+ 请求方式  
`POST`
    - 请求数据示例  
    参数: data

    ```json

        {
            "xh":"1111123456"
        }
    ```

### 往年四六级成绩

+ 功能  
查询往年四六级成绩
+ 接口地址
[/score/former_cet.json](http://api.gotit.asia/score/former_cet.json)
+ 请求方式  
`POST`
    - 请求数据示例  
    参数: data

    ```json

        {
            "xh":"1111123456"
        }
    ```
## 课表类

### 当前学期课表

+ 功能  
查询当前学期课表, 跟随正方教务系统, 实时获取.
+ 接口地址  
[/timetable/current_semester.json](http://api.gotit.asia/timetable/current_semester.json)
+ 请求方式  
`GET` + `POST`  
    + 使用说明  
        1. **GET**:  先进行一次GET获取 `UID` 值(用户识别码), 用户的唯一标识. 
        2. 通过`UID`获取验证码, 验证码链接为`http://api.gotit.asia/zheng/checkcode?=[UID]`.
        3.  **POST**: POST的数据有: 学号, 密码, 中文验证码(utf-8), 用户识别码`UID`

    + GET 结果示例

    ```json

        {
            "status": {
                "code": 200,
                "message": "Success",
            },
            "data": {
                "uid": "user_067e11ac790844c08e068c96fb5b023b"
            }
        }
    ```
    + POST 示例

    参数: `data`

    ```json

        {
            "uid": "user_067e11ac790844c08e068c96fb5b023b",
            "xh": "1111123456",
            "pw": "password",
            "verify": "疫讨",
        }
    ```

+ 返回值示例

```json

        [
            {
                "location": "西3101",
                "name": "媒体策划与数字编辑",
                "plan": "周一第7,8节{第10-10周}|双周", \\（原始字符串，用于检测解析是否准确）
                "teacherName": "鞠英辉",
                "dayOfWeek": "周一",
                "oddEvenFlag": 0,       \\（单周为1，双周为2，不分单双周为0）
                "sectionFrom": "7",     \\（节次开始）
                "sectionTo": "9",       \\（节次结束）
                "weekFrom": "2",        \\（开始上课周次）
                "weekTo": "12 "         \\（结束上课周次）
            },
            \\ ...
        ]
```

### 当前学期课表(原始html)

+ 功能  
查询当前学期课表, 跟随正方教务系统, 实时获取, 返回值为从正方教务系统通过正则表达式得出的原始html, 未经任何处理.
+ 接口地址  
[/timetable/raw/current_semester.json](http://api.gotit.asia/timetable/current_semester/raw.json)
+ 请求方式  
`GET` + `POST`  
    + 使用说明  
        1. **GET**:  先进行一次GET获取 `UID` 值(用户识别码), 用户的唯一标识. 
        2. 通过`UID`获取验证码, 验证码链接为`http://api.gotit.asia/zheng/checkcode?=[UID]`.
        3.  **POST**: POST的数据有: 学号, 密码, 中文验证码(utf-8), 用户识别码`UID`

    + GET 结果示例

    ```json

        {
            "status": {
                "code": 200,
                "message": "Success",
            },
            "data": {
                "uid": "user_067e11ac790844c08e068c96fb5b023b"
            }
        }
    ```
    + POST 示例

    参数: `data`

    ```json

        {
            "uid": "user_067e11ac790844c08e068c96fb5b023b",
            "xh": "1111123456",
            "pw": "password",
            "verify": "疫讨",
        }
    ```

+ 返回值示例

```json

    {
        {
            "status": {
                "code": 200,
                "message": "Success",
            },
            "data": {
                "raw": "<tr>......<tr>",
            }
        }
    }
```
