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

class Hap2NagiosNDOUtilsPoller(haplib.BasePoller):

    def __init__(self, *args, **kwargs):
        haplib.BasePoller.__init__(self, *args, **kwargs) 

        self.__db_server = "localhost"
        self.__db_user = "root"
        self.__db_passwd = ""

    def poll_setup(self):
        if self.__deb is not None:
            return
        try:
            self.__db = MySQLdb.connect(host=self.__db_server,
                                        user=self.__db_user,
                                        passwd=self.__db_passwd)
            self.__cursor = db.cursor()
        except MySQLdb.Error as (errno, msg):
            logging.error('MySQL Error [%d]: %s' % (errno, msg))
            raise haplib.HandledException

    def poll_hosts(self):
        sql = "SELECT " \
              "t0.host_object_id, " \
              "t0.display_name, " \
              "t1.name1" \
              "FROM nagios_hostgroups t0 INNER JOIN nagios_objects t1 " \
              "ON t0.host_object_id=t1.object_id"
        self.__cursor.execute(sql)
        result = cursor.fetchall()
        for row in result:
            print "code -- " + row[0].encode('utf-8')
            print "name -- " + row[1].encode('utf-8')

    def poll_hostgroups(self):
        pass

    def poll_hostgroup_members(self):
        pass

    def poll_triggers(self):
        pass

    def poll_events(self):
        pass

    def on_aborted_poll(self):
        self.__db = None
        self.__cursor = None

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
