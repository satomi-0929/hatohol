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
import multiprocessing
import json
import Queue
import logging
import haplib
import transporter
from haplib import HAPUtils

class TestHaplib(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_queue = multiprocessing.JoinableQueue()

    def test_send_request_to_queue(self):
        test_sender = SenderForTest(self.test_queue, True)
        self._assertNotRaises(test_sender.send_request_to_queue,
                              "test_procedure_name", "test_param", 1)

    def test_send_response_to_queue(self):
        test_sender = SenderForTest(self.test_queue, True)
        self._assertNotRaises(test_sender.send_response_to_queue,
                              "test_result", 1)

    def test_send_error_to_queue(self):
        test_sender = SenderForTest(self.test_queue, True)
        self._assertNotRaises(test_sender.send_error_to_queue, -32700, 1)

    def test_get_response_and_check_id(self):
        test_sender = SenderForTest(self.test_queue)
        exact_result = "test_result"
        exact_id = 1
        self.test_queue.put({"id": exact_id, "result": exact_result})
        self.test_queue.task_done()
        output = test_sender.get_response_and_check_id(exact_id)

        self.assertEquals(output, exact_result)

    def test_get_response_and_check_id_timeout(self):
        test_sender = SenderForTest(self.test_queue)
        exact_result = "test_result"
        test_id = 1
        # Wait 30 seconds
        output = test_sender.get_response_and_check_id(test_id)

        self.assertIsNone(output)

    def test_get_monitoring_server_info(self):
        test_sender = SenderForTest(self.test_queue, True)
        self._assertNotRaises(test_sender.get_monitoring_server_info)

    def test_get_last_info(self):
        test_sender = SenderForTest(self.test_queue, True)
        self._assertNotRaises(test_sender.get_last_info, "test_element")

    def test_exchange_profile_request(self):
        test_sender = SenderForTest(self.test_queue, True)
        self._assertNotRaises(test_sender.exchange_profile, "test_params")

    def test_exchange_profile_response(self):
        test_sender = SenderForTest(self.test_queue, True)
        self._assertNotRaises(test_sender.exchange_profile, "test_params", 1)

    def test_udpate_arm_info(self):
        test_sender = SenderForTest(self.test_queue, True)
        test_arm_info = haplib.ArmInfo()
        self._assertNotRaises(test_sender.update_arm_info, test_arm_info)

# The above tests is HAPBaseSender tests.
# The following tests is HAPBaseReceiver tests.

    def test_message_manager_poller(self):
        test_receiver = ReceiverForTest()
        test_receiver.poller_queue.put(set[1])
        test_json_string = '{"id":1}'
        exact_json_dict = json.loads(test_json_string)
        self._assertNotRaises(test_receiver.message_manager, None,
                              test_json_string)
        result = test_receiver.poller_queue.get()

        self.assertEquals(exact_json_dict, result)

    def test_message_manager_main_response(self):
        test_receiver = ReceiverForTest()
        test_receiver.main_response_queue(set[1])
        test_json_string = '{"id":1}'
        exact_json_dict = json.loads(test_json_string)
        self._assertNotRaises(test_receiver.message_manager, None,
                              test_json_string)
        result = test_receiver.main_response_queue.get()

        self.assertEquals(exact_json_dict, result)

    def test_message_manager_main_request(self):
        test_receiver = ReceiverForTest()
        test_receiver.main_request_queue = multiprocessing.JoinableQueue()
        test_json_string = '{"id":1}'
        exact_json_dict = json.loads(test_json_string)
        self._assertNotRaises(test_receiver.message_manager, None,
                              test_json_string)
        result = test_receiver.main_request_queue.get()

        self.assertEquals(exact_json_dict, result)

    def test_message_manager_main_notification(self):
        test_receiver = ReceiverForTest()
        test_receiver.main_request_queue = multiprocessing.JoinableQueue()
        test_json_string = '{"notification":"test"}'
        exact_json_dict = json.loads(test_json_string)
        self._assertNotRaises(test_receiver.message_manager, None,
                              test_json_string)
        result = test_receiver.main_request_queue.get()

        self.assertEquals(exact_json_dict, result)


# The above tests is HAPBaseReceiver tests.
# The following tests is HAPBaseMainPlugin tests.

    def test_hap_exchange_profile(self):
        test_main_plugin = MainPluginForTest(self.test_queue)
        self._assertNotRaises(test_main_plugin.hap_exchange_profile,
                              ["exchangeProfile",], 1)

    def test_get_request_loop(self):
        test_main_plugin = MainPluginForTest(self.test_queue)
        self.test_queue.put({"method":"exchangeProfile", "id":1, "params":{"procedures": ["exchangeProfile"], "name":"test_name"}})
        try:
            test_main_plugin.get_sender().get_connector().set_finish_reply()
            test_main_plugin.get_request_loop()
        except Exception as exception:
            self.assertEquals("finish", exception)

# The above tests is HAPBaseMainPlugin tests.
# The following tests is HAPUtils tests.

    def test_check_message_invalid_json(self):
        test_message = "invalid_message"
        result = HAPUtils.check_message(test_message, None)

        self.assertEquals((-32700, None), result)

    def test_check_message_not_implement(self):
        test_message = '{"method": "test_procedure", "params": "test_params", "id": 1, "jsonrpc": "2.0"}'
        result = HAPUtils.check_message(test_message, ["exchangeProfile"])

        self.assertEquals((-32601, 1), result)

    def test_check_message_invalid_argument(self):
        test_message = '{"method": "exchangeProfile", "params": {"name":1, "procedures":"test"}, "id": 1, "jsonrpc": "2.0"}'
        result = HAPUtils.check_message(test_message, ["exchangeProfile"])

        self.assertEquals((-32602, 1), result)

    def test_check_message_valid_json(self):
        test_message = '{"method": "exchangeProfile", "params": {"name":"test_name", "procedures":["exchangeProfile"]}, "id": 1, "jsonrpc": "2.0"}'
        result = HAPUtils.check_message(test_message, ["exchangeProfile"])

        exact_dict = json.loads(test_message)
        self.assertEquals(exact_dict,result)

    def test_check_message_response(self):
        test_message = '{"result":"test_result","id":1,"jsonrpc": "2.0"}'
        result = HAPUtils.check_message(test_message, ["exchangeProfile"])

        exact_dict = json.loads(test_message)
        self.assertEquals(exact_dict,result)

    def test_convert_string_to_dict_success(self):
        test_json_string = '{"test_key":"test_value"}'

        exact_result = json.loads(test_json_string)
        unnesessary_result, result = HAPUtils.convert_string_to_dict(test_json_string)
        self.assertEquals(result, exact_result)

    def test_convert_string_to_dict_failure(self):
        test_json_string = '{"test_key": test_value}'

        exact_result = (-32700, None)
        result = HAPUtils.convert_string_to_dict(test_json_string)
        self.assertEquals(result, exact_result)

    def test_check_procedures_is_implemented_success(self):
        result = HAPUtils.check_procedure_is_implemented("exchangeProfile", ["exchangeProfile"])
        self.assertIsNone(result)

    def test_check_procedures_is_implemented_failure(self):
        result = HAPUtils.check_procedure_is_implemented("test_procedure_name", ["exchangeProfile"])
        self.assertEquals(result, -32601)

    def check_argument_is_correct_success(self):
        test_json_string = '{"method": "exchangeProfile", "params": {"name":"test_name", "procedures":["exchangeProfile"]}}'
        test_json_dict = json.loads(test_json_string)
        result = HAPUtils.check_argument_is_correct(test_json_dict)
        self.assertIsNone(result)

    def check_argument_is_correct_failure(self):
        test_json_string = '{"method": "exchangeProfile", "params": {"name":"test_name", "procedures":"exchangeProfile"}}'
        test_json_dict = json.loads(test_json_string)
        result = HAPUtils.check_argument_is_correct(test_json_dict)
        self.assertEquals(result, -32602)

    def test_get_and_save_request_id(self):
        test_ids = set([])
        result = HAPUtils.get_and_save_request_id(test_ids)

        self.assertTrue(0 <= result <=2048)
        self.assertTrue(result in test_ids)

    def test_translate_unit_time_to_hatohol_time(self):
        result = HAPUtils.translate_unix_time_to_hatohol_time(0)
        self.assertEquals(result, "19700101090000.000000")

    def test_translate_hatohol_time_time_to_unix_time(self):
        result = HAPUtils.translate_hatohol_time_to_unix_time("19700101090000.000000")
        self.assertEquals(result, 0)

    def _assertNotRaises(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            raise

        if "exception" not in locals():
            exception = None

        self.assertIsNone(exception)


class SenderForTest(haplib.HAPBaseSender):

    def __init__(self, test_queue, change_get_response_and_check_id_flag=False):
        self.sender_queue = test_queue
        self.set_connector(ConnectorForTest(test_queue))
        self.requested_ids = set()

        if change_get_response_and_check_id_flag:
            def get_response_and_check_id(self):
                return

class ConnectorForTest(transporter.Transporter):

    def __init__(self, test_queue):
        self._test_queue = test_queue
        self._finish_reply = False

    def call(self, msg):
        self._test_queue.get()
        self._test_queue.task_done()
        self._test_queue.put({"id": 1, "result": None})
        self._test_queue.task_done()

    def reply(self, msg):
        # This raise is used in test_get_request_loop
        if self._finish_reply:
            raise Exception("finish")

    def set_receiver(self, receiver):
        return

    def set_finish_reply(self, value=True):
        self._finish_reply = value


class ReceiverForTest(haplib.HAPBaseReceiver):

    def __init__(self):
        self.main_response_queue = multiprocessing.JoinableQueue()
        self.main_request_queue = multiprocessing.JoinableQueue()
        self.poller_queue = multiprocessing.JoinableQueue()
        self.main_requested_ids = set()
        self.poller_requested_ids = set()
        self.implement_procedures = ["exchangeProfile"]


class MainPluginForTest(haplib.HAPBaseMainPlugin):

    def __init__(self, test_queue):
        self.main_request_queue = test_queue
        self.procedures = {"exchangeProfile": self.hap_exchange_profile}
        self.implement_procedures = ["exchangeProfile"]
        self.set_sender(SenderForTest(test_queue, True))
