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
import cPickle
import base64

class Common:

    STATUS_MAP = {"ok": "OK", "insufficient data": "UNKNOWN", "alarm": "NG"}
    STATUS_EVENT_MAP = {"OK": "GOOD", "NG": "BAD", "UNKNOWN": "UNKNOWN"}

    def __init__(self):
        self.close_connection()

    def close_connection(self):
        self.__token = None
        self.__nova_ep = None
        self.__ceilometer_ep = None
        self.__host_cache = {} # key: host_id, value: host_name
        self.__alarm_cache = {} # key: alarm_id, value: {host_id, brief}

         # key: alarm_id, value: last_alarm time (HAPI format)
        self.__alarm_last_time_map = {}

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
        response = self.__request(url)

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
        response = self.__request(url)

        # Now we get all the alarms. So the list shoud be cleared here
        self.__alarm_cache = {}
        triggers = []
        for alarm in response:
            alarm_id = alarm["alarm_id"]
            threshold_rule = alarm["threshold_rule"]
            meter_name = threshold_rule["meter_name"]
            ts = datetime.datetime.strptime(alarm["state_timestamp"],
                                            "%Y-%m-%dT%H:%M:%S.%f")
            timestamp_str = ts.strftime("%Y%m%d%H%M%S.") + str(ts.microsecond)

            host_id, host_name = self.__parse_alarm_host(threshold_rule)
            brief = "%s: %s" % (meter_name, alarm["description"]),
            trigger = {
                "triggerId": alarm["alarm_id"],
                "status": self.STATUS_MAP[alarm["state"]],
                "severity": "ERROR",
                "lastChangeTime": timestamp_str,
                "hostId": host_id,
                "hostName": host_name,
                "brief": brief,
                "extendedInfo": "",
            }
            triggers.append(trigger)
            self.__alarm_cache[alarm_id] = {
                "host_id": host_id, "brief": brief}
        update_type = "ALL"
        self.put_triggers(triggers, update_type=update_type, fetch_id=fetch_id)

    def collect_events_and_put(self, fetch_id=None, last_info=None,
                               count=None, direction="ASC"):
        if last_info is None:
            last_info = self.get_cached_event_last_info()
        # TODO: validate raw_last_info

        for alarm_id in self.__alarm_cache.keys():
            last_alarm_time = self.__get_last_alarm_time(alarm_id, last_info)
            self.__collect_events_and_put(alarm_id, last_alarm_time, fetch_id)

    def collect_items_and_put(self, fetch_id, host_ids):
        assert False, "Not implemented"

    def collect_items_and_put(self, fetch_id, host_id, item_id,
                              begin_time, end_time):
        assert False, "Not implemented"

    def __get_last_alarm_time(self, alarm_id, last_info):
        if last_info is None:
            return None
        try:
            pickled = base64.b64decode(last_info)
            last_alarm_timestamp_map = cPickle.loads(pickled)
        except Exception as e:
            logging.error("Failed to decode: %s."  % e)
            return None
        return last_alarm_timestamp_map.get(alarm_id)

    def __collect_events_and_put(self, alarm_id, last_alarm_time, fetch_id):
        query_option = self.__get_history_query_option(last_alarm_time)
        url = self.__ceilometer_ep + \
              "/v2/alarms/%s/history%s" % (alarm_id, query_option)
        response = self.__request(url)

        # host_id, host_name and brief
        alarm_cache = self.__alarm_cache.get(alarm_id)
        if alarm_cache is not None:
            host_id = alarm_cache["host_id"]
            brief = alarm_cache["brief"]
        else:
            host_id = "N/A"
            brief = "N/A"
        host_name = self.__host_cache.get(host_id, "N/A")

        # make the events to put
        events = []
        for history in response:
            hapi_status = self.alarm_to_hapi_status(
                        history["type"], history.get("detail"))
            hapi_event_type = self.status_to_hapi_event_type(hapi_status)
            timestamp = self.parse_time(history["timestamp"])

            events.append({
                "eventId": history["event_id"],
                "time": haplib.Utils.conv_to_hapi_time(timestamp),
                "type": hapi_event_type,
                "triggerId": alarm_id,
                "status": hapi_status,
                "severity": "ERROR",
                "hostId": host_id,
                "hostName": host_name,
                "brief": brief,
                "extendedInfo": ""
            })
        # TODO: we have to sort events in time asc order
        self.put_events(events, fetch_id=fetch_id,
                        last_info_generator=self.__last_info_generator)

    def __last_info_generator(self, events):
        # TODO: check the alarms that are no longer existing and remove them
        for evt in events:
            alarm_id = evt["triggerId"]
            alarm_time = evt["time"]

            doUpdate = True
            latest_time = self.__alarm_last_time_map.get(alarm_id)
            if latest_time is not None:
                # TODO: FIX: This is too easy and imprecise
                doUpdate = float(alarm_time) > float(latest_time)
            if doUpdate:
                self.__alarm_last_time_map[alarm_id] = alarm_time

        pickled = cPickle.dumps(self.__alarm_last_time_map)
        b64enc = base64.b64encode(pickled)
        assert len(b64enc) <= haplib.MAX_LAST_INFO_SIZE
        return b64enc

    def __get_history_query_option(self, last_alarm_time):
        if last_alarm_time is None:
            return ""
        time_value = self.hapi_time_to_url_enc_openstack_time(last_alarm_time)
        return "?q.field=timestamp&q.op=gt&q.value=%s" % time_value

    @staticmethod
    def hapi_time_to_url_enc_openstack_time(hapi_time):
        year  = hapi_time[0:4]
        month = hapi_time[4:6]
        day   = hapi_time[6:8]
        hour  = hapi_time[8:10]
        min   = hapi_time[10:12]
        sec   = hapi_time[12:14]
        if hapi_time[14:15] == ".":
            frac_len = len(hapi_time) - 15
            zero_pads = "".join(["0" for i in range(0, 6 - frac_len)])
            microsec = hapi_time[15:21] + zero_pads
        else:
            microsec = "000000"

        return "%04s-%02s-%02sT%02s%%3A%02s%%3A%02s.%s" % \
               (year, month, day, hour, min, sec, microsec)

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

    @classmethod
    def alarm_to_hapi_status(cls, alarm_type, detail_json):
        assert alarm_type == "creation" or alarm_type == "state transition"
        detail = json.loads(detail_json)
        state = detail["state"]
        return cls.STATUS_MAP[state]

    @classmethod
    def status_to_hapi_event_type(cls, hapi_status):
        return cls.STATUS_EVENT_MAP[hapi_status]

    @staticmethod
    def parse_time(time):
        """
        Parse time strings returned from OpenStack.

        @param time
        A time string such as
        - 2014-09-05T06:25:26.007000
        - 2014-09-05T06:25:26

        @return A datetime object.
        """

        EXPECT_LEN_WITHOUT_MICRO = 19
        EXPECT_LEN_WITH_MICRO = EXPECT_LEN_WITHOUT_MICRO + 7
        formats = {
            EXPECT_LEN_WITHOUT_MICRO: "%Y-%m-%dT%H:%M:%S",
            EXPECT_LEN_WITH_MICRO: "%Y-%m-%dT%H:%M:%S.%f",
        }
        return datetime.datetime.strptime(time, formats[len(time)])


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
        self.collect_items_and_put(params["fetchId"], params["hostIds"])

    def hap_fetch_history(self, params, request_id):
        self.collect_history_and_put(params["fetchId"],
                                     params["hostId"], params["itemId"],
                                     params["beginTime"], params["endTime"])


class Hap2Ceilometer(standardhap.StandardHap):
    def create_main_plugin(self, *args, **kwargs):
        return Hap2CeilometerMain(*args, **kwargs)

    def create_poller(self, *args, **kwargs):
        return Hap2CeilometerPoller(self, *args, **kwargs)


if __name__ == '__main__':
    hap = Hap2Ceilometer()
    hap()
