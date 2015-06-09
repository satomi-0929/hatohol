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
import time
import argparse
from collections import namedtuple

import haplib
import transporter
from haplib import Utils

class TestHAPLib(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.__test_queue = multiprocessing.JoinableQueue()

    def test_get_connector(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        result_connector = test_sender.get_connector()
        self.assertEquals(test_sender._Sender__connector, result_connector)

    def test_set_connector(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        test_sender.set_connector("test")
        self.assertEquals("test", test_sender._Sender__connector)

    def test_request(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        self.__assertNotRaises(test_sender.request,
                              "test_procedure_name", "test_param", 1)

    def test_response(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        self.__assertNotRaises(test_sender.response,
                              "test_result", 1)

    def test_send_error_to_queue(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        self.__assertNotRaises(test_sender.send_error_to_queue, -32700, 1)

# The above tests is Sender tests.
# The following tests is HapiProcessor tests.

    def test_get_reply_queue(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        test_processor = haplib.HapiProcessor(test_sender, 0x01)
        result_queue = test_processor.get_reply_queue()
        exact_queue = self.__returnPrivObj(test_processor, "__reply_queue")
        self.assertEquals(result_queue, exact_queue)

    def test_get_monitoring_server_info(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        test_processor = haplib.HapiProcessor(test_sender, 0x01)
        test_connector = ConnectorForTest(test_processor.get_reply_queue())
        test_connector.enable_ms_flag()
        test_sender.set_connector(test_connector)
        self.__assertNotRaises(test_processor.get_monitoring_server_info)

    def test_get_last_info(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        test_processor = haplib.HapiProcessor(test_sender, 0x01)
        test_connector = ConnectorForTest(test_processor.get_reply_queue())
        test_sender.set_connector(test_connector)
        self.__assertNotRaises(test_processor.get_last_info, "test_element")

    def test_exchange_profile_request(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        test_processor = haplib.HapiProcessor(test_sender, 0x01)
        test_connector = ConnectorForTest(test_processor.get_reply_queue())
        test_sender.set_connector(test_connector)
        self.__assertNotRaises(test_processor.exchange_profile, "test_params")

    def test_exchange_profile_response(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        test_processor = haplib.HapiProcessor(test_sender, 0x01)
        self.__assertNotRaises(test_processor.exchange_profile, "test_params", 1)

    def test_udpate_arm_info(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        test_processor = haplib.HapiProcessor(test_sender, 0x01)
        test_connector = ConnectorForTest(test_processor.get_reply_queue())
        test_sender.set_connector(test_connector)
        test_arm_info = haplib.ArmInfo()
        self.__assertNotRaises(test_processor.update_arm_info, test_arm_info)
    def test_wait_response(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        test_processor = ProcessorForTest(test_sender, 0x01)
        exact_result = "test_result"
        exact_id = 1
        reply_queue = test_processor.get_reply_queue()
        reply_queue.put({"id": exact_id, "result": exact_result})
        reply_queue.task_done()
        output = test_processor.wait_response(exact_id)

        self.assertEquals(output, exact_result)

    def test_wait_response_timeout(self):
        transporter_args = {"class": transporter.Transporter}
        test_sender = haplib.Sender(transporter_args)
        test_processor = ProcessorForTest(test_sender, 0x01)
        test_id = 1
        try:
            test_processor.wait_response(test_id)
        except Exception as exception:
            self.assertEquals(str(exception), "Timeout")

# The above tests is HapiProcessor tests.
# The following tests is DispatchableReceiver tests.

    def test___dispatch_response(self):
        transporter_args = {"class": transporter.Transporter}
        test_receiver = haplib.DispatchableReceiver(transporter_args,
                                                    multiprocessing.JoinableQueue(),
                                                    None)
        test_receiver.attach_reply_queue(self.__test_queue)
        self.__test_queue.put(1)
        time.sleep(1)
        test_json_string = '{"id": 1, "result": "SUCCESS"}'
        exact_json_dict = json.loads(test_json_string)
        dispatch = self.__returnPrivObj(test_receiver,
                                         "__dispatch")
        self.__assertNotRaises(dispatch, None, test_json_string)
        result = self.__test_queue.get()
        self.__test_queue.task_done()

        self.assertEquals(exact_json_dict, result)

    def test___dispatch_exchange_profile(self):
        transporter_args = {"class": transporter.Transporter}
        test_receiver = haplib.DispatchableReceiver(transporter_args,
                                                    self.__test_queue,
                                                    ["exchangeProfile"])
        test_json_string = '{"method":"exchangeProfile", "id":1, "params":{"procedures": ["exchangeProfile"], "name":"test_name"}}'
        exact_json_dict = json.loads(test_json_string)
        dispatch = self.__returnPrivObj(test_receiver,
                                        "__dispatch")
        self.__assertNotRaises(dispatch, None, test_json_string)

        result = self.__test_queue.get()
        self.__test_queue.task_done()
        self.assertEquals(exact_json_dict, result)

    def test___dispatch_get_error(self):
        transporter_args = {"class": transporter.Transporter}
        test_receiver = haplib.DispatchableReceiver(transporter_args,
                                                    self.__test_queue,
                                                    ["exchangeProfile"])
        test_json_string = '{"valid_request"}'
        dispatch = self.__returnPrivObj(test_receiver,
                                        "__dispatch")
        self.__assertNotRaises(dispatch, None, test_json_string)

        result = self.__test_queue.get()
        self.__test_queue.task_done()
        self.assertEquals((-32700, None), result)

    def test_attach_reply_queue(self):
        transporter_args = {"class": transporter.Transporter}
        test_receiver = haplib.DispatchableReceiver(transporter_args,
                                                    self.__test_queue,
                                                    ["exchangeProfile"])
        test_receiver.attach_reply_queue(self.__test_queue)
        self.assertTrue(self.__test_queue in                                     \
                   test_receiver._DispatchableReceiver__reply_queues)

    def test_dispatch___call__(self):
        transporter_args = {"class": transporter.Transporter}
        test_receiver = haplib.DispatchableReceiver(transporter_args,
                                                    self.__test_queue,
                                                    ["exchangeProfile"])
        self.__assertNotRaises(test_receiver.__call__)

    def test_daemonize(self):
        transporter_args = {"class": transporter.Transporter}
        test_receiver = haplib.DispatchableReceiver(transporter_args,
                                                    self.__test_queue,
                                                    ["exchangeProfile"])
        self.__assertNotRaises(test_receiver.daemonize)

# The above tests is DispatchableReceiver tests.
# The following tests is BaseMainPlugin tests.

    def test_get_sender(self):
        transporter_args = {"class": transporter.Transporter}
        test_main_plugin = haplib.BaseMainPlugin(transporter_args)
        result = test_main_plugin.get_sender()
        exact = self.__returnPrivObj(test_main_plugin, "__sender")
        self.assertEquals(result, exact)

    def test_set_sender(self):
        transporter_args = {"class": transporter.Transporter}
        test_main_plugin = haplib.BaseMainPlugin(transporter_args)
        exact_sender = "test"
        test_main_plugin.set_sender(exact_sender)
        set_sender = self.__returnPrivObj(test_main_plugin, "__sender")
        self.assertEquals(set_sender, exact_sender)

    def test_get_receiver(self):
        transporter_args = {"class": transporter.Transporter}
        test_main_plugin = haplib.BaseMainPlugin(transporter_args)
        result = test_main_plugin.get_receiver()
        exact = self.__returnPrivObj(test_main_plugin, "__receiver")
        self.assertEquals(result, exact)

    def test_set_implemented_procedures(self):
        transporter_args = {"class": transporter.Transporter}
        test_main_plugin = haplib.BaseMainPlugin(transporter_args)
        exact_procedures = "test"
        test_main_plugin.set_implemented_procedures(exact_procedures)
        set_procedures = self.__returnPrivObj(test_main_plugin, "__implemented_procedures")
        self.assertEquals(set_procedures, exact_procedures)

    def test_hap_exchange_profile(self):
        transporter_args = {"class": transporter.Transporter}
        test_main_plugin = haplib.BaseMainPlugin(transporter_args)
        self.__assertNotRaises(test_main_plugin.hap_exchange_profile,
                              {"name":"test_name",
                               "procedures":["exchangeProfile"]}, 1)

    def test_hap_return_error(self):
        transporter_args = {"class": transporter.Transporter}
        test_main_plugin = haplib.BaseMainPlugin(transporter_args)

        self.__assertNotRaises(test_main_plugin.hap_return_error, -32700, None)

    def test_request_exit(self):
        transporter_args = {"class": transporter.Transporter}
        test_main_plugin = haplib.BaseMainPlugin(transporter_args)
        self.__assertNotRaises(test_main_plugin.request_exit)

        result_queue = self.__returnPrivObj(test_main_plugin, "__rpc_queue")
        self.assertEquals(result_queue.get(), None)
        result_queue.task_done()

    def test_is_exit_request(self):
        transporter_args = {"class": transporter.Transporter}
        test_main_plugin = haplib.BaseMainPlugin(transporter_args)
        result = test_main_plugin.is_exit_request(None)
        self.assertTrue(result)
        result = test_main_plugin.is_exit_request("test")
        self.assertFalse(result)

    def test_start_receiver(self):
        transporter_args = {"class": transporter.Transporter}
        test_main_plugin = haplib.BaseMainPlugin(transporter_args)
        self.__assertNotRaises(test_main_plugin.start_receiver)

    def test_main_plugin___call__(self):
        transporter_args = {"class": transporter.Transporter}
        test_main_plugin = haplib.BaseMainPlugin(transporter_args)
        rpc_queue = self.__returnPrivObj(test_main_plugin, "__rpc_queue")
        rpc_queue.put({"method":"exchangeProfile", "id":1, "params":{"procedures": ["exchangeProfile"], "name":"test_name"}})
        rpc_queue.put(None)
        self.__assertNotRaises(test_main_plugin.__call__)

# The above tests is HAPBaseMainPlugin tests.
# The following tests is Utils tests.

    def test_define_transporter_arguments(self):
        test_parser = argparse.ArgumentParser()
        self.__assertNotRaises(Utils.define_transporter_arguments, test_parser)

    def test_load_transporter(self):
        test_transport_arguments = namedtuple("transport_argument", "transporter_module transporter")
        test_transport_arguments.transporter_module = "haplib"
        test_transport_arguments.transporter = "RabbitMQHapiConnector"

        self.__assertNotRaises(Utils.load_transporter, test_transport_arguments)

    def test_check_message_invalid_json(self):
        test_message = "invalid_message"
        result = Utils.check_message(test_message, None)

        self.assertEquals((-32700, None), result)

    def test_check_message_not_implement(self):
        test_message = '{"method": "test_procedure", "params": "test_params", "id": 1, "jsonrpc": "2.0"}'
        result = Utils.check_message(test_message, ["exchangeProfile"])

        self.assertEquals((-32601, 1), result)

    def test_check_message_invalid_argument(self):
        test_message = '{"method": "exchangeProfile", "params": {"name":1, "procedures":"test"}, "id": 1, "jsonrpc": "2.0"}'
        result = Utils.check_message(test_message, ["exchangeProfile"])

        self.assertEquals((-32602, 1), result)

    def test_check_message_valid_json(self):
        test_message = '{"method": "exchangeProfile", "params": {"name":"test_name", "procedures":["exchangeProfile"]}, "id": 1, "jsonrpc": "2.0"}'
        result = Utils.check_message(test_message, ["exchangeProfile"])

        exact_dict = json.loads(test_message)
        self.assertEquals(exact_dict,result)

    def test_check_message_response(self):
        test_message = '{"result":"test_result","id":1,"jsonrpc": "2.0"}'
        result = Utils.check_message(test_message, ["exchangeProfile"])

        exact_dict = json.loads(test_message)
        self.assertEquals(exact_dict,result)

    def test_convert_string_to_dict_success(self):
        test_json_string = '{"test_key":"test_value"}'

        exact_result = json.loads(test_json_string)
        unnesessary_result, result = Utils.convert_string_to_dict(test_json_string)
        self.assertEquals(result, exact_result)

    def test_convert_string_to_dict_failure(self):
        test_json_string = '{"test_key": test_value}'

        exact_result = (-32700, None)
        result = Utils.convert_string_to_dict(test_json_string)
        self.assertEquals(result, exact_result)

    def test_check_procedures_is_implemented_success(self):
        result = Utils.check_procedure_is_implemented("exchangeProfile", ["exchangeProfile"])
        self.assertIsNone(result)

    def test_check_procedures_is_implemented_failure(self):
        result = Utils.check_procedure_is_implemented("test_procedure_name", ["exchangeProfile"])
        self.assertEquals(result, -32601)

    def test_validate_arguments_success(self):
        test_json_string = '{"method": "exchangeProfile", "params": {"name":"test_name", "procedures":["exchangeProfile"]}}'
        test_json_dict = json.loads(test_json_string)
        result = Utils.validate_arguments(test_json_dict)
        self.assertIsNone(result)

    def test_validate_arguments_fail(self):
        test_json_string = '{"method": "exchangeProfile", "params": {"name":"test_name", "procedures":"exchangeProfile"}}'
        test_json_dict = json.loads(test_json_string)
        result = Utils.validate_arguments(test_json_dict)
        self.assertEquals(result, -32602)

    def test_generate_request_id(self):
        result = Utils.generate_request_id(0x01)

        self.assertTrue(0 <= result <=  1111111111111)

    def test_translate_unit_time_to_hatohol_time(self):
        result = Utils.translate_unix_time_to_hatohol_time(0)
        self.assertEquals(result, "19700101090000.000000")

    def test_translate_hatohol_time_time_to_unix_time(self):
        result = Utils.translate_hatohol_time_to_unix_time("19700101090000.000000")
        self.assertEquals(result, 0)

    def test_optimize_server_procedures(self):
        test_procedures_dict = {"exchangeProfile": True, "updateTriggers": True}
        test_procedures = ["exchangeProfile"]

        Utils.optimize_server_procedures(test_procedures_dict,
                                            test_procedures)
        self.assertTrue(test_procedures_dict["exchangeProfile"])
        self.assertFalse(test_procedures_dict["updateTriggers"])

    def test_find_last_info_from_dict_array(self):
        test_target_array = [{"test_value": 3},
                             {"test_value": 7},
                             {"test_value": 9}]
        result = Utils.find_last_info_from_dict_array(test_target_array,
                                                         "test_value")
        self.assertEquals(result, 9)

    def test_get_current_hatohol_time(self):
        result = Utils.get_current_hatohol_time()

        self.assertEquals(len(result), 21)
        self.assertEquals(result[15: 21], "000000")

    def __assertNotRaises(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            raise

    def __returnPrivObj(self, instance, obj_name):
        class_name = instance.__class__.__name__
        return eval("instance._"+class_name+obj_name)


class ProcessorForTest(haplib.HapiProcessor):

    def __init__(self, sender, component_code):
        self.__sender = sender
        self.__reply_queue = multiprocessing.JoinableQueue()
        self.__component_code = component_code

    def get_reply_queue(self):
        return self.__reply_queue
    # The following method is same as the HapiProcessor one without timeout time.
    def wait_response(self, request_id):
        try:
            self.__reply_queue.join()
            response = self.__reply_queue.get(True, 1)
            self.__reply_queue.task_done()

            responsed_id = response["id"]
            if responsed_id != request_id:
                msg = "Got unexpected repsponse. req: " + str(request_id)
                logging.error(msg)
                raise Exception(msg)
            return response["result"]

        except ValueError as exception:
            if str(exception) == "task_done() called too many times" and \
                                              request_id == response["id"]:
                return response["result"]
            else:
                logging.error("Got invalid response.")
                raise Exception("InvalidResponse")
        except Queue.Empty:
            logging.error("Request failed.")
            raise Exception("Timeout")


class ConnectorForTest(transporter.Transporter):

    def __init__(self, test_queue):
        self.__test_queue = test_queue
        self.__ms_flag = False

    def enable_ms_flag(self):
        self.__ms_flag = True

    def call(self, msg):
        response_id = json.loads(msg)["id"]
        if self.__ms_flag:
            result = {"extendedInfo": "exampleExtraInfo",
                      "serverId": 0,
                      "url": "http://example.com:80",
                      "type": 0,
                      "nickName": "exampleName",
                      "userName": "Admin",
                      "password": "examplePass",
                      "pollingIntervalSec": 30,
                      "retryIntervalSec": 10}
            self.__test_queue.put({"result": result, "id": response_id})
        else:
            self.__test_queue.put({"result": "SUCCESS", "id": response_id})
        self.__test_queue.task_done()
