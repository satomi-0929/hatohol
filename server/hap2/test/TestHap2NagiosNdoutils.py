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
import common as testutil
import haplib
from hap2_nagios_ndoutils import Common

class CommonForTest(Common):
    def __init__(self, options={}):
        Common.__init__(self)
        self.__options = options
        self.stores = {}
        print options

    def get_ms_info(self):
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
            # On TravisCI, we may return appropriate paramters here
            return None

    def put_hosts(self, hosts):
        self.stores["hosts"] = hosts

    def put_host_groups(self, groups):
        self.stores["host_groups"] = groups

    def put_host_group_membership(self, membership):
        self.stores["host_group_membership"] = membership

    def put_triggers(self, triggers, update_type,
                     last_info=None, fetch_id=None):
        self.stores["triggers"] = triggers
        self.stores["update_type"] = update_type
        self.stores["last_info"] = last_info
        self.stores["fetch_id"] = fetch_id

class TestCommon(unittest.TestCase):
    def test_constructor(self):
        testutil.assertNotRaises(Common)

    def test_ensure_connection(self):
        comm = CommonForTest()
        testutil.assertNotRaises(comm.ensure_connection)

    def test_ensure_connection_with_failure_of_opening_db(self):
        options = {"db_invalid_param": True}
        comm = CommonForTest(options)
        self.assertRaises(haplib.Signal, comm.ensure_connection)

    def test_close_connection_without_connection(self):
        comm = Common()
        testutil.assertNotRaises(comm.close_connection)

    def test_close_connection(self):
        self.test_ensure_connection()
        self.test_close_connection_without_connection()

    def test_parse_url_sv_port_db(self):
        self.__assert_parse_url(
            "123.45.67.89:1122/mydb", ("123.45.67.89", "1122", "mydb"))

    def test_parse_url_sv_port(self):
        self.__assert_parse_url(
            "123.45.67.89:1122",
            ("123.45.67.89", "1122", Common.DEFAULT_DATABASE))

    def test_parse_url_sv(self):
        self.__assert_parse_url(
            "123.45.67.89",
            ("123.45.67.89", Common.DEFAULT_PORT, Common.DEFAULT_DATABASE))

    def test_parse_url_sv_db(self):
        self.__assert_parse_url(
            "123.45.67.89/mydb",
            ("123.45.67.89", Common.DEFAULT_PORT, "mydb"))

    def test_parse_url_db(self):
        self.__assert_parse_url(
            "/mydb", (Common.DEFAULT_SERVER, Common.DEFAULT_PORT, "mydb"))

    def test_collect_hosts_and_put(self):
        comm = CommonForTest()
        comm.ensure_connection()
        # TODO: insert test materials and check it
        comm.collect_hosts_and_put()
        self.assertEquals(type(comm.stores["hosts"]), type([]))

    def test_collect_host_groups_and_put(self):
        comm = CommonForTest()
        comm.ensure_connection()
        # TODO: insert test materials and check it
        comm.collect_host_groups_and_put()
        self.assertEquals(type(comm.stores["host_groups"]), type([]))

    def test_collect_host_group_membership_and_put(self):
        comm = CommonForTest()
        comm.ensure_connection()
        # TODO: insert test materials and check it
        comm.collect_host_group_membership_and_put()
        self.assertEquals(type(comm.stores["host_group_membership"]), type([]))

    def test_collect_triggers_and_put(self):
        comm = CommonForTest()
        comm.ensure_connection()
        # TODO: insert test materials and check it
        fetch_id = "12345"
        comm.collect_triggers_and_put(fetch_id)
        self.assertEquals(type(comm.stores["triggers"]), type([]))
        self.assertEquals(comm.stores["update_type"], "ALL")
        self.assertEquals(comm.stores["last_info"], None)
        self.assertEquals(comm.stores["fetch_id"], fetch_id)

    def __assert_parse_url(self, url, expect):
        comm = Common()
        target_func = testutil.returnPrivObj(comm, "__parse_url")
        self.assertEquals(target_func(url), expect)
