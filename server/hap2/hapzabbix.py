#! /usr/bin/env python
# coding: UTF-8

import daemon
import json
import haplib
import zabbixapi

class HapZabbixProcedures(haplib.BaseProcedures):
    def exchangeProfile(self, params):
        optimize_server_procedures(self.valid_procedures_of_server, params)
        my_procedures = haplib.get_implement_procedures(HapZabbixProcedures)
        push_profile("response", my_procedures)


    def fetchItems(self):
        print "Not implement"


    def fetchHistory(self):
        print "Not implement"


    def fetchTriggers(self):
        print "Not implement"


    def fetchEvents(self):
        print "Not implement"


class PreviousHostsInfo:
    def __init__():
        self.hosts = []
        self.host_groups = []
        self.host_group_membeship = []




def routine_update():
    print "Not implement"

def main():
    daemon_runner = daemon.runner.DaemonRunner()


if __name__ == '__main__':
    main()
