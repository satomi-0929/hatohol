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
