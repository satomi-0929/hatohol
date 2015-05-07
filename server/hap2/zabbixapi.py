#! /usr/bin/env python
# coding: UTF-8

import urllib2
import json

TRIGGER_SEVERITY = {-1: "ALL", 0: "UNKNOWN", 1: "INFO", 2: "WARNING", 3:"ERROR", 4: "CRITICAL", 5: "EMERGENCY"}
TRIGGER_STATUS = {0: "GOOD", 1: "NG", 2: "UNKNOWN"}
EVENT_TYPE = {0: "GOOD", 1: "BAD", 2: "UNKNOWN", 3: "NOTIFICATION"}

class ZabbixAPI:
    HEADER = {"Content-Type":"application/json-rpc"}
    def __init__(self, monitoring_server_info):
        self.url = "http://" + monitoring_server_info.ip_address + "/zabbix/api_jsonrpc.php"
        self.auth_token = self.get_auth_token(monitoring_server_info.user_name,
                                monitoring_server_info.user_passwd)
        self.api_version = self.get_api_version()


    def get_auth_token(self, ip_adderss, user_name, user_passwd):
        params = {'user':user_name, 'password':user_passwd}
        res_dict = get_response_dict("user.authenticate", params)

        self.result = check_response(res_dict)
        if not self.result:
            return

        return res_dict["result"]


    def get_api_version(self):
        res_dict = get_response_dict("apiinfo.version", None)

        self.result = check_response(res_dict)
        if not self.result:
            return

        return res_dict["result"][0:3]


    # The following method gets not only hosts info but also host group membership.
    def get_hosts(self):
        params = {"output":"extend", "selectGroups":"refer", "monitored_hosts":True}
        res_dict = get_response_dict("hosts.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        hosts = []
        host_group_membership = []
        for host in res_dict["result"]:
            hosts.append({"hostId":host["hostid"], "hostName":host["name"]})

            group_ids = []
            for groups in host["groups"]:
                group_ids.append(groups["groupid"])

            host_group_membership.append({"hostId":host["id"], "groupIds":group_ids})

        return (hosts, host_group_membership)


    def get_host_groups(self):
        params = {"output": "extend", "selectHosts": "refer", "real_hosts": True, "monitored_hosts": True}
        res_dict = get_response_dict("hostgroup.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        host_groups = []
        for host_group in res_dict["result"]:
            host_groups.append({"hostId": host_group["hostid"], "groupName": host_group["name"]})

        return host_groups


    def get_triggers(self, requestSince = None):
        params = {"output": ["extend", "description"], "monitored_hosts": True}
        if requestSince is not None:
            params["lastChangeSince"] = int(requestSince)

        res_dict = get_response_dict("trigger.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        triggers = []
        for trigger in res_dict["result"]:
            triggers.append({"triggerId": trigger["triggerid"],
                             "status": "OK",
                             "severity": trigger["priority"],
                             "lastChangeTime": translate_unix_time_to_hatohol_time(int(trigger["lastChange"])),
                             "hostId": trigger["hostid"],
                             "hostName": trigger["hostName"],
                             "brief": trigger["description"],
                             "extendedInfo": trigger["description"]})

        return triggers


    def get_events(self, event_id_from, event_id_till = None):
        params = {"output": "extend", "eventid_from": event_id_from}
        if event_id_till is not None:
            params["eventid_till"] = event_id_till

        res_dict = get_response_dict("evnet.get", params, self.auth_token)

        self.result = check_response(res_dict)
        if not self.result:
            return

        events = []
        for event in res_dict["result"]:
            events.append({"eventId": event["eventid"],
                           "time": translate_unix_time_to_hatohol_time(int(event["clock"]) + event["ns"]),
                           "type": EVENT_TYPE[event["value"]]
                           "status": TRIGGER_STATUS[event["value"]]
                           "triggerId": event["objectid"],


        return events


    def get_response_dict(self, method_name, params, auth_token = None):
        post = json.dumps({"jsonrpc": "2.0", "method": method_name, "params": params, "auth": self.auth_token, "id": 1})
        request = urllib2.Request(self.url, post, HEADER)
        response = urllib2.urlopen(request)
        res_str = response.read()

        return json.loads(res_str)


def check_response(response_dict):
    if "error" in response_dict:
        return False

    return True
