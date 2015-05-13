#! /usr/bin/env python
# coding: UTF-8

import daemon
import json
import multiprocessing
import argparse

import haplib
import zabbixapi

class HapZabbixProcedures(haplib.BaseProcedures):
    def exchangeProfile(self, params):
        haplib.optimize_server_procedures(self.valid_procedures_of_server, params)
        my_procedures = haplib.get_implement_procedures(HapZabbixProcedures)
        push_profile("response", my_procedures)


    def fetchItems(self):
        print "Not implement"


    def fetchHistory(self):
        print "Not implement"


    def fetchTriggers(self):
        print "Not implement"


    def fetchEvents(self):
        print "Not implement"


class PreviousHostsInfo:
    def __init__():
        self.hosts = list()
        self.host_groups = list()
        self.host_group_membeship = list()


class HAPZabbixRabbitMQConsumer(haplib.RabbitMQConsumer):
    def __init__(self, host, port, queue_name, user_name, user_password, queue):
        RabbitMQConsumer.__init__(self, host, port, queue_name, user_name, user_password)
        self.queue = queue

    def callback_handler(self):
        print "Not implement"


class HAPZabbixRabbitMQPublisher(haplib.RabbitMQPublisher):
    def __init__(self, host, port, queue_name, user_name, user_password, queue):
        RabbitMQPublisher.__init__(self, host, port, queue_name, user_name, user_password)
        self.queue = queue
        ms_dict = self.get_monitoring_server_info()
        self.ms_info = haplib.MonitoringServerInfo(ms_dict)

    def routine_update(self):
        print "Not implement"


class HAPZabbixDaemon:
    def __init__(self, host, port, queue_name, user_name, user_password):
        self.host = host
        self.port = port
        self.queue_name = queue_name
        self.user_name = user_name
        self.user_password = user_password


    def start(self):
        queue = multioprocessing.Queue()
        consumer = HAPZabbixRabbitMQConsumer(self.host, self.port, "c_" + self.queue_name,
                                             self.user_name, self.user_password, queue)
        subprocess = multiprocessing.Process(target = consumer.start_receiving)
        subprocess.daemon = True
        subprocess.start()

        publisher = HAPZabbixRabbitMQPublisher(self.host, self.port, "p_" + self.queue_name,
                                               self.user_name, self.user_password, queue)
        publisher.routine_update()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",
                        dest="host",
                        type=str,
                        default="localhost",
                        help="RabbitMQ host")
    parser.add_argument("--port",
                        dest="rabbitmq_port",
                        type=int,
                        default=None,
                        help="RabbitMQ port")
    parser.add_argument("--user_name",
                        dest="user_name",
                        type=str,
                        required=True,
                        help="RabbitMQ host user name")
    parser.add_argument("--user_password",
                        dest="user_password",
                        type=str,
                        required=True,
                        help="RabbitMQ host user password")
    parser.add_argument("--queue",
                        dest="queue_name",
                        type=str,
                        required=True,
                        help="RabbitMQ queue")
    args = parser.parse_args()

    with daemon.DaemonContext():
        hap_zabbix_daemon = HAPZabbixDaemon(args.host, args.port, args.queue_name,
                                            args.user_name, args.user_password)
        hap_zabbix_daemon.start()
