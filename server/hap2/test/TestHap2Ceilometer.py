#!/usr/bin/env python
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
import unittest
import common as testutils
from hap2_ceilometer import Common
from datetime import datetime
import haplib
import re

class CommonForTest(Common):

    NOVA_EP = "http://hoge/nova"
    CEILOMETER_EP = "http://hoge/ceilometer"

    SERVERS = [{
        "id": "12345",
        "name": "onamae",
    }]

    ALARMS = [{
        "alarm_id": "112233",
        "state_timestamp": "2015-06-29T10:05:11.135000",
        "description": "DESCRIPTION",
        "state": "ok",
        "threshold_rule": {
            "meter_name": "cpu_util",
            "query": [{
                "field": "name",
                "value": "889900",
                "op": "eq",
            }]
        },
    }]


    EXPECT_ITEM_HOST_ID1_CNAME = {
        "itemId": "host_id1.CNAME",
        "hostId": "host_id1",
        "brief": "CNAME",
        "lastValueTime": "19940525123456.000000",
        "lastValue": "CVOL",
        "itemGroupName": "",
        "unit": "UNIT",
    }

    def __init__(self, options={}):
        Common.__init__(self)
        self.__options = options
        self.store = {}

        # replace a lower layer method
        self._Common__request = self.__request

    def get_ms_info(self):
        if self.__options.get("none_monitoring_server_info"):
            return None
        return haplib.MonitoringServerInfo({
            "serverId": 51,
            "url": "http://example.com",
            "type": "Ceilometer",
            "nickName": "Jack",
            "userName": "fooo",
            "password": "gooo",
            "pollingIntervalSec": 30,
            "retryIntervalSec": 10,
            "extendedInfo": '{"tenantName": "yah"}',
        })

    def put_hosts(self, hosts):
        self.store["hosts"] = hosts

    def put_triggers(self, triggers, update_type,
                     last_info=None, fetch_id=None):
        self.store["triggers"] = triggers
        self.store["update_type"] = update_type
        self.store["last_info"] = last_info
        self.store["fetch_id"] = fetch_id

    def put_events(self, events, fetch_id=None, last_info_generator=None):
        self.store["events"] = events
        self.store["fetch_id"] = fetch_id
        self.store["last_info_generator"] = last_info_generator

    def __request(self, url, headers={}, use_token=True, data=None):
        url_handler_map = {
            "http://example.com/tokens": self.__request_token,
            self.NOVA_EP + "/servers": self.__request_servers,
            "http://hoge/ceilometer/v2/alarms": self.__request_alarms,
            "http://hoge/ceilometer/v2/resource": self.__request_resources,
            "http://HREF/href1": self.__request_href1,
            "http://hoge/ceilometer/v2/meters/CNAME":
                self.__request_meters_CNAME,
        }

        handler = None
        for key, func in url_handler_map.items():
            if re.search(key, url):
                handler = func
                break
        else:
            raise Exception("Not found handler for %s" % url)
        return handler(url)

    def __request_token(self, url):
        return {
            "access": {
                "token": {
                    "id": "xxxxxxxxxxxxxxxx",
                    "expires": "2015-06-29T16:54:23Z",
                },
                "serviceCatalog": [{
                    "name": "nova",
                    "endpoints": [{"publicURL": self.NOVA_EP}],
                }, {
                    "name": "ceilometer",
                    "endpoints": [{"publicURL": self.CEILOMETER_EP}],
                }]
            }
        }

    def __request_servers(self, url):
        return {
            "servers": self.SERVERS,
        }

    def __request_alarms(self, url):
        return self.ALARMS

    def __request_resources(self, url):
        return {
            "links": [{
                "rel": "cpu_util",
                "href": "http://HREF/href1",
            }],
        }

    def __request_href1(self, url):
        num_items = self.__options.get("href1_num_items", 1)
        items = [{
            "timestamp": "1994-05-25T12:34:56",
            "counter_name": "CNAME",
            "counter_volume": "CVOL",
            "counter_unit": "UNIT",
        }, {
            "timestamp": "1997-01-22T22:33:44",
            "counter_name": "Flower",
            "counter_volume": 13.20,
            "counter_unit": "%",
        }, {
            "timestamp": "1992-08-20T11:22:33",
            "counter_name": "Lake",
            "counter_volume": 123,
            "counter_unit": "degree",
        }]
        return items[0:num_items]

    def __request_meters_CNAME(self, url):
        return [{
            "timestamp": "2012-12-19T01:23:46",
            "counter_volume": 12,
        }, {
            "timestamp": "2012-12-19T01:23:45",
            "counter_volume": 10,
        }]

    def get_cached_event_last_info(self):
        return "abcdef"

    def put_items(self, items, fetch_id):
        self.store["items"] = items
        self.store["fetch_id"] = fetch_id

    def put_history(self, samples, item_id, fetch_id):
        self.store["samples"] = samples
        self.store["item_id"] = item_id
        self.store["fetch_id"] = fetch_id


