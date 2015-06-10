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

class Hap2NagiosNDOUtilsPoller(haplib.HapiProcessor):

    def __init__(self, *args, **kwargs):
        haplib.HapiProcessor.__init__(self, kwargs["sender"],
                                      kwargs["component_code"])
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

class Hap2NagiosNDOUtilsMain(haplib.BaseMainPlugin):
    def __init__(self, *args, **kwargs):
        haplib.BaseMainPlugin.__init__(self, kwargs["transporter_args"])
        self.set_implemented_procedures(["exchangeProfile"])

class Hap2NagiosNDOUtils(standardhap.StandardHap):
    def create_main_plugin(self, *args, **kwargs):
        return Hap2NagiosNDOUtilsMain(*args, **kwargs)

    def create_poller(self, *args, **kwargs):
        return Hap2NagiosNDOUtilsPoller(self, *args, **kwargs)

    def on_got_monitoring_server_info(self, ms_info):
        self.get_main_plugin().set_ms_info(ms_info)
        self.get_poller().set_ms_info(ms_info)

if __name__ == '__main__':
    hap = Hap2NagiosNDOUtils()
    hap()
