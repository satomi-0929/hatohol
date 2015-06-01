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

import sys
import MySQLdb
import time
import haplib
import stdhap2process

class HandledException:
    pass

class NagiosNDOUtilsPoller:

    def __init__(self):
        self._pollingInterval = 30
        self._retryInterval = 10
        self._db_server = "localhost"
        self._db_user = "root"
        self._db_passwd = ""

    def run(self):
        while (True):
            self._poll()

    def _poll(self):
        logging.debug("Start polling.")
        sleepTime = self._retryInterval
        try:
            self._connect_ndoutils_db()
            self._get_hosts()
            sleepTime = self._pollingInterval
        except HandledException:
            pass
        except:
            (exctype, value, traceback) = sys.exc_info()
            logging.error("Unexpected error: %s, %s, %s" % (exctype, value, traceback))

        # NOTE: The following sleep() will be replaced with a blocking read
        #       from the queue.
        time.sleep(sleepTime)

    def _connect_ndoutils_db(self):
        try:
            db = MySQLdb.connect(host=self._db_server,
                                 user=self._db_user, passwd=self._db_passwd)
            cursor = db.cursor()
        except MySQLdb.Error as (errno, msg):
            logging.error('MySQL Error [%d]: %s' % (errno, msg))
            raise HandledException

    def _get_hosts(self):
        pass

    def exchangeProfile(self):
        pass

class HapNagiosNDOUtilsMain(haplib.HAPBaseMainPlugin):
    def __init__(*args, **kwargs):
        haplib.HAPBaseMainPlugin.__init__(*args, **kwargs)

class HapNagiosNDOUtils(stdhap2process.StdHap2Process):
    def create_main_plugin(self, *args, **kwargs):
        return HapNagiosNDOUtilsMain(*args, **kwargs)

if __name__ == '__main__':
    hap = HapNagiosNDOUtils()
    hap.run()
