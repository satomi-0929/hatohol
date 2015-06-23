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
from hap2_ceilometer import Common
from datetime import datetime

class TestCommon(unittest.TestCase):
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
