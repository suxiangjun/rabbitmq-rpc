#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author = "susu"
import pika, sys,os
import pika
credentials = pika.PlainCredentials('junesu', '123456')
connection = pika.BlockingConnection(pika.ConnectionParameters(
    '192.168.5.132', 5672, '/', credentials))
channel = connection.channel()
channel.exchange_declare(exchange="direct_cmd",
                              exchange_type="direct")
queue_name="192.168.5.131"
result = channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange="direct_cmd",
                   queue=queue_name,
                   routing_key=queue_name)
def run_cmd(cmd):
    if os.system(cmd.decode()):
        cmd_res="[{}] is not exist".format(cmd.decode())
    else:
        cmd_res = os.popen(cmd.decode()).read()
    return str([queue_name,cmd_res]).encode()
def on_request(ch, method, props, body):
    cmd = body
    print(" [.] fib(%s)" % cmd)
    response = run_cmd(cmd)
    ch.basic_publish(exchange="",
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=\
                                                         props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag=method.delivery_tag)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue=queue_name)
print(" [x] Awaiting RPC requests")
channel.start_consuming()