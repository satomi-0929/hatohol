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

class DummyServer:

    def __init__(self, transporter_args):
        procedures = ["getMonitoringServerInfo"]
        self.__sender = haplib.Sender(transporter_args)
        self.__rpc_queue = multiprocessing.JoinableQueue()
        self.__receiver = haplib.DispatchableReceiver(transporter_args,
                                                      self.__rpc_queue,
                                                      procedures)
        self.__handler_map = {"getMonitoringServerInfo":
                              self.__rpc_get_monitoring_server_info}

    def __call__(self):
        self.__receiver.daemonize()
        while True:
            request = self.__rpc_queue.get()
            method = request["method"]
            params = request["params"]
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


if __name__ == '__main__':
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
