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
import hapzabbix
import multiprocessing

from TestHAPLib import ConnectorForTest

class TestHAPZabbix(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_queue = multiprocessing.JoinableQueue()

    def test_hap_fetch_items(self):
        test_main_plugin = MainPluginForTest(self.test_queue)
        test_params = {"hostId": "1", "fetchId": 1}
        self._assertNotRaises(test_main_plugin.hap_fetch_items, test_params, 1)

    def test_hap_fetch_history(self):
        test_main_plugin = MainPluginForTest(self.test_queue)
        test_params = {"itemId": "1", "beginTime": None, "endTime": None, "fetchId": 1}
        self._assertNotRaises(test_main_plugin.hap_fetch_history, test_params, 1)

    def test_hap_fetch_triggers(self):
        test_main_plugin = MainPluginForTest(self.test_queue)
        test_params = {"hostId": ["1"], "fetchId": 1}
        self._assertNotRaises(test_main_plugin.hap_fetch_triggers, test_params, 1)

    def test_hap_fetch_events(self):
        test_main_plugin = MainPluginForTest(self.test_queue)
        test_params = {"lastInfo": 1, "count": 10, "direction": "ASC",
                       "fetchId": 1}
        self._assertNotRaises(test_main_plugin.hap_fetch_events, test_params, 1)

# The above tests is HAPZabbixMainPlugin tests.
# The following tests is HAPZabbixPoller tests.

    def test_update_lump(self):
        test_poller = PollerForTest(self.test_queue)
        self._assertNotRaises(test_poller.update_lump)

    def _assertNotRaises(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            raise


class SenderForTest(hapzabbix.HAPZabbixSender):

    def __init__(self, test_queue):
        self.set_connector(ConnectorForTest(test_queue))
        self.sender_queue = test_queue
        self.requested_ids = set([1])
        self.api = APIForTest()
        self.previous_hosts_info = hapzabbix.PreviousHostsInfo()
        self.trigger_last_info = None
        self.event_last_info = None

    def get_response_and_check_id(self, request_id):
        return


class MainPluginForTest(hapzabbix.HAPZabbixMainPlugin):

    def __init__(self, test_queue):
        self.sender = SenderForTest(test_queue)
        self.procedures = {"exchangeProfile": self.hap_exchange_profile,
                           "fetchItems": self.hap_fetch_items,
                           "fetchHistory": self.hap_fetch_history,
                           "fetchTriggers": self.hap_fetch_triggers,
                           "fetchEvents": self.hap_fetch_events}
        self.implement_procedures = ["fetchItems","fetchHistory",
                                     "fetchTriggers", "fetchEvents"]


class PollerForTest(hapzabbix.HAPZabbixPoller):

    def __init__(self, test_queue):
        self.sender = SenderForTest(test_queue)


class APIForTest:

    def get_items(self, host_id=None):
        test_items = [{"unit": "example unit",
                       "itemGroupName": "example name",
                       "lastValue": "example value",
                       "lastValueTime": "20150410175500",
                       "brief": "example brief",
                       "hostId": "1",
                       "itemId": "1"}]

        return test_items

    def get_history(self, item_id, begin_time, end_time):
        test_history = [{"time": "20150323113000", "value": "exampleValue"},
                        {"time": "20150323113012", "value": "exampleValue2"}]

        return test_history

    def get_hosts(self):
        test_hosts = [{"hostId": "1", "hostName": "test_host_name"}]
        test_host_group_membership = [{"hostId": "1", "groupIds": ["1", "2"]}]

        return (test_hosts, test_host_group_membership)

    def get_host_groups(self):
        test_host_groups = [{"groupId": "1", "groupName": "test_group"}]

        return test_host_groups

    def get_triggers(self, request_since=None, host_id=None):
        test_triggers = [{"extendedInfo": "sample extended info",
                          "brief": "example brief",
                          "hostName": "exampleName",
                          "hostId": "1",
                          "lastChangeTime": "20150323175800",
                          "severity": "INFO",
                          "status": "OK",
                          "triggerId": "1"}]

        return test_triggers

    def get_events(self, event_id_from, event_id_till=None):
        test_events = [{"extendedInfo": "sampel extended info",
                        "brief": "example brief",
                        "eventId": "1",
                        "time": "20150323151300",
                        "type": "GOOD",
                        "triggerId": 2,
                        "status": "OK",
                        "severity": "INFO",
                        "hostId": 3,
                        "hostName": "exampleName"}]

        return test_events
