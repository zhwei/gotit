Got it
=========
校内信息查询平台  

[http://gotit.asia](http://gotit.asia)

启动前需要启动`redis`

启动方式

    gunicorn code:application

测试启动

    python test_run.py

#### 依赖包

+ web.py
+ jinja2
+ redis


#### install redis


    $ wget http://download.redis.io/releases/redis-2.6.16.tar.gz
    $ tar xzf redis-2.6.16.tar.gz
    $ cd redis-2.6.16
    $ make

