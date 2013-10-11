Got it
=========
校内信息查询平台  

[http://gotit.asia](http://gotit.asia)

## 启动

启动前需要启动`redis`

启动方式

    gunicorn code:application

测试启动

    python test_run.py

## 运行环境
### 依赖包

+ web.py
+ jinja2
+ redis
+ gunicorn


### redis


    $ wget http://download.redis.io/releases/redis-2.6.16.tar.gz
    $ tar xzf redis-2.6.16.tar.gz
    $ cd redis-2.6.16
    $ make

## License

The MIT License (MIT)

Copyright (c) 2013 zhwei

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
