#! /usr/bin/env python
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

import daemon
import json
import multiprocessing
import Queue
import argparse
import time
from haplib import Utils
import haplib
import zabbixapi
import standardhap

class PreviousHostsInfo:
    def __init__(self):
        self.hosts = list()
        self.host_groups = list()
        self.host_group_membership = list()


class ZabbixAPIConductor:
    def __init__(self):
        self.__api = None
        self.__previous_hosts_info = PreviousHostsInfo()
        self.__trigger_last_info = None
        self.__event_last_info = None

    def set_monitoring_server_info(self, ms_info):
        self.__api = zabbixapi.ZabbixAPI(ms_info)

    def request(self, procedure_name, params):
        raise NotImplementedError

    def wait_response(self, request_id):
        raise NotImplementedError

    def put_items(self, host_id=None, fetch_id=None):
        params = {"items": self.__api.get_items(host_id)}
        if fetch_id is not None:
            params["fetchId"] = fetch_id

        request_id = self.request("putItems", params)
        self.wait_response(request_id)

    def put_history(self, item_id, begin_time, end_time, fetch_id):
        params = {"itemId": item_id,
                  "histories": self.__api.get_history(item_id, begin_time, end_time),
                  "fetchId": fetch_id}

        request_id = self.request("putHistory", params)
        self.wait_response(request_id)

    def update_hosts_and_host_group_membership(self):
        hosts, hg_membership = self.__api.get_hosts()
        hosts.sort()
        if self.__previous_hosts_info.hosts != hosts:
            hosts_params = {"updateType": "ALL", "hosts": hosts}
            request_id = self.request("updateHosts", hosts_params)
            self.wait_response(request_id)
            self.__previous_hosts_info.hosts = hosts

        hg_membership.sort()
        if self.__previous_hosts_info.host_group_membership != hg_membership:
            hg_membership_params = {"updateType": "ALL",
                                    "hostGroupMembership": hg_membership}
            request_id = self.request("updateHostGroupMembership",
                                      hg_membership_params)
            self.wait_response(request_id)
            self.__previous_hosts_info.host_group_membership = hg_membership

    def update_host_groups(self):
        host_groups = self.__api.get_host_groups()
        host_groups.sort()
        if self.__previous_hosts_info.host_groups != host_groups:
            hosts_params = {"updateType": "ALL", "hostGroups": host_groups}
            request_id = self.request("updateHostGroups", hosts_params)
            self.wait_response(request_id)
            self.__previous_hosts_info.host_groups = host_groups

    def update_triggers(self, host_id=None, fetch_id=None):
        if self.__trigger_last_info is None:
            self.__trigger_last_info = self.get_last_info("trigger")

        triggers = self.__api.get_triggers(self.__trigger_last_info, host_id)
        self.__trigger_last_info = \
            Utils.find_last_info_from_dict_array(triggers, "lastChangeTime")

        params = {"triggers": triggers, "updateType": "UPDATED",
                  "lastInfo": self.__trigger_last_info}

        if fetch_id is not None:
            params["fetchId"] = fetch_id
            params["updateType"] = "ALL"

        request_id = self.request("updateTriggers", params)
        self.wait_response(request_id)

    def update_events(self, last_info=None, count=None, direction="ASC",
                      fetch_id=None):
        if last_info is None:
            last_info = self.get_last_info("event")

        if direction == "ASC":
            event_id_from = last_info
            event_id_till = None
            if count is not None:
                event_id_till = event_id_from + count
        # The following elif sentence is used from only fetchEvents
        elif direction == "DESC":
            event_id_till = last_info
            event_id_from = event_id_till - count

        events = self.__api.get_events(event_id_from, event_id_till)

        count = len(events) / 1000 + 1
        for num in range(0, count):
            start = num * 1000
            send_events = events[start: start + 1000]
            last_info = Utils.find_last_info_from_dict_array(send_events,
                                                              "eventId")
            params = {"events": send_events, "lastInfo": last_info,
                      "updateType": "UPDATE"}

            if fetch_id is not None:
                params["fetchId"] = fetch_id

            if num < count - 1:
                params["mayMoreFlag"] = True

            request_id = self.request("updateTriggers", params)
            self.wait_response(request_id)

        self.__event_last_info = last_info


class Hap2ZabbixAPIPoller(haplib.HapiProcessor, ZabbixAPIConductor):
    def __init__(self, __sender):
        haplib.HapiProcessor.__init__(self, __sender)
        ZabbixAPIConductor.__init__(self)

    def __update(self):
        self.put_items()
        self.update_hosts_and_host_group_membership()
        self.update_host_groups()
        self.update_triggers()
        self.update_events()

    def __call__(self):
        arm_info = haplib.ArmInfo()
        while True:
            sleep_time = self.sender.ms_info.polling_interval_sec
            try:
                self.__update()
                arm_info.last_status = "OK"
                arm_info.failure_reason = ""
                arm_info.last_success_time = Utils.get_current_hatohol_time()
                arm_info.num_success += 1
            except:
                sleep_time = self.sender.ms_info.retry_interval_sec
                arm_info.last_status = "NG"
                #ToDo Think about how to input failure_reason
                # arm_info.failure_reason = ""
                arm_info.failure_time = Utils.get_current_hatohol_time()
                arm_info.num_failure += 1

            self.update_arm_info(arm_info)
            time.sleep(sleep_time)

class Hap2ZabbixAPIMain(haplib.BaseMainPlugin, ZabbixAPIConductor):
    def __init__(self, *args, **kwargs):
        haplib.BaseMainPlugin.__init__(self, kwargs["transporter_args"])
        ZabbixAPIConductor.__init__(self)
        self.set_implemented_procedures(["exchangeProfile",
                                         "fetchItems",
                                         "fetchHistory",
                                         "fetchTriggers",
                                         "fetchEvents"])

    def hap_fetch_items(self, params, request_id):
        self.get_sender().response("SUCCESS", request_id)
        self.put_items(params["hostId"], params["fetchId"])

    def hap_fetch_history(self, params, request_id):
        self.get_sender().response("SUCCESS", request_id)
        self.put_history(params["itemId"], params["beginTime"],
                         params["endTime"], params["fetchId"])

    def hap_fetch_triggers(self, params, request_id):
        self.get_sender().response("SUCCESS", request_id)
        self.update_triggers(params["hostId"], params["fetchId"])

    def hap_fetch_events(self, params, request_id):
        self.get_sender().response("SUCCESS", request_id)
        self.update_events(params["lastInfo"], params["count"],
                           params["direction"], params["fetchId"])


class Hap2ZabbixAPI(standardhap.StandardHap):
    def create_main_plugin(self, *args, **kwargs):
        return Hap2ZabbixAPIMain(*args, **kwargs)

    def create_poller(self, *args, **kwargs):
        return Hap2ZabbixAPIPoller(self, *args, **kwargs)

    def on_got_monitoring_server_info(self, ms_info):
        get_main_plugin().set_monitoring_server_info(ms_info)

if __name__ == '__main__':
    hap = Hap2ZabbixAPI()
    hap()
