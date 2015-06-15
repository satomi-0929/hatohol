#!/usr/bin/env python
"""
  Copyright (C) 2015 Project Hatohol

  This file is part of Hatohol.

  Hatohol is free software: you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License, version 3
  as published by the Free Software Foundation.

  Hatohol is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with Hatohol. If not, see
  <http://www.gnu.org/licenses/>.
"""

import haplib
import multiprocessing
import transporter
import argparse
import logging

class DummyServer:

    def __init__(self, transporter_args):
        self.__sender = haplib.Sender(transporter_args)
        self.__rpc_queue = multiprocessing.JoinableQueue()
        self.__dispatcher = haplib.Dispatcher(self.__rpc_queue)
        self.__dispatcher.daemonize();

        self.__handler_map = {
          "getMonitoringServerInfo": self.__rpc_get_monitoring_server_info,
          "putHosts": self.__rpc_put_hosts,
          "putHostGroups": self.__rpc_put_host_groups,
          "putHostGroupMembership": self.__rpc_put_host_group_membership,
          "putTriggers": self.__rpc_put_triggers,
          "putEvents": self.__rpc_put_events}

        # launch receiver process
        dispatch_queue = self.__dispatcher.get_dispatch_queue()
        self.__receiver = haplib.Receiver(transporter_args, dispatch_queue,
                                          self.__handler_map.keys())
        self.__receiver.daemonize()

    def __call__(self):
        while True:
            pm = self.__rpc_queue.get()
            if pm.error_code is not None:
                logging.error(pm.get_error_message())
                continue
            request = pm.message_dict
            method = request["method"]
            params = request["params"]
            logging.info("method: %s" % method)
            call_id = request["id"]
            self.__handler_map[method](call_id, params)

    def __rpc_get_monitoring_server_info(self, call_id, params):
        result = {
            "extendedInfo": "exampleExtraInfo",
            "serverId": 1,
            "url": "http://example.com:80",
            "type": 0,
            "nickName": "exampleName",
            "userName": "Admin",
            "password": "examplePass",
            "pollingIntervalSec": 30,
            "retryIntervalSec": 10
        }
        self.__sender.response(result, call_id)

    def __rpc_put_hosts(self, call_id, params):
        logging.info(params)
        # TODO: Parse content
        result = "SUCCESS"
        self.__sender.response(result, call_id)

    def __rpc_put_host_groups(self, call_id, params):
        logging.info(params)
        # TODO: Parse content
        result = "SUCCESS"
        self.__sender.response(result, call_id)

    def __rpc_put_host_group_membership(self, call_id, params):
        logging.info(params)
        # TODO: Parse content
        result = "SUCCESS"
        self.__sender.response(result, call_id)

    def __rpc_put_triggers(self, call_id, params):
        logging.info(params)
        # TODO: Parse content
        result = "SUCCESS"
        self.__sender.response(result, call_id)

    def __rpc_put_events(self, call_id, params):
        logging.info(params)
        # TODO: Parse content
        result = "SUCCESS"
        self.__sender.response(result, call_id)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Dummy Server for HAPI 2.0")
    parser = argparse.ArgumentParser()
    haplib.Utils.define_transporter_arguments(parser)

    args = parser.parse_args()
    transporter_class = haplib.Utils.load_transporter(args)
    transporter_args = {"class": transporter_class}
    transporter_args.update(transporter_class.parse_arguments(args))
    transporter_args["amqp_send_queue_suffix"] = "-T"
    transporter_args["amqp_recv_queue_suffix"] = "-S"
    server = DummyServer(transporter_args)
    server()
