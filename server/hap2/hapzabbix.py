#! /usr/bin/env python
# coding: UTF-8

import daemon
import json
import multiprocessing
import argparse

import haplib
import zabbixapi

class HapZabbixProcedures(haplib.PluginProcedures):
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
        self.api = zabbixapi.ZabbixAPI(self.ms_info)
        self.previous_hosts_info = PreviousHostsInfo()
        self.trigger_last_info = None
        self.event_last_info = None


    def put_items(self, host_id = None, fetch_id = None):
        params = {"items": self.api.get_items(host_id)}
        if fetch_id is not None:
            params["fetchId"] = fetch_id

        request_id = haplib.get_request_id()
        self.send_request_to_queue("putItems", params, request_id)

        haplib.get_response_and_check_id(self.queue, request_id)


    def put_history(self, item_id, fetch_id):
        params = {"itemId": item_id, "histories": self.api.get_history(item_id),
                  "fetchId": fetch_id}

        request_id = haplib.get_request_id()
        self.send_request_to_queue("putHistory", params, request_id)

        haplib.get_response_and_check_id(self.queue, request_id)


    def update_hosts_and_host_group_membership(self, previous_hosts, previous_host_group_membership):
        hosts, hg_membership = self.api.get_hosts()

        hosts.sort()
        if previous_hosts != hosts:
            hosts_params = {"updateType": "ALL", "hosts": hosts}
            request_id = haplib.get_request_id()
            self.send_request_to_queue("updateHosts", params, request_id)
            haplib.get_response_and_check_id(self.queue, request_id)
            previous_hosts = hosts

        hg_membership.sort()
        if previous_host_group_membership != hg_membership:
            hg_membership_params = {"updateType": "ALL", "hostGroupMembership": hg_membership}
            request_id = haplib.get_request_id()
            self.send_request_to_queue("updateHostGroupMembership", params, request_id)
            haplib.get_response_and_check_id(self.queue, request_id)
            previous_host_group_membership = hg_membership


    def update_host_groups(self, previous_host_groups)
        host_groups = api.get_host_groups()
        host_groups.sort()
        if previous_host_groups != host_groups:
            hosts_params = {"updateType": "ALL", "hostGroups": host_groups}
            request_id = haplib.get_request_id()
            self.send_request_to_queue("updateHostGroups", params, request_id)
            haplib.get_response_and_check_id(self.queue, request_id)
            previous_host_groups = host_groups


    def update_triggers(self, requests_since = None, host_id = None, fetchId = None)
        if self.trigger_last_info is None:
            self.trigger_last_info = self.get_last_info("trigger")

        triggers = self.api.get_triggers(self.trigger_last_info, host_id)
        self.trigger_last_info = haplib.find_last_info_from_dict_array(triggers, "lastChangeTime")

        params = {"triggers": triggers, "updateType": "UPDATED",
                  "lastInfo": self.trigger_last_info}

        if fetch_id is not None:
            params["fetchId"] = fetch_id
            params["updateType"] = "ALL"

        request_id = haplib.get_request_id()
        self.send_request_to_queue("updateTriggers", params, request_id)

        haplib.get_response_and_check_id(self.queue, request_id)


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
