程序开发管理系统配置说明
======
**1、运行环境以及依赖**
------
    1、centos
    2、gunicorn
    3、直接百度怎么在centos搭建flask系统运行环境
    4、requirements.txt中的包
**2、数据库连接配置**
------
    1、在flasky目录下新建config.ini文件
    2、文件中的信息格式（忽略注释信息）：
        #程序主数据库连接
        [MySql]
        host=192.168.80.xxx   #IP
        user=xxx              #用户名
        password=xxx          #密码
        db=xxx                #数据库名称
        charset=utf8          #字符集
        
        #程序副数据库连接用来从周报系统中获取订单信息
        [ManPower]
        host=192.168.80.xxx   #IP
        user=xxx              #用户名
        password=xxxx         #密码
        db=xxxxxxxxx          #SID
        
        [Email]
        address=xxxxxx@xxxx.com.cn  #用户注册时邮件发送所用的邮箱
        password=xxxxxx             #邮箱密码
        admin_email=xxxxx@xxxx.com  #管理员邮箱，意义不大
        
        [SLIMS]               #系统与SLISM系统进行数据交互的Web Service
        address=http://192.168.80.xxx:45016/ammic2slmsservice.asmx?WSDL
    3、日志文件
        1、在flasky目录下新建文件夹logs，然后logs文件中新建error.log和info.log
    4、各种静态文件保存文件夹
        1、这种文件夹会自动新建
        2、别问logs文件夹为什么不自动新建，问就是反手一巴掌
**3、程序常用命令**
------
    1、. venv/bin/activate   #启动虚拟环境
    2、ps -ef|grep gun       #查看gunicorn用到的进程  gun即gunicorn缩写，可以不写全部
    3、kill xxxx             #xxxx为进程ID
    4、nohub gunicorn -w 10 -b 0.0.0.0:5000 flasky:app &   #参数信息不明白自己百度；nohub...&表示可以后台运行
    5、gunicorn -w 10 -b 0.0.0.0:5000 flasky:app           #不是后台运行；使用上一个就好
    6、还有一些git的命令，拉取程序时使用