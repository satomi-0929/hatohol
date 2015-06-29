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
from hap2_ceilometer import Common
from datetime import datetime
import haplib

class CommonForTest(Common):
    def get_ms_info(self):
        return None

class TestCommon(unittest.TestCase):
    def test_constructor(self):
        testutils.assertNotRaises(Common)

    def test_ensure_connection_without_monitoring_server_info(self):
        comm = CommonForTest()
        self.assertRaises(haplib.Signal, comm.ensure_connection)

    def test_parse_time_with_micro(self):
        actual = Common.parse_time("2014-09-05T06:25:29.185000")
        expect = datetime(2014, 9, 5, 6, 25, 29, 185000)
        self.assertEqual(actual, expect)

    def test_parse_time_without_micro(self):
        actual = Common.parse_time("2014-09-05T06:25:29")
        expect = datetime(2014, 9, 5, 6, 25, 29)
        self.assertEqual(actual, expect)

    def test_parse_time_without_invalid_string(self):
        self.assertRaises(Exception, Common.parse_time, "20140905062529")

    def test_alarm_to_hapi_status_ok(self):
        alarm_type = "state transition"
        detail = '{"state": "ok"}'
        evt_type = Common.alarm_to_hapi_status(alarm_type, detail)
        self.assertEqual(evt_type, "OK")

    def test_alarm_to_hapi_status_ng(self):
        alarm_type = "state transition"
        detail = '{"state": "alarm"}'
        evt_type = Common.alarm_to_hapi_status(alarm_type, detail)
        self.assertEqual(evt_type, "NG")

    def test_alarm_to_hapi_status_unknown(self):
        alarm_type = "state transition"
        detail = '{"state": "insufficient data"}'
        evt_type = Common.alarm_to_hapi_status(alarm_type, detail)
        self.assertEqual(evt_type, "UNKNOWN")

    def test_alarm_to_hapi_status_creation(self):
        alarm_type = "creation"
        detail = '{"state": "ok"}'
        evt_type = Common.alarm_to_hapi_status(alarm_type, detail)
        self.assertEqual(evt_type, "OK")

    def test_alarm_to_hapi_status_with_invalid_type(self):
        alarm_type = "unknown type"
        detail = '{"state": "ok"}'
        self.assertRaises(
            Exception,
            Common.alarm_to_hapi_status, (alarm_type, detail))

    def test_alarm_to_hapi_status_with_invalid_detail(self):
        alarm_type = "state transition"
        detail = '{"state": "Cho Cho II kanji"}'
        self.assertRaises(
            Exception,
            Common.alarm_to_hapi_status, (alarm_type, detail))

    def test_hapi_time_to_url_enc_openstack_time(self):
        hapi_time = "20150624081005"
        actual = Common.hapi_time_to_url_enc_openstack_time(hapi_time)
        expect = "2015-06-24T08%3A10%3A05.000000"
        self.assertEqual(actual, expect)

    def test_hapi_time_to_url_enc_openstack_time_with_us(self):
        hapi_time = "20150624081005.123456"
        actual = Common.hapi_time_to_url_enc_openstack_time(hapi_time)
        expect = "2015-06-24T08%3A10%3A05.123456"
        self.assertEqual(actual, expect)

    def test_hapi_time_to_url_enc_openstack_time_with_ns(self):
        hapi_time = "20150624081005.123456789"
        actual = Common.hapi_time_to_url_enc_openstack_time(hapi_time)
        expect = "2015-06-24T08%3A10%3A05.123456"
        self.assertEqual(actual, expect)

    def test_hapi_time_to_url_enc_openstack_time_with_ms(self):
        hapi_time = "20150624081005.123"
        actual = Common.hapi_time_to_url_enc_openstack_time(hapi_time)
        expect = "2015-06-24T08%3A10%3A05.123000"
        self.assertEqual(actual, expect)

    def test_hapi_time_to_url_enc_openstack_time_with_dot_only(self):
        hapi_time = "20150624081005."
        actual = Common.hapi_time_to_url_enc_openstack_time(hapi_time)
        expect = "2015-06-24T08%3A10%3A05.000000"
        self.assertEqual(actual, expect)
