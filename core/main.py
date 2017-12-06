#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author__ = "Junesu"
import pika,uuid,time,sys,threading
from conf import setting
import pika, uuid, time
#用生成式获取任务ID
tast_ids=( i for i in range(100,1000))

queue_dic={
    "tast_id":[]  #任务ID 返回的队列
}

class RpcClient(object):
    "rpc客户端"
    def __init__(self,):
        credentials = pika.PlainCredentials(setting.username, setting.password)
        # 连接信息
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            setting.rabbitmq_ip, setting.port, '/', credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange="direct_cmd",
                                 exchange_type="direct")
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response,
                                   queue=self.callback_queue)
    def on_response(self, ch, method, props, body):
        self.response = None
        if self.tast_id == props.correlation_id:  # 我发过去的结果就是我想要的结果，保持数据的一致性
            queue_dic[self.tast_id].append(eval(body.decode()))
            self.response=1
            ch.basic_ack(delivery_tag=method.delivery_tag)#回复收到消息
    #群发消息
    def call(self,cmd_dic):
        self.tast_id =cmd_dic["tast_id"]
        queue_dic[self.tast_id] = list()
        for host in cmd_dic["hosts"]: #
            self.response = None
            self.severity =host
            self.channel.publish(exchange="direct_cmd",
                                 routing_key=self.severity,
                                 properties=pika.BasicProperties(
                                     reply_to=self.callback_queue,
                                     correlation_id=self.tast_id),
                                 body=cmd_dic["cmd"].encode())
            while self.response is None:
                self.connection.process_data_events()  # 非阻塞版的start_consumer()
                time.sleep(0.5)
        return queue_dic[self.tast_id]

class Rabbit_client():
    #执行指令
    def __init__(self):
        self.help='''eg:
1.\033[1;35mrun "df -h" --hosts 192.168.5.133\033[0m
2.\033[1;35mcheck task'id\033[0m'''

    def cmd_run(self,cmd_dic):
        rpc_client = RpcClient()
        response = rpc_client.call(cmd_dic)

    #通过ID查看任务
    def chect_task(self,cmd_dic):
        data=queue_dic[cmd_dic["task_id"]]
        print("task:\033[1;35m{}\033[0m".format(cmd_dic["task_id"]))
        for d in data:
            print('''information:
\033[1;35m{}\033[0m'''.format(d[0].center(50,"-")))
            print("\033[1;32m{}\033[0m".format(d[1]))

    #细分用户指令
    def cmd_hosts(self,cmd):
        if cmd.startswith("run"):
            cmd_dic = {
                "cmd": eval(" ".join(cmd.strip().split("--hosts")[0].split()[1:])) ,
                "hosts": cmd.strip().split("--hosts")[1].split(),
                "action": cmd.strip().split("--hosts")[0].split()[0]
            }
        elif cmd.startswith("check"):
            cmd_dic = {
                "cmd": cmd,
                "task_id":cmd.strip().split()[1],
                "action": "check"
            }
        return cmd_dic

    def run(self):
        while True:
            try:
                cmd = input("[{}]#".format("admin"))
                if cmd==0:continue
                elif cmd=="q":break
                if cmd.startswith("run") or cmd.startswith("check"):
                    cmd_dic=self.cmd_hosts(cmd)
                    if cmd_dic["action"]=="run":
                        tast_id = str(tast_ids.__next__())#生成任务ID
                        cmd_dic["tast_id"]=tast_id
                        t = threading.Thread(target=self.cmd_run, args=(cmd_dic,))
                        t.start()
                        print("The ID of this task is:\033[1;35m[{}]\033[0m".format(tast_id))
                    elif  cmd_dic["action"]=="check":
                        self.chect_task(cmd_dic)
                else:
                    print(self.help)
            except (SyntaxError,NameError,IndexError) as e:
                print(self.help)
                continue
            except KeyError as e:
                print("\033[1;31m The task is no existent or Just a moment, please!\033[0m")
my_task=Rabbit_client()
