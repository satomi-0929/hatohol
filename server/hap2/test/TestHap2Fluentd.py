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
import common as testutils
import hap2_fluentd
import transporter
import haplib

class Hap2FluentdMainTestee(hap2_fluentd.Hap2FluentdMain):
    def __init__(self):
        kwargs = {"transporter_args": {"class": transporter.Transporter}}
        hap2_fluentd.Hap2FluentdMain.__init__(self, **kwargs)

    def get_launch_args(self):
        return testutils.returnPrivObj(self, "__launch_args", "Hap2FluentdMain")

    def set_null_fluentd_manager_main(self):
        self._Hap2FluentdMain__fluentd_manager_main = lambda : None

class Hap2FluentdMain(unittest.TestCase):
    def test_constructor(self):
        kwargs = {"transporter_args": {"class": transporter.Transporter}}
        main = hap2_fluentd.Hap2FluentdMain(**kwargs)

    def test_set_arguments(self):
        main = Hap2FluentdMainTestee()
        arg = type('', (), {})()
        arg.fluentd_launch = "ABC -123 435"
        main.set_arguments(arg)
        self.assertEquals(main.get_launch_args(), ["ABC", "-123", "435"])

    def test_set_ms_info(self):
        main = Hap2FluentdMainTestee()
        main.set_null_fluentd_manager_main()
        main.set_ms_info(haplib.MonitoringServerInfo({
            "serverId": 51,
            "url": "http://example.com",
            "type": "Fluentd",
            "nickName": "Jack",
            "userName": "fooo",
            "password": "gooo",
            "pollingIntervalSec": 30,
            "retryIntervalSec": 10,
            "extendedInfo": "",
        }))
