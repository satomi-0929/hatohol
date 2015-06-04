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
import unittest
import sys
from standardhap import StandardHap
import haplib
import transporter
import multiprocessing
import json

class EzTransporter(transporter.Transporter):

    __queue = multiprocessing.Queue()
    TEST_MONITORING_SERVER_RESULT = '{ \
          "extendedInfo": "exampleExtraInfo", \
          "serverId": 1, \
          "url": "http://example.com:80", \
          "type": 0, \
          "nickName": "exampleName", \
          "userName": "Admin", \
          "password": "examplePass",\
          "pollingIntervalSec": 30, \
          "retryIntervalSec": 10 \
        }'

    def __init__(self):
        transporter.Transporter.__init__(self)

    def call(self, _msg):
        cmd_map = {"getMonitoringServerInfo": self.__get_monitoring_server_info}
        msg = json.loads(_msg)
        handler = cmd_map.get(msg["method"])
        assert handler is not None
        handler(msg["id"], msg["params"])

    def reply(self, msg):
        raise Error

    def run_receive_loop(self):
        msg = self.__queue.get()
        (self.get_receiver())(None, msg)

    def __get_monitoring_server_info(self, call_id, params):
        reply = '{"id": %s, "result": %s, "jsonrpc": "2.0"}' % \
                (str(call_id), self.TEST_MONITORING_SERVER_RESULT)
        self.__queue.put(reply)

class TestStandardHap(unittest.TestCase):
    class StandardHapTestee(StandardHap):
        def __init__(self):
            StandardHap.__init__(self)
            self.__received_ms_info = None

        def create_main_plugin(self, *args, **kwargs):
            return haplib.BaseMainPlugin(*args, **kwargs)

        def on_got_monitoring_server_info(self, ms_info):
            self.__received_ms_info = ms_info

        def get_received_ms_info(self):
            return self.__received_ms_info

    def test_normal_run(self):
        hap = self.StandardHapTestee()
        sys.argv = [sys.argv[0],
                    "--transporter", "EzTransporter",
                    "--transporter-module", "TestStandardHap"]
        hap()
        self.assertEquals(hap.get_received_ms_info(),
                          json.loads(EzTransporter.TEST_MONITORING_SERVER_RESULT))
