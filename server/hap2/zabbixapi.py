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

import urllib2
import json
import math
from haplib import HAPUtils

TRIGGER_SEVERITY = {-1: "ALL", 0: "UNKNOWN", 1: "INFO", 2: "WARNING",
                    3: "ERROR", 4: "CRITICAL", 5: "EMERGENCY"}
TRIGGER_STATUS = {0: "GOOD", 1: "NG", 2: "UNKNOWN"}
EVENT_TYPE = {0: "GOOD", 1: "BAD", 2: "UNKNOWN", 3: "NOTIFICATION"}

class ZabbixAPI:
    def __init__(self, monitoring_server_info):
        self.url = monitoring_server_info.url
        self.auth_token = self.get_auth_token(monitoring_server_info.user_name,
                                              monitoring_server_info.user_passwd)
        self.api_version = self.get_api_version()

    def get_auth_token(self, user_name, user_passwd):
        params = {'user': user_name, 'password': user_passwd}
        res_dict = self.get_response_dict("user.authenticate", params)

        self.result = check_response(res_dict)
        if not self.result:
            return

        return res_dict["result"]

    def get_api_version(self):
        res_dict = self.get_response_dict("apiinfo.version", None)

        self.result = check_response(res_dict)
        if not self.result:
            return

        return res_dict["result"][0:3]

    def get_items(self, host_id=None):
        params = {"output": "extend", "selectApplications": ["name"],
                  "monitored": True}
        if host_id is not None:
            params["hostids"] = host_id

        res_dict = self.get_response_dict("item.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        items = list()
        for item in res_dict["result"]:
            if int(item["lastns"]) == 0:
                ns = 0
            else:
                ns = float(item["lastns"])/(10 ** math.log10(int(item["lastns"])) + 1)

            items.append({"itemId": item["itemid"],
                          "hostId": item["hostid"],
                          "brief": item["name"],
                          "lastValueTime": HAPUtils.translate_unix_time_to_hatohol_time(int(item["lastclock"]) + ns),
                          "lastValue": item["lastvalue"],
                          "itemGroupName": get_item_groups(item["applications"]),
                          "unit": item["units"]})

        return items

    def get_history(self, item_id, begin_time, end_time):
        params = {"output": "extend", "itemids": item_id,
                  "history": get_item_value_type(item_id), "sortfield": "clock",
                  "sortorder": "ASC", "time_from": begin_time, "time_till": end_time}
        res_dict = self.get_response_dict("history.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        histories = list()
        for history in res_dict["result"]:
            if int(history["ns"]) == 0:
                ns = 0
            else:
                ns = float(history["ns"])/(10 ** math.log10(int(history["ns"])) + 1)

            histories.append({"value": history["value"],
                              "time": HAPUtils.translate_unix_time_to_hatohol_time(int(history["clock"]) + ns)})

        return histories

    def get_item_value_type(self, item_id):
        params = {"output": ["value_type"], "itemids": [item_id]}
        res_dict = self.get_response_dict("item.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        return res_dict[0]["value_type"]

    # The following method gets not only hosts info but also host group membership.
    def get_hosts(self):
        params = {"output": "extend", "selectGroups": "refer",
                  "monitored_hosts": True}
        res_dict = self.get_response_dict("host.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        hosts = list()
        host_group_membership = list()
        for host in res_dict["result"]:
            hosts.append({"hostId": host["hostid"], "hostName": host["name"]})

            group_ids = list()
            for groups in host["groups"]:
                group_ids.append(groups["groupid"])

            host_group_membership.append({"hostId": host["hostid"],
                                          "groupIds": group_ids})

        return (hosts, host_group_membership)

    def get_host_groups(self):
        params = {"output": "extend", "selectHosts": "refer",
                  "real_hosts": True, "monitored_hosts": True}
        res_dict = self.get_response_dict("hostgroup.get", params,
                                          self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        host_groups = list()
        for host_group in res_dict["result"]:
            host_groups.append({"hostId": host_group["groupid"],
                                "groupName": host_group["name"]})

        return host_groups

    def get_triggers(self, requestSince=None, host_id=None):
        params = {"output": "extend", "selectHosts": ["name"], "active": True}
        if requestSince is not None:
            params["lastChangeSince"] = int(requestSince)
        if host_id is not None:
            params["hostids"] = host_id

        res_dict = self.get_response_dict("trigger.get", params,
                                          self.auth_token)
        expanded_res_dict = self.get_trigger_expanded_description(requestSince,
                                                                  host_id)

        self.result = check_response(res_dict)
        if not self.result:
            return

        triggers = list()
        for num, trigger in enumerate(res_dict["result"]):
            triggers.append({"triggerId": trigger["triggerid"],
                             "status": "OK",
                             "severity": trigger["priority"],
                             "lastChangeTime": HAPUtils.translate_unix_time_to_hatohol_time(int(trigger["lastchange"])),
                             "hostId": trigger["hosts"][0]["hostid"],
                             "hostName": trigger["hosts"][0]["name"],
                             "brief": trigger["description"],
                             "extendedInfo": expanded_res_dict[num]["description"]})

        return triggers

    def get_trigger_expanded_description(self, requestSince=None, host_id=None):
        params = {"output": "description", "expandDescription": 1,
                  "active": True}
        if requestSince is not None:
            params["lastChangeSince"] = int(requestSince)
        if host_id is not None:
            params["hostids"] = host_id

        res_dict = self.get_response_dict("trigger.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        return res_dict

    def get_select_trigger(self, trigger_id):
        params = {"output": "extend", "triggers_id": trigger_id, "expandDescription": 1}
        res_dict = self.get_response_dict("trigger.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        return res_dict

    def get_events(self, event_id_from, event_id_till=None):
        params = {"output": "extend", "eventid_from": event_id_from, "selectHosts": ["name"]}
        if event_id_till is not None:
            params["eventid_till"] = event_id_till

        res_dict = self.get_response_dict("event.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        events = list()
        for event in res_dict["result"]:
            if int(event["ns"]) == 0:
                ns = 0
            else:
                ns = float(event["ns"])/(10 ** math.log10(int(event["ns"])) + 1)

            trigger = self.get_select_trigger(event["objectid"])
            events.append({"eventId": event["eventid"],
                           "time": HAPUtils.translate_unix_time_to_hatohol_time(int(event["clock"]) + ns),
                           "type": EVENT_TYPE[event["value"]],
                           "triggerId": trigger["triggerid"],
                           "status": TRIGGER_STATUS[event["value"]],
                           "severity": trigger["severity"],
                           "hostId": event["hosts"][0]["hostid"],
                           "hostName": event["hosts"][0]["name"],
                           "brief": trigger["description"],
                           "extendedInfo": ""})

        return events

    def get_response_dict(self, method_name, params, auth_token=None):
        HEADER = {"Content-Type": "application/json-rpc"}
        post = json.dumps({"jsonrpc": "2.0", "method": method_name,
                           "params": params, "auth": auth_token, "id": 1})
        request = urllib2.Request(self.url, post, HEADER)
        response = urllib2.urlopen(request)
        res_str = response.read()

        return json.loads(res_str)


def get_last_info_from_array_dict(value_name, array_dict):
    last_info = None
    for each_dict in array_dict:
        if last_info < each_dict[value_name]:
            last_info = each_dict[value_name]

    return last_info


def get_item_groups(applications):
    item_groups = list()
    for application in applications:
        item_groups.append(application["name"])

    return item_groups


def check_response(response_dict):
    if "error" in response_dict:
        return False

    return True
