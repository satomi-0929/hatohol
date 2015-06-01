#! /usr/bin/env python
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

import multiprocessing

class StdHap2Process:

    def create_main_plugin(self):
        assert False, "create_main_plugin shall be overriden"

    """
    An abstract method to create poller process.

    @return
    A class for poller. The class shall have run method.
    If this method returns None, no poller process is created.
    """
    def create_poller(self):
        return None

    def run(self):
        main_plugin = create_main_plugin()
        poller = create_poller()
        if poller is not None:
            poll_process = multiprocessing.Process(target=poller.run)
            poll_process.daemon = True
            poll_process.start()
        main_plugin.run()
