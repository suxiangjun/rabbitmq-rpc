## 项目名称：rabbitMQ-RPC

*本软件只在python3环境下运行，经过测试window，Linux都正常运行。*

#### 实现功能

1.可以对指定机器异步的执行多个命令
例子：

>:run "df -h" --hosts 192.168.5.133
>task id: 45334
>: check 45334
>

2.每执行一条命令，即立刻生成一个任务ID,不需等待结果返回，通过命令check_task TASK_ID来得到任务结果

#### 程序架构

```php+HTML
├──rabbitMQ-rpc               
│      │──bin             	           
│      │   ├──rabbitmq_rpc.py      #  rabbitmq_rpc执行程序   
│      │   └──__init__.py
│      │──conf                       
│      │   ├──setting.py           #  配置文件
│      │   └──__init__.py
│      │──core                     #  主程序文件        
│      │   ├──main.py           
│      │   └──__init__.py
│      │──作业截图                  # 作业截图存放路径
│      └──rabbitmq_server.py        # 远程服务端执行文件
│                  
│──README
```

`使用说明：`   ​  b 退出程序

[博客地址]: http://www.cnblogs.com/xiangjun555

