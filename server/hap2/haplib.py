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

import json
from datetime import datetime
import time
import pika
import random
import Queue
import logging
import multiprocessing
import imp
import transporter
from rabbitmqconnector import RabbitMQConnector
import pickle

SERVER_PROCEDURES = {"exchangeProfile": True,
                     "getMonitoringServerInfo": True,
                     "getLastInfo": True,
                     "putItems": True,
                     "putHistory": True,
                     "updateHosts": True,
                     "updateHostGroups": True,
                     "updateHostGroupMembership": True,
                     "updateTriggers": True,
                     "updateEvents": True,
                     "updateHostParent": True,
                     "updateArmInfo": True}
ERROR_DICT = {-32700: "Parse error", -32600: "invalid Request",
              -32601: "Method not found", -32602: "invalid params"}

class MonitoringServerInfo:
    def __init__(self, ms_info_dict):
        self.server_id = ms_info_dict["serverId"]
        self.url = ms_info_dict["url"]
        self.server_type = ms_info_dict["type"]
        self.nick_name = ms_info_dict["nickName"]
        self.user_name = ms_info_dict["userName"]
        self.password = ms_info_dict["password"]
        self.polling_interval_sec = ms_info_dict["pollingIntervalSec"]
        self.retry_interval_sec = ms_info_dict["retryIntervalSec"]
        self.extended_info = ms_info_dict["extendedInfo"]

class ParsedMessage:
    def __init__(self):
        self.error_code = None
        self.message_id = None
        self.message_dict = None

    def get_error_message(self):
        return "error code: %s, message ID: %s" % \
               (self.error_code, self.message_id)


class ArmInfo:
    def __init__(self):
        self.last_status = str()
        self.failure_reason = str()
        self.last_success_time = str()
        self.last_failure_time = str()
        self.num_success = int()
        self.num_failure = int()

class RabbitMQHapiConnector(RabbitMQConnector):
    def setup(self, transporter_args):
        send_queue_suffix = transporter_args.get("amqp_send_queue_suffix", "-S")
        recv_queue_suffix = transporter_args.get("amqp_recv_queue_suffix", "-T")
        suffix_map = {transporter.DIR_SEND: send_queue_suffix,
                      transporter.DIR_RECV: recv_queue_suffix}
        suffix = suffix_map.get(transporter_args["direction"], "")

        if "amqp_hapi_queue" not in transporter_args:
            transporter_args["amqp_hapi_queue"] = transporter_args["amqp_queue"]
        transporter_args["amqp_queue"] = \
          transporter_args["amqp_hapi_queue"] + suffix
        RabbitMQConnector.setup(self, transporter_args)

class Sender:
    def __init__(self, transporter_args):
        transporter_args["direction"] = transporter.DIR_SEND
        self.__connector = transporter.Factory.create(transporter_args)

    def get_connector(self):
        return self.__connector

    def set_connector(self, connector):
        self.__connector = connector

    def request(self, procedure_name, params, request_id):
        request = json.dumps({"jsonrpc": "2.0", "method": procedure_name,
                              "params": params, "id": request_id})
        self.__connector.call(request)

    def response(self, result, response_id):
        response = json.dumps({"jsonrpc": "2.0", "result": result,
                               "id": response_id})
        self.__connector.reply(response)

    def send_error_to_queue(self, error_code, response_id):
        response = json.dumps({"jsonrpc": "2.0",
                               "error": {"code": error_code,
                                         "message": ERROR_DICT[error_code]},
                               "id": response_id})
        self.__connector.reply(response)

"""
Issue HAPI requests and responses.
Some APIs blocks until the response is arrived.
"""
class HapiProcessor:
    def __init__(self, sender, component_code):
        self.__sender = sender
        self.__reply_queue = multiprocessing.JoinableQueue()
        self.__component_code = component_code

    def get_reply_queue(self):
        return self.__reply_queue

    def get_monitoring_server_info(self):
        """
        Get a MonitoringServerInfo from Hatohol server.
        This method blocks until the response is obtained.
        @return A MonitoringServerInfo object.
        """
        params = ""
        request_id = Utils.generate_request_id(self.__component_code)
        self.__sender.request("getMonitoringServerInfo", params, request_id)
        return MonitoringServerInfo(self.wait_response(request_id))

    def get_last_info(self, element):
        params = element
        request_id = Utils.generate_request_id(self.__component_code)
        self.__sender.request("getLastInfo", params, request_id)

        return self.wait_response(request_id)

    def exchange_profile(self, procedures, response_id=None):
        if response_id is None:
            request_id = Utils.generate_request_id(self.__component_code)
            self.__sender.request("exchangeProfile", procedures, request_id)
            self.wait_response(request_id)
        else:
            self.__sender.response(procedures, response_id)

    def update_arm_info(self, arm_info):
        params = {"lastStatus": arm_info.last_status,
                  "failureReason": arm_info.failure_reason,
                  "lastSuccessTime": arm_info.last_success_time,
                  "lastFailureTime": arm_info.last_failure_time,
                  "numSuccess": arm_info.num_success,
                  "numFailure": arm_info.num_failure}

        request_id = Utils.generate_request_id(self.__component_code)
        self.__sender.request("updateArmInfo", params, request_id)
        self.wait_response(request_id)

    def wait_response(self, request_id):
        TIMEOUT_SEC = 30
        try:
            self.__reply_queue.put(request_id)
            self.__reply_queue.join()
            pm = self.__reply_queue.get(True, TIMEOUT_SEC)
            self.__reply_queue.task_done()

            if pm.error_code is not None:
                raise Exception(pm.get_error_message())

            if pm.message_id != request_id:
                msg = "Got unexpected repsponse. req: " + str(request_id)
                logging.error(msg)
                raise Exception(msg)
            return pm.message_dict["result"]

        except ValueError as exception:
            if str(exception) == "task_done() called too many times" and \
                                              request_id == response["id"]:
                return response["result"]
            else:
                logging.error("Got invalid response.")
                raise
        except Queue.Empty:
            logging.error("Request failed.")
            raise

