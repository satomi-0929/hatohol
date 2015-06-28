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
    def get_ms_info(self):
        # On TravisCI, we may return appropriate paramters here
        return None

class TestCommon(unittest.TestCase):
    def test_constructor(self):
        common.assertNotRaises(Common)

    def test_close_connection(self):
        comm = Common()
        common.assertNotRaises(comm.close_connection)

    # TODO: test_close_connection with __currsor and __db used

    def test_ensure_connection(self):
        comm = CommonForTest()
        common.assertNotRaises(comm.ensure_connection)
