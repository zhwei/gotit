# 部署gotit

## 安装依赖包

    pip install web.py jinja2 PIL


## 测试运行

    python test_run.py

此处依赖django的相关模块


## 启动

将doc中的`gotit`文件复制到`/etc/init.d/`, 可以通过

    sudo service gotit start

启动


## 停止

    sudo kill `cat /var/run/gunicorn.pid`