class TestCommon(unittest.TestCase):
    def test_constructor(self):
        testutils.assertNotRaises(Common)

    def test_ensure_connection_without_monitoring_server_info(self):
        options = {"none_monitoring_server_info": True}
        comm = CommonForTest(options)
        self.assertRaises(haplib.Signal, comm.ensure_connection)

    def test_ensure_connection(self):
        options = {}
        comm = CommonForTest(options)
        comm.ensure_connection()
        nova_ep = testutils.returnPrivObj(comm, "__nova_ep", "Common")
        self.assertEqual(nova_ep, comm.NOVA_EP)
        ceilometer_ep = \
            testutils.returnPrivObj(comm, "__ceilometer_ep", "Common")
        self.assertEqual(ceilometer_ep, comm.CEILOMETER_EP)

    # skip tests for __set_nova_ep and __set_ceilometer_ep, because theya are
    # private and used in ensure_connection().

    def test_collect_hosts_and_put(self):
        comm = CommonForTest()
        comm.ensure_connection()
        comm.collect_hosts_and_put()
        hosts = comm.store["hosts"]
        self.assertEqual(hosts, [{"hostId": "12345", "hostName": "onamae"}])

    def test_collect_triggers_and_put(self):
        comm = CommonForTest()
        comm.ensure_connection()

        fetch_id = "000111"
        # TODO: Test with non-None host_ids
        host_ids = None
        comm.collect_triggers_and_put(fetch_id=fetch_id, host_ids=host_ids)
        self.assertEqual(comm.store["triggers"],
            [{
                "triggerId": "112233",
                "status": "OK",
                "severity": "ERROR",
                "lastChangeTime": "20150629100511.135000",
                "hostId": "889900",
                "hostName": "N/A",
                "brief": "cpu_util: DESCRIPTION",
                "extendedInfo": "",
             }])
        self.assertEquals(comm.store["update_type"], "ALL")
        self.assertEquals(comm.store["last_info"], None)
        self.assertEquals(comm.store["fetch_id"], fetch_id)

    def test_collect_events_and_put(self):
        caught = []
        def catcher(alarm_id, last_alarm_time, fetch_id):
            caught.extend([alarm_id, last_alarm_time, fetch_id])

        comm = CommonForTest()
        comm.ensure_connection()
        fetch_id = "000111"
        # TODO: Test with non-None host_ids, last_info, count
        last_info = None
        host_ids = None
        count = None
        # TODO: Test with "DESC"
        direction = "ASC"
        comm._Common__collect_events_and_put = catcher
        comm._Common__decode_last_alarm_timestamp_map = \
            lambda x: {"alarm_id1": "20150629110435.250000"}
        comm._Common__alarm_cache = {"alarm_id1": {"host id", "brief"}}
        comm.collect_events_and_put(fetch_id=fetch_id,
                                    last_info=last_info,
                                    count=count, direction=direction)
        self.assertEqual(caught,
                         ["alarm_id1", "20150629110435.250000", "000111"])


    def test_collect_items_and_put(self):
        comm = CommonForTest()
        comm.ensure_connection()
        # TODO: Test with non-None host_ids
        fetch_id = "000111"
        host_ids = ["host_id1"]
        comm.collect_items_and_put(fetch_id, host_ids)
        self.assertEquals(comm.store["items"], [
            {
                "itemId": "host_id1.CNAME",
                "hostId": "host_id1",
                "brief": "CNAME",
                "lastValueTime": "19940525123456.000000",
                "lastValue": "CVOL",
                "itemGroupName": "",
                "unit": "UNIT",
            }
        ])
        self.assertEquals(comm.store["fetch_id"], fetch_id)

    def test_collect_history_and_put(self):
        comm = CommonForTest()
        comm.ensure_connection()
        fetch_id = "0055"
        host_id = "host_id1"
        item_id = "host_id1.CNAME"
        # TODO: Set the proper time range
        begin_time = ""
        end_time = ""
        comm.collect_history_and_put(fetch_id=fetch_id, host_id=host_id,
                                     item_id=item_id, begin_time=begin_time,
                                     end_time=end_time)
        self.assertEquals(comm.store["fetch_id"], fetch_id)
        self.assertEquals(comm.store["item_id"], item_id)
        self.assertEquals(comm.store["samples"], [
            {
                "time": "20121219012345.000000",
                "value": "10",
            }, {
                "time": "20121219012346.000000",
                "value": "12",
            }
        ])

    def test__collect_items_and_put(self):
        comm = CommonForTest()
        comm.ensure_connection()
        host_id = "host_id2"
        target_func = \
            testutils.returnPrivObj(comm, "__collect_items_and_put", "Common")
        expect_item = comm.EXPECT_ITEM_HOST_ID1_CNAME
        expect_item["itemId"] = "host_id2.CNAME"
        expect_item["hostId"] = host_id
        self.assertEquals(target_func(host_id), [expect_item])

    def test_get_resource(self):
        comm = CommonForTest()
        get_resource = \
            testutils.returnPrivObj(comm, "__get_resource", "Common")
        rel = None
        href = "http://HREF/href1"
        self.assertEquals(get_resource(rel, href), {
            "timestamp": "1994-05-25T12:34:56",
            "counter_name": "CNAME",
            "counter_unit": "UNIT",
            "counter_volume": "CVOL"
        })

    def test_parse_time_with_micro(self):
        actual = Common.parse_time("2014-09-05T06:25:29.185000")
        expect = datetime(2014, 9, 5, 6, 25, 29, 185000)
        self.assertEqual(actual, expect)

    def test_parse_time_without_micro(self):
        actual = Common.parse_time("2014-09-05T06:25:29")
        expect = datetime(2014, 9, 5, 6, 25, 29)
        self.assertEqual(actual, expect)

    def test_parse_time_without_invalid_string(self):
        self.assertRaises(Exception, Common.parse_time, "20140905062529")

    def test_alarm_to_hapi_status_ok(self):
        alarm_type = "state transition"
        detail = '{"state": "ok"}'
        evt_type = Common.alarm_to_hapi_status(alarm_type, detail)
        self.assertEqual(evt_type, "OK")

    def test_alarm_to_hapi_status_ng(self):
        alarm_type = "state transition"
        detail = '{"state": "alarm"}'
        evt_type = Common.alarm_to_hapi_status(alarm_type, detail)
        self.assertEqual(evt_type, "NG")

    def test_alarm_to_hapi_status_unknown(self):
        alarm_type = "state transition"
        detail = '{"state": "insufficient data"}'
        evt_type = Common.alarm_to_hapi_status(alarm_type, detail)
        self.assertEqual(evt_type, "UNKNOWN")

    def test_alarm_to_hapi_status_creation(self):
        alarm_type = "creation"
        detail = '{"state": "ok"}'
        evt_type = Common.alarm_to_hapi_status(alarm_type, detail)
        self.assertEqual(evt_type, "OK")

    def test_alarm_to_hapi_status_with_invalid_type(self):
        alarm_type = "unknown type"
        detail = '{"state": "ok"}'
        self.assertRaises(
            Exception,
            Common.alarm_to_hapi_status, (alarm_type, detail))

    def test_alarm_to_hapi_status_with_invalid_detail(self):
        alarm_type = "state transition"
        detail = '{"state": "Cho Cho II kanji"}'
        self.assertRaises(
            Exception,
            Common.alarm_to_hapi_status, (alarm_type, detail))

    def test_hapi_time_to_url_enc_openstack_time(self):
        hapi_time = "20150624081005"
        actual = Common.hapi_time_to_url_enc_openstack_time(hapi_time)
        expect = "2015-06-24T08%3A10%3A05.000000"
        self.assertEqual(actual, expect)

    def test_hapi_time_to_url_enc_openstack_time_with_us(self):
        hapi_time = "20150624081005.123456"
        actual = Common.hapi_time_to_url_enc_openstack_time(hapi_time)
        expect = "2015-06-24T08%3A10%3A05.123456"
        self.assertEqual(actual, expect)

    def test_hapi_time_to_url_enc_openstack_time_with_ns(self):
        hapi_time = "20150624081005.123456789"
        actual = Common.hapi_time_to_url_enc_openstack_time(hapi_time)
        expect = "2015-06-24T08%3A10%3A05.123456"
        self.assertEqual(actual, expect)

    def test_hapi_time_to_url_enc_openstack_time_with_ms(self):
        hapi_time = "20150624081005.123"
        actual = Common.hapi_time_to_url_enc_openstack_time(hapi_time)
        expect = "2015-06-24T08%3A10%3A05.123000"
        self.assertEqual(actual, expect)

    def test_hapi_time_to_url_enc_openstack_time_with_dot_only(self):
        hapi_time = "20150624081005."
        actual = Common.hapi_time_to_url_enc_openstack_time(hapi_time)
        expect = "2015-06-24T08%3A10%3A05.000000"
        self.assertEqual(actual, expect)
