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
import time
import haplib
import standardhap
import logging
import urllib2
import json
import datetime

class Common:

    STATUS_MAP = {"ok": "OK", "insufficient data": "UNKNOWN", "alarm": "NG"}

    def __init__(self):
        self.close_connection()

    def close_connection(self):
        self.__token = None
        self.__nova_ep = None
        self.__ceilometer_ep = None
        self.__host_cache = {}

    def ensure_connection(self):
        if self.__token is not None:
            RETOKEN_MARGIN = datetime.timedelta(minutes=5)
            now  = datetime.datetime.utcnow()
            if self.__expires - now > RETOKEN_MARGIN:
                return

        self.__ms_info = self.get_ms_info()
        ms_info = self.__ms_info
        if ms_info is None:
            logging.error("Not found: MonitoringServerInfo.")
            raise haplib.Signal()

        auth_url = ms_info.url + "/tokens"
        ext_info_type = haplib.MonitoringServerInfo.EXTENDED_INFO_JSON
        ext_info = ms_info.get_extended_info(ext_info_type)
        data = {
            "auth": {
                "tenantName": ext_info["tenantName"],
                "passwordCredentials": {
                    "username": ms_info.user_name,
                    "password": ms_info.password,
                }
            }
        }
        headers = {"Content-Type": "application/json"}
        response = self.__request(auth_url, headers, use_token=False,
                                  data=json.dumps(data))

        self.__token = response["access"]["token"]["id"]
        expires = response["access"]["token"]["expires"]
        self.__expires = datetime.datetime.strptime(expires,
                                                    "%Y-%m-%dT%H:%M:%SZ")
        logging.info("Got token, expires: %s" % self.__expires)

        # Extract endpoints
        target_eps = {"nova": self.__set_nova_ep,
                      "ceilometer": self.__set_ceilometer_ep}
        for catalog in response["access"]["serviceCatalog"]:
            if len(target_eps) == 0:
                break
            name = catalog["name"]
            ep_setter = target_eps.get(name)
            if ep_setter is None:
                continue
            ep_setter(catalog["endpoints"][0]["publicURL"])
            del target_eps[name]

        if len(target_eps) > 0:
            logging.error("Not found Endpoints: Nova: %s, Ceiloemeter: %s" % \
                          self.__nova_ep, self.__ceilometer_ep)
            raise haplib.Signal()

        logging.info("EP: Nova: %s", self.__nova_ep)
        logging.info("EP: Ceiloemeter: %s", self.__ceilometer_ep)

    def __set_nova_ep(self, ep):
        self.__nova_ep = ep

    def __set_ceilometer_ep(self, ep):
        self.__ceilometer_ep = ep

    def collect_hosts_and_put(self):
        url = self.__nova_ep + "/servers/detail?all_tenants=1"
        headers = {"X-Auth-Token": self.__token}
        response = self.__request(url, headers)

        hosts = []
        for server in response["servers"]:
            host_id = server["id"]
            host_name = server["name"]
            hosts.append({"hostId": host_id, "hostName": host_name})
            self.__host_cache[host_id] = host_name
        self.put_hosts(hosts)

    def collect_host_groups_and_put(self):
        pass

    def collect_host_group_membership_and_put(self):
        pass

    def collect_triggers_and_put(self, fetch_id=None, host_ids=None):

        # TODO: Take care of host_ids

        url = self.__ceilometer_ep + "/v2/alarms";
        headers = {"X-Auth-Token": self.__token}
        response = self.__request(url, headers)

        triggers = []
        for alarm in response:
            threshold_rule = alarm["threshold_rule"]
            meter_name = threshold_rule["meter_name"]
            ts = datetime.datetime.strptime(alarm["state_timestamp"],
                                            "%Y-%m-%dT%H:%M:%S.%f")
            timestamp_str = ts.strftime("%Y%m%d%H%M%S.") + str(ts.microsecond)

            host_id, host_name = self.__parse_alarm_host(threshold_rule)
            trigger = {
                "triggerId": alarm["alarm_id"],
                "status": self.STATUS_MAP[alarm["state"]],
                "severity": "ERROR",
                "lastChangeTime": timestamp_str,
                "hostId": host_id,
                "hostName": host_name,
                "brief": "%s: %s" % (meter_name, alarm["description"]),
                "extendedInfo": "",
            }
            triggers.append(trigger)
        update_type = "ALL"
        self.put_triggers(triggers, update_type=update_type, fetch_id=fetch_id)

    def collect_events_and_put(self, fetch_id=None, last_info=None,
                               count=None, direction="ASC"):
        pass

    def __request(self, url, headers={}, use_token=True, data=None):
        if use_token:
            headers["X-Auth-Token"] = self.__token
        request = urllib2.Request(url, headers=headers, data=data)
        raw_response = urllib2.urlopen(request).read()
        return json.loads(raw_response)

    def __parse_alarm_host(self, threshold_rule):
        query_array = threshold_rule.get("query")
        if query_array is None:
            return "N/A", "N/A"

        for query in query_array:
            host_id = self.__parse_alarm_host_each(query)
            if host_id is not None:
                break
        else:
            return "N/A", "N/A"

        host_name = self.__host_cache.get(host_id, "N/A")
        return host_id, host_name

    def __parse_alarm_host_each(self, query):
        field = query.get("field")
        if field is None:
            return None
        value = query.get("value")
        if value is None:
            return None
        op = query.get("op")
        if value is None:
            return None
        if op != "eq":
            logger.info("Unknown eperator: %s" % op)
            return None
        return value


class Hap2CeilometerPoller(haplib.BasePoller, Common):

    def __init__(self, *args, **kwargs):
        haplib.BasePoller.__init__(self, *args, **kwargs)
        Common.__init__(self)

    def poll_setup(self):
        self.ensure_connection()

    def poll_hosts(self):
        self.collect_hosts_and_put()

    def poll_host_groups(self):
        self.collect_host_groups_and_put()

    def poll_host_group_membership(self):
        self.collect_host_group_membership_and_put()

    def poll_triggers(self):
        self.collect_triggers_and_put()

    def poll_events(self):
        self.collect_events_and_put()

    def on_aborted_poll(self):
        self.reset()
        self.close_connection()


class Hap2CeilometerMain(haplib.BaseMainPlugin, Common):
    def __init__(self, *args, **kwargs):
        haplib.BaseMainPlugin.__init__(self, kwargs["transporter_args"])
        Common.__init__(self)

    def hap_fetch_triggers(self, params, request_id):
        self.ensure_connection()
        fetch_id = params["fetchId"]
        host_ids = params["hostIds"]
        self.collect_triggers_and_put(fetch_id, host_ids)

    def hap_fetch_events(self, params, request_id):
        self.ensure_connection()
        self.collect_events_and_put(params["fetchId"], params["lastInfo"],
                                    params["count"], params["direction"])

    def hap_fetch_items(self, params, request_id):
        logging.error("Not implemented")

    def hap_fetch_items(self, params, request_id):
        logging.error("Not implemented")


class Hap2Ceilometer(standardhap.StandardHap):
    def create_main_plugin(self, *args, **kwargs):
        return Hap2CeilometerMain(*args, **kwargs)

    def create_poller(self, *args, **kwargs):
        return Hap2CeilometerPoller(self, *args, **kwargs)


if __name__ == '__main__':
    hap = Hap2Ceilometer()
    hap()
