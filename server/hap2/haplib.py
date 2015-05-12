#! /usr/lib/env python
# coding: UTF-8

import json
from datetime import datetime
import pika

class PluginProcedures:
    def __init__():
        self.valid_procedures_of_server = {"exchangeProfile":False,
                                           "getMonitoringServerInfo":False,
                                           "getLastInfo":False,
                                           "putItems":False,
                                           "putHistory":False,
                                           "updateHosts":False,
                                           "updateHostGroups":False,
                                           "updateHostGroupMembership":False,
                                           "updateTriggers":False,
                                           "updateEvents":False,
                                           "updateHostParent":False,
                                           "updateArmInfo":False}


    def exchangeProfile(self):
        print "Not implement"


    def fetchItems(self):
        print "Not implement"


    def fetchHistory(self):
        print "Not implement"


    def fetchTriggers(self):
        print "Not implement"


    def fetchEvents(self):
        print "Not implement"


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


class RabbitMQConnector:
    def __init__(self, host, queue_name, user_name, user_password):
        self.queue_name = queue_name
        credentials = pika.PlaneCredentials(user_name, user_password)
        param = pika.ConnectionParameter(host = host, credentials = credentials)
        connection = pika.BlockingConnenction(param)
        self.channel = connection.channel()
        self.channel.queue_declare(queue = queue_name)


class RabbitMQPublisher(RabbitMQConnector):
    def send_message_to_que(json_string):
        self.channel.basic_publish(exchange = '',
                                   routing_key = self.queue_name,
                                   body = json_string)


class RabbitMQConsumer(RabbitMQConnector):
    def Not_implement():
        print "Not implement"


def get_error_dict():
    error_dict = {-32700: "Parse error" , -32600: "invalid Request",
                  -32601: "Method not found", -32602: "invalid params",
                  -32603: "Internal error"}
    for num in range(-32000,-32100):
        error_dict[str(num)] = "Server error"

    return error_dict


def convert_string_to_dict(json_string):
    try:
        json_dict = json.loads(json_string)
    except Exception:
        return -32700
    else:
        return json_dict


def check_method_is_implemented(method_name):
    for method in get_implement_methods():
        if method_name == method:
            return "IMPLEMENT"
        else:
            return -32601


def check_argument_is_correct(json_dict):
    args = inspect.getargspec(json_dict["method"])
    for argument in json_dict["params"]:
        if argument in args:
            result = "OK"

    return -32602
# ToDo Think about algorithm. In case of param is object.


def get_implement_procedures(class_name):
    procedures = ()
    modules = dir(eval(class_name))
    for module in modules:
        if inspect.ismethod(eval(class_name + "." + module)) and eval("BaseProcedures." + module).im_func != eval(class_name + "." +module).im_func:
            procedures = procedures + (module,)

    return procedures


def create_request_json(procedure_name, params):
    request_dict = {"jsonrpc": "2.0", "method": procedure_name, "params": params, "id": get_request_id()}
    for param_key, param_value in params.items():
        request_dict["params"][param_key] = param_value

    return json.dumps(request_dict)


#def create_response_json(req_id):


def create_error_json(error_code, req_id = "null"):
    error_dict = get_error_dictdd()
    #ToDo Create place
    return '{"jsonrpc": "2.0", "error": {"code":' + error_code + ', "message":' + error_dict[error_code]+ '}, "id":' + req_id + '"}}'


def get_request_id():
    return random.int()
    #ToDo How management ID


def check_request(json_string):
    json_dict = convert_string_to_dict(json_string)
    if not isinstance(json_dict, dict):
        send_json_to_que(create_error_json(json_dict))
        return

    result = check_implement_method(json_dict["method"])
    if result is not None:
        send_json_to_que(create_error_json(result, json_dict["id"]))
        return

    result = check_argument_is_correct(json_dict["method"])
    if result is not None:
        send_json_to_que(create_error_json(result, json_dict["id"]))
        return

    return json_dict


def call_procedure(json_string):
    valid_json_dict = check_request(json_string)
    if valid_json_dict is None:
        return

    locals()[valid_json_dict["method"]](valid_json_dict("params"))
    #ToDo How do pass arguments to the params


def translate_unix_time_to_hatohol_time(float_unix_time):
    return datetime.strftime(datetime.fromtimestamp(float_unix_time), "%Y%m%d%H%M%S.%f")


def translate_hatohol_time_to_unix_time(hatohol_time):
    return datetime.strptime(hatohol_unix_time, "%Y%m%d%H%M%S.%f")


def optimize_server_procedures(valid_procedures_dict, procedures):
    for procedure in procedures:
        valid_procedures_dict[procedure] = True
