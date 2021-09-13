# 1. Background
* 该工具基于 Python3.8 + Django 框架开发，目前可以实现更改端口VLAN、根据MAC/IP定位设备、绑定或者解绑IP/MAC以及一些常用命令行操作。
* 常用命令行操作、更改端口VLAN：通过直接登录相应的交换机进行操作。
* 绑定或者解绑IP/MAC：在核心交换机操作。
* 根据MAC/IP定位设置：如下图所示，首先在核心上查找到目标所在的端口，也即找到对应汇聚交换机，然后在汇聚交换机找到对应的接入交换机，最后找到所在的端口（需要根据实际网络拓扑，修改 HexinCaozuo.py、JiaohuanjiCaozuo.py、locate_item.py 中交换机列表以及各端口连接信息）。
![](https://github.com/easonlis/SwitchAdmin/blob/master/static/screenshort/example.png)
# 2. Install
* 安装相关库
```
pip3 install -r requirements.txt
```
* Mysql 配置

先创建数据库
```
CREATE DATABASE IF NOT EXISTS SwitchAdmin CHARACTER SET = 'utf8';
```
在 setting.py 配置对应的数据库连接参数
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'SwitchAdmin', 
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USER': 'sa',
        'PASSWORD': '123456',
    }
}
```
* 迁移 Django 数据库到 Mysql
```
python3 manage.py migrate
```
* 创建管理用户
```
python3 manage.py createsuperuser
```
* 现在可以尝试运行了
```
python3 manage.py runserver 127.0.0.1:80
```
* 最后使用 Nginx+uwsgi 稳定运行该工具

Nginx 配置
```
server {
    listen         80; 
    server_name    127.0.0.1 
    charset UTF-8;
    access_log      /var/log/nginx/SwitchAdmin_access.log;
    error_log       /var/log/nginx/SwitchAdmin_err.log;

    client_max_body_size 75M;

    location / { 
        include uwsgi_params;
        uwsgi_pass 127.0.0.1:8000;
        uwsgi_read_timeout 60;
    }   
    location /static {
        expires 30d;
        autoindex on; 
        add_header Cache-Control private;
        alias /var/www/SwitchAdmin/static/; #需要指向静态资源所在目录
     }
 }
```
supervisor 配置
```
[program:switchcontroller]
directory=/usr/local/bin
command=uwsgi --ini /var/www/SwitchAdmin/uwsgi.ini #uwsgi配置所在位置

user=root
autostart=true
autorestart=true
startsecs=1
```
# 3. Screenshot
![](https://github.com/easonlis/SwitchAdmin/blob/master/static/screenshot/dashboard.PNG)

![](https://github.com/easonlis/SwitchAdmin/blob/master/static/screenshot/changevlan.png)

![](https://github.com/easonlis/SwitchAdmin/blob/master/static/screenshot/locate.png)

![](https://github.com/easonlis/SwitchAdmin/blob/master/static/screenshot/bind.PNG)

![](https://github.com/easonlis/SwitchAdmin/blob/master/static/screenshot/command.png)
