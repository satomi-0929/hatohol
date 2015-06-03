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
import standardhap

class HandledException:
    pass

class NagiosNDOUtilsPoller:

    def __init__(self):
        self.__pollingInterval = 30
        self.__retryInterval = 10
        self.__db_server = "localhost"
        self.__db_user = "root"
        self.__db_passwd = ""

    def __call__(self):
        while (True):
            self.__poll()

    def __poll(self):
        logging.debug("Start polling.")
        sleepTime = self._retryInterval
        try:
            self.__connect_ndoutils_db()
            self.__get_hosts()
            sleepTime = self.__pollingInterval
        except HandledException:
            pass
        except:
            (exctype, value, traceback) = sys.exc_info()
            logging.error("Unexpected error: %s, %s, %s" % (exctype, value, traceback))

        # NOTE: The following sleep() will be replaced with a blocking read
        #       from the queue.
        time.sleep(sleepTime)

    def __connect_ndoutils_db(self):
        try:
            db = MySQLdb.connect(host=self._db_server,
                                 user=self._db_user, passwd=self._db_passwd)
            cursor = db.cursor()
        except MySQLdb.Error as (errno, msg):
            logging.error('MySQL Error [%d]: %s' % (errno, msg))
            raise HandledException

    def __get_hosts(self):
        pass

class HapNagiosNDOUtilsMain(haplib.BaseMainPlugin):
    def __init__(self, *args, **kwargs):
        haplib.BaseMainPlugin.__init__(self, *args, **kwargs)

class HapNagiosNDOUtils(standardhap.StandardHap):
    def create_main_plugin(self, *args, **kwargs):
        return HapNagiosNDOUtilsMain(*args, **kwargs)

if __name__ == '__main__':
    hap = HapNagiosNDOUtils()
    hap()
