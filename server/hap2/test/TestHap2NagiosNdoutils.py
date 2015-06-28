#!/usr/bin/env python
# coding: UTF-8
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
import common
import haplib
from hap2_nagios_ndoutils import Common

class CommonForTest(Common):
    def __init__(self, options={}):
        Common.__init__(self)
        self.__options = options
        print options

    def get_ms_info(self):
        # On TravisCI, we may return appropriate paramters here
        if self.__options.get("db_invalid_param"):
            return haplib.MonitoringServerInfo({
                "serverId": "hoge",
                "url": "",
                "type": "",
                "nickName": "",
                "userName": "non-existing-user",
                "password": "",
                "pollingIntervalSec": 30,
                "retryIntervalSec": 10,
                "extendedInfo": "",
            })
        else:
            return None

class TestCommon(unittest.TestCase):
    def test_constructor(self):
        common.assertNotRaises(Common)

    def test_ensure_connection(self):
        comm = CommonForTest()
        common.assertNotRaises(comm.ensure_connection)

    def test_ensure_connection_with_failure_of_opening_db(self):
        options = {"db_invalid_param": True}
        comm = CommonForTest(options)
        self.assertRaises(haplib.Signal, comm.ensure_connection)

    def test_close_connection_without_connection(self):
        comm = Common()
        common.assertNotRaises(comm.close_connection)

    def test_close_connection(self):
        self.test_ensure_connection()
        self.test_close_connection_without_connection()

