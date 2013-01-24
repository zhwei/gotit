# 正方教务系统查询工具
* * *  
### 实现方法
使用`urllib2`模拟登录,然后使用`BeaufitualSoup`解析出所需的表格内容. 登录难点是`url`中有一段随机字符串,需要先将其匹配出来获得`base_url`, 一开始时是每一次登录都匹配一次该随机字符串,也就是说查询一次成绩程序要访问两次正方教务系统, 现在使用了马伟伟同学写的`cache`模块,每500秒获取一次该字符串,提高了成绩查询速度.另一个就是模拟登录时的`post`内容中有一个`VIEWSTATE`值, 类似与`csrf_token`吧, 登录时需要先抓取该值然后`post`.  

### 该类中的方法  
+ `initlog`  初始化日志模块  
+ `__get_base_url()`  获取基础`url`,返回值类似`http://210.44.176.133/(mncumtmnxzhoz4550kr2qjnf)/`  
+ `cache_url()`  用来缓存`base_url`以提高成绩查询效率, 500秒更新一次`base_url`.
+ `__get_login_url` and `__get_url()`  用来获取需要查询信息的`url`
+ `login()` 实现登录功能,登录成功时返回`opener`,登录失败时返回`None`
+ `get_table()`  真正用来获取需要查询的信息.
