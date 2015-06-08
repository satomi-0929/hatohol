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
        transporter_args["amqp_queue"] += suffix
        RabbitMQConnector.setup(self, transporter_args)

class Sender:
    def __init__(self, transporter_args):
        transporter_args["direction"] = transporter.DIR_SEND
        self.__connector = transporter.Factory.create(transporter_args)

    def get__connector(self):
        return self.__connector

    def set__connector(self, connector):
        self.__connector = connector

    def request(self, procedure_name, params, request_id):
        request = json.dumps({"jsonrpc": "2.0", "method": procedure_name,
                              "params": params, "id": request_id})
        self.__connector.call(request)

    def response(self, result, response_id):
        response = json.dumps({"jsonrpc": "2.0", "result": result,
                               "id": response_id})
        self.__connector.reply(result)

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
        params = ""
        request_id = Utils.generate_request_id(self.__component_code)
        self.__reply_queue.put(request_id)
        self.__sender.request("getMonitoringServerInfo", params, request_id)
        return self.wait_response(request_id)

    def get_last_info(self, element):
        params = element
        request_id = Utils.get_and_save_request_id(self.requested_ids)
        self.request("getLastInfo", params, request_id)

        return self.wait_response(request_id)

    def exchange_profile(self, procedures, response_id=None):
        if response_id is None:
            request_id = Utils.get_and_save_request_id(self.requested_ids)
            self.request("exchangeProfile", procedures, request_id)
            self.wait_response(request_id)
        else:
            self.response(procedures, response_id)

    def update_arm_info(self, arm_info):
        params = {"lastStatus": arm_info.last_status,
                  "failureReason": arm_info.failure_reason,
                  "lastSuccessTime": arm_info.last_success_time,
                  "lastFailureTime": arm_info.last_failure_time,
                  "numSuccess": arm_info.num_success,
                  "numFailure": arm_info.num_failure}

        request_id = Utils.get_and_save_request_id(self.requested_ids)
        self.request("updateArmInfo", params, request_id)
        self.wait_response(request_id)

    def wait_response(self, request_id):
        try:
            self.__reply_queue.join()
            response = self.__reply_queue.get(True, 30)
            self.__reply_queue.task_done()

            responsed_id = response["id"]
            if responsed_id != request_id:
                msg = "Got unexpected repsponse. req: " + str(request_id)
                logging.error(msg)
                raise Exception(msg)
            return response["result"]

        except ValueError as exception:
            if str(exception) == "task_done() called too many times" and      \
                                            request_id == response_dict["id"]:
                self.requested_ids.remove(request_id)

                return response["result"]
            else:
                return
        except Queue.Empty:
            self.requested_ids.remove(request_id)
            logging.error("Request failed")
            return


class DispatchableReceiver:
    def __init__(self, transporter_args, rpc_queue):
        self.__reply_queues = []
        transporter_args["direction"] = transporter.DIR_RECV
        self.__connector = transporter.Factory.create(transporter_args)
        self.__rpc_queue = rpc_queue
        self.__connector.set_receiver(self.__dispatch)
        self.__id_res_q_map = {}

    def attach_reply_queue(self, queue):
        self.__reply_queues.append(queue)

    def __dispatch(self, ch, body):
        # TODO: Make it easier to see the result (OK or ERROR)
        msg = Utils.check_message(body, {})
        if isinstance(msg, tuple):
            self.__rpc_queue.put(msg)
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
        response_id = msg["id"]
        target_queue = self.__id_res_q_map.get(response_id, self.__rpc_queue)
        target_queue.put(msg)

    def __call__(self):
        # TODO: handle exceptions
        self.__connector.run_receive_loop()


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
        self.implement_procedures = ["exchangeProfile"]

        # launch receiver process
        receiver = DispatchableReceiver(transporter_args, self.__rpc_queue)
        receiver.attach_reply_queue(self.get_reply_queue())

        receiver_process = multiprocessing.Process(target=receiver)
        receiver_process.daemon = True
        receiver_process.start()

    def get_sender(self):
        return self.__sender

    def set_sender(self, sender):
        self.__sender = sender

    def hap_exchange_profile(self, params, request_id):
        Utils.optimize_server_procedures(SERVER_PROCEDURES, params["procedures"])
        #ToDo Output to log that is connect finish message with params["name"]
        self.__sender.exchange_profile(self.implement_procedures, request_id)

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

    def __call__(self):
        while True:
            request = self.__rpc_queue.get()
            if request is None:
                return
            try:
                self.procedures[request["method"]](request["params"],
                                                   request["id"])
            except KeyError:
                #The following sentense is used in case of receive notification
                # from Hatohol server. 
                self.procedures[request["method"]](request["params"])
            except ValueError as exception:
                if exception == "tuple indices must be integers, not str":
                    self.hap_return_error(request[0], request[1])


class Utils:

    PROCEDURES_ARGS = {"exchangeProfile": {"procedures":list(), "name": unicode()},
                       "fetchItems": {"hostIds":list(), "fetchId": unicode()},
                       "fetchHistory": {"hostId":unicode(),"itemId": unicode(),
                                        "beginTime": unicode(), "endTime": unicode(),
                                        "fetchId": unicode()},
                       "fetchTriggers": {"hostIds":list(), "fetchId": unicode()},
                       "fetchEvents": {"lastInfo":unicode(),"count":int(),
                                       "direction": unicode(),"fetchId": unicode()}}

    # ToDo Currently, this method does not have notification filter.
    # If we implement notification procedures, should insert notification filter.

    @staticmethod
    def define_transporter_arguments(parser):
        parser.add_argument("--transporter", type=str,
                            default="RabbitMQHapiConnector")
        parser.add_argument("--transporter-module", type=str, default="haplib")

    @staticmethod
    def load_transporter(args):
        (file, pathname, descr) = imp.find_module(args.transporter_module)
        mod = imp.load_module("", file, pathname, descr)
        transporter_class = eval("mod.%s" % args.transporter)
        return transporter_class

    @staticmethod
    def check_message(message, implement_procedures):
        error_code, message_dict = Utils.convert_string_to_dict(message)
        if isinstance(error_code, int):
            return (error_code, None)

        if message_dict.get("result") and message_dict.get("id"):
            return message_dict

        error_code = Utils.check_procedure_is_implemented(               \
                                  message_dict["method"], implement_procedures)
        if isinstance(error_code, int):
            try:
                return (error_code, message_dict["id"])
            except KeyError:
                return (error_code, None)

        error_code = Utils.check_argument_is_correct(message_dict)
        if isinstance(error_code, int):
            try:
                return (error_code, message_dict["id"])
            except KeyError:
                return (error_code, None)

        return message_dict

    @staticmethod
    def convert_string_to_dict(json_string):
        try:
            json_dict = json.loads(json_string)
        except ValueError:
            return (-32700, None)
        else:
            return (None, json_dict)

    @staticmethod
    def check_procedure_is_implemented(procedure_name, implement_procedures):
        if procedure_name in implement_procedures:
            return
        else:
            return -32601

    @staticmethod
    def check_argument_is_correct(json_dict):
        args_dict = Utils.PROCEDURES_ARGS[json_dict["method"]]
        for arg_name, arg_value in json_dict["params"].iteritems():
            try:
                if type(args_dict[arg_name]) != type(arg_value):
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