class DispatchableReceiver:
    def __init__(self, transporter_args, rpc_queue, procedures):
        self.__reply_queues = []
        transporter_args["direction"] = transporter.DIR_RECV
        self.__connector = transporter.Factory.create(transporter_args)
        self.__rpc_queue = rpc_queue
        self.__connector.set_receiver(self.__dispatch)
        self.__id_res_q_map = {}
        self.__implemented_procedures = procedures

    def attach_reply_queue(self, queue):
        self.__reply_queues.append(queue)

    def __dispatch(self, ch, message):
        parsed = Utils.parse_received_message(message,
                                              self.__implemented_procedures)
        if parsed.error_code is not None:
            self.__rpc_queue.put(parsed)
            return

        # collect newly arrived wait IDs
        for queue in self.__reply_queues:
            if queue.empty():
                continue
            wait_id = queue.get(False)
            queue.task_done()

            if wait_id in self.__id_res_q_map:
                logging.error("Ignored duplicated ID: " + str(wait_id))
                continue
            self.__id_res_q_map[wait_id] = queue

        # dispatch the received message from the transport layer
        response_id = parsed.message_id
        target_queue = self.__id_res_q_map.get(response_id, self.__rpc_queue)
        target_queue.put(parsed)
        self.__id_res_q_map.pop(response_id, None)

    def __call__(self):
        # TODO: handle exceptions
        self.__connector.run_receive_loop()

    def daemonize(self):
        receiver_process = multiprocessing.Process(target=self)
        receiver_process.daemon = True
        receiver_process.start()


class BaseMainPlugin(HapiProcessor):

    __COMPONENT_CODE = 0x10

    def __init__(self, transporter_args):
        self.__sender = Sender(transporter_args)
        HapiProcessor.__init__(self, self.__sender, self.__COMPONENT_CODE)

        self.__rpc_queue = multiprocessing.JoinableQueue()
        self.procedures = {"exchangeProfile": self.hap_exchange_profile,
                           "fetchItems": self.hap_fetch_items,
                           "fetchHistory": self.hap_fetch_history,
                           "fetchTriggers": self.hap_fetch_triggers,
                           "fetchEvents": self.hap_fetch_events}
        #ToDo Currently, implement_method is fixed.
        # I want to get its dynamically to to use function.
        self.set_implemented_procedures(["exchangeProfile"])

        # launch receiver process
        self.__receiver = DispatchableReceiver(transporter_args,
                                               self.__rpc_queue,
                                               self.__implemented_procedures)
        self.__receiver.attach_reply_queue(self.get_reply_queue())

    def get_sender(self):
        return self.__sender

    def set_sender(self, sender):
        self.__sender = sender

    def get_receiver(self):
        return self.__receiver

    def set_implemented_procedures(self, procedures):
        self.__implemented_procedures = procedures

    def hap_exchange_profile(self, params, request_id):
        Utils.optimize_server_procedures(SERVER_PROCEDURES, params["procedures"])
        #ToDo Output to log that is connect finish message with params["name"]
        self.exchange_profile(self.__implemented_procedures, request_id)

    def hap_fetch_items(self, params, request_id):
        pass

    def hap_fetch_history(self, params, request_id):
        pass

    def hap_fetch_triggers(self, params, request_id):
        pass

    def hap_fetch_events(self, params, request_id):
        pass

    def hap_return_error(self, error_code, response_id):
        self.__sender.send_error_to_queue(error_code, response_id)

    def request_exit(self):
        """
        Request to exit main loop that is started by __call__().
        """
        self.__rpc_queue.put(None)

    def is_exit_request(self, request):
        return request is None

    def start_receiver(self):
        """
        Launch the process for receiving data from the transporter.
        This method shall be called once before calling __call__().
        """
        self.__receiver.daemonize()

    def __call__(self):
        while True:
            request = self.__rpc_queue.get()
            self.__rpc_queue.task_done()
            if self.is_exit_request(request):
                return
            try:
                self.procedures[request["method"]](request["params"],
                                                   request["id"])
            except KeyError:
                #The following sentense is used in case of receive notification
                # from Hatohol server. 
                self.procedures[request["method"]](request["params"])
            except ValueError as exception:
                if str(exception) == "tuple indices must be integers, not str":
                    self.hap_return_error(request[0], request[1])


