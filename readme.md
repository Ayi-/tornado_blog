# Tornado Blog
基于`Python2.7`和`Tornado`框架搭的一个小博客

创建一个`database`

`create database blog character set utf8;`

导入`blog.sql`MySQL数据库。

`mysql -uroot -p blog < blog.sql`

安装模块

`pip install -r requirement.txt`

启动应用

`python run.py --port=8000 --mysqlhost=192.168.1.2 --mysqlport=3306 --mysqldatabase=blog --mysqluser=root --mysqlpassword=xxxxxx`