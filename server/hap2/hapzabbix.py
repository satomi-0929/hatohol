#! /usr/bin/env python
# coding: UTF-8

import daemon
import json
import multiprocessing

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
	def callback_handler(self):
		print "Not implement"


class HAPZabbixRabbitMQPublisher(haplib.RabbitMQPublisher):
    def routine_update(self):
        print "Not implement"


if __name__ == '__main__':
	with daemon.DaemonContext():
		hap_zabbix_daemon = HAPZabbixDaemon
    main()