class Utils:

    PROCEDURES_ARGS = {
      "exchangeProfile": {"procedures":list(), "name": unicode()},
      "fetchItems": {"hostIds":list(), "fetchId": unicode()},
      "fetchHistory": {"hostId":unicode(),"itemId": unicode(),
                       "beginTime": unicode(), "endTime": unicode(),
                       "fetchId": unicode()},
      "fetchTriggers": {"hostIds":list(), "fetchId": unicode()},
      "fetchEvents": {"lastInfo":unicode(),"count":int(),
                      "direction": unicode(),"fetchId": unicode()},
      "getMonitoringServerInfo": {},
    }

    # ToDo Currently, this method does not have notification filter.
    # If we implement notification procedures, should insert notification filter.

    @staticmethod
    def define_transporter_arguments(parser):
        parser.add_argument("--transporter", type=str,
                            default="RabbitMQHapiConnector")
        parser.add_argument("--transporter-module", type=str, default="haplib")

        # TODO: Don't specifiy a sub class of transporter directly.
        #       We'd like to implement the mechanism that automatically
        #       collects transporter's sub classes, loads them,
        #       and calls their define_arguments().
        RabbitMQHapiConnector.define_arguments(parser)

    @staticmethod
    def load_transporter(args):
        (file, pathname, descr) = imp.find_module(args.transporter_module)
        mod = imp.load_module("", file, pathname, descr)
        transporter_class = eval("mod.%s" % args.transporter)
        return transporter_class

    @staticmethod
    def parse_received_message(message, implemented_procedures):
        """
        Parse a received message.
        @return A ParsedMessage object. Each attribute will be set as below.
        - error_code If the parse is succeeded, this attribute is set to None.
                     Othwerwise the error code is set.
        - message_dict A dictionary that corresponds to the received message.
                       If the parse fails, this attribute may be None.
        - message_id A message ID if available. Or None.
        """

        pm = ParsedMessage()
        pm.error_code, pm.message_dict = \
          Utils.__convert_string_to_dict(message)
        try:
            pm.message_id = pm.message_dict["id"]
        except KeyError:
            pm.message_id = None

        # Failed to convert the message to a dictionary
        if pm.error_code is not None:
            return pm

        # 'id' is not included in the message.
        if pm.message_id is None:
            pm.error_code = -32602
            return pm

        # If the message is a reply, sage to a dictionary
        if pm.message_dict.get("result") and pm.message_id is not None:
            return pm

        pm.error_code = Utils.check_procedure_is_implemented( \
                           pm.message_dict["method"], implemented_procedures)
        if pm.error_code is not None:
            return pm

        pm.error_code = Utils.validate_arguments(pm.message_dict)
        if pm.error_code is not None:
            return pm

        return pm

    @staticmethod
    def __convert_string_to_dict(json_string):
        try:
            json_dict = json.loads(json_string)
        except ValueError:
            return (-32700, None)
        else:
            return (None, json_dict)

    @staticmethod
    def check_procedure_is_implemented(procedure_name, implemented_procedures):
        if procedure_name in implemented_procedures:
            return
        else:
            return -32601

    @staticmethod
    def validate_arguments(json_dict):
        args_dict = Utils.PROCEDURES_ARGS[json_dict["method"]]
        for arg_name, arg_value in args_dict.iteritems():
            try:
                if type(json_dict["params"][arg_name]) != type(arg_value):
                    return -32602
            except KeyError:
                return -32602

        return

    @staticmethod
    def generate_request_id(component_code):
        assert component_code <= 0x7f, \
               "Invalid component code: " + str(component_code)
        req_id = random.randint(1, 0xffffff)
        req_id |= component_code << 24
        return req_id

    @staticmethod
    def translate_unix_time_to_hatohol_time(float_unix_time):
        return datetime.strftime(datetime.fromtimestamp(float_unix_time), "%Y%m%d%H%M%S.%f")

    @staticmethod
    def translate_hatohol_time_to_unix_time(hatohol_time):
        date_time = time.strptime(hatohol_time, "%Y%m%d%H%M%S.%f")
        return int(time.mktime(date_time))

    @staticmethod
    def optimize_server_procedures(valid_procedures_dict, procedures):
        for name in valid_procedures_dict:
            valid_procedures_dict[name] = False

        for procedure in procedures:
            valid_procedures_dict[procedure] = True

    @staticmethod
    def find_last_info_from_dict_array(target_array, last_info_name):
        last_info = None
        for target_dict in target_array:
            if last_info < target_dict[last_info_name]:
                last_info = target_dict[last_info_name]

        return last_info

    @staticmethod
    def get_current_hatohol_time():
        unix_time = float(time.mktime(datetime.now().utctimetuple()))
        return Utils.translate_unix_time_to_hatohol_time(unix_time)
