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

![](https://github.com/easonlis/SwitchAdmin/blob/master/static/screenshort/dashboard.PNG)
![](https://github.com/easonlis/SwitchAdmin/blob/master/static/screenshort/bind.PNG)
