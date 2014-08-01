Got it
=========
校内信息查询平台

[http://gotit.asia](http://gotit.asia)

帮助使用校外网的同学使用正方教务系统， 以及计算学分绩点等其他功能。

##组件

+ 在线查询系统
+ Apis
+ 后台管理系统
+ 微信公众账号
+ 成绩推送服务

## 启动方式

    测试运行
    python test_run.py
    正式上线
    gunicorn gotit:application

## 安装依赖包

    pip install -r `requirement.txt`
    apt-get install python-lxml


## 需要的其他服务

  + redis
  + mongodb 
