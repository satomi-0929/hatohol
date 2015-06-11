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

        self.__db = None
        self.__db_server = "localhost"
        self.__db_name = "ndoutils"
        self.__db_user = "root"
        self.__db_passwd = ""

    def poll_setup(self):
        if self.__db is not None:
            return
        try:
            self.__db = MySQLdb.connect(host=self.__db_server,
                                        db=self.__db_name,
                                        user=self.__db_user,
                                        passwd=self.__db_passwd)
            self.__cursor = self.__db.cursor()
        except MySQLdb.Error as (errno, msg):
            logging.error('MySQL Error [%d]: %s' % (errno, msg))
            raise haplib.HandledException

    def poll_hosts(self):
        t0 = "nagios_hosts"
        t1 = "nagios_objects"
        sql = "SELECT " \
              + "%s.host_object_id, " % t0 \
              + "%s.display_name, " % t0 \
              + "%s.name1 " % t1 \
              + "FROM %s INNER JOIN %s " % (t0, t1) \
              + "ON %s.host_object_id=%s.object_id" % (t0, t1)
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        hosts = []
        for row in result:
            host_id, name, name1 = row
            hosts.append({"hostId":name1, "hostName":name})
        self.put_hosts(hosts)

    def poll_hostgroups(self):
        t0 = "nagios_hostgroups"
        t1 = "nagios_objects"
        sql = "SELECT " \
              + "%s.hostgroup_id, " % t0 \
              + "%s.alias, " % t0 \
              + "%s.name1 " % t1 \
              + "FROM %s INNER JOIN %s " % (t0, t1) \
              + "ON %s.hostgroup_id=%s.object_id" % (t0, t1)
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        groups = []
        for row in result:
            group_id, name, name1 = row
            groups.append({"groupId":name1, "groupName":name})
        self.put_host_groups(groups)

    def poll_hostgroup_members(self):
        pass

    def poll_triggers(self):
        pass

    def poll_events(self):
        pass

    def on_aborted_poll(self):
        if self.__cursor is not None:
            self.__cursor.close()
            self.__cursor = None
        if self.__db is not None:
            self.__db.close()
            self.__db = None
        self.reset()

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
