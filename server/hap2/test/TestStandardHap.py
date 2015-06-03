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

class TestStandardHap(unittest.TestCase):
    class StandardHapTestee(StandardHap):
        def __init__(self):
            StandardHap.__init__(self)

        def create_main_plugin(self, *args, **kwargs):
            return haplib.BaseMainPlugin(*args, **kwargs)

    def test_normal_run(self):
        hap = self.StandardHapTestee()
        sys.argv = [sys.argv[0],
                    "--amqp-vhost", "test", "--amqp-user", "test_user",
                    "--amqp-password", "test_password"]
        sys.argv = []
        hap()
