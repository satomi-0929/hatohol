#! /usr/lib/env python

import os
import sys
import json

class base_procedures:
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


def get_error_dict():
	error = {"-32700":"Parse error" , "-32600":"invalid Request", "-32601":"Method not found", "-32602":"invalid params", "-32603":"Internal error"}
	for num in range(-32000,-32100):
		error[str(num)] = "Server error"

	return error


def send_json_to_que(string):
	print string


def receive_json_from_que():
	print "Not implement"


def convert_string_to_dict(json_string):
	try:
		json_dict = json.loads(json_string)
	except Exception:
		return "-32700"
	else:
		return json_dict


def check_method_is_implemented(method_name):
	for method in get_implement_methods():
		if method_name == method:
				return "IMPLEMENT"
		else:
				return "-32601"


def check_argument_is_correct(json_dict):
	args = inspect.getargspec(json_dict["method"])
	for argument in json_dict["params"]:
		if argument in args:
			result = "OK"
	return "-32602"
# ToDo ちゃんとアルゴリズム考える。params内がオブジェクトだったらどうするのか，とか。


def get_implement_purocedures(class_name):
	procedures = ()
	modules = dir(eval(class_name))
	for module in modules:
		if inspect.ismethod(eval(class_name + "." + module)) and eval("base_procedures." + module).im_func != eval(class_name + "." +module).im_func:
			procedures = procedures + (module,)
	
	return procedures


error_dict = get_error_dict()
def create_error_json(error_code, req_id = "null"):
	return '{"jsonrpc": "2.0", "error": {"code":' + error_code + ', "message":' + error_dict[error_code]+ '}, "id":' + req_id + '"}}'


def get_request_id():
	return random.int()

def create_request_string(procedure_name, key, id, *params):
	zabbix = "http://10.0.3.11/zabbix/api_jsonrpc.php"
	header = {"Content-Type":"application/json-rpc"}
	user = "Admin"
	passwd = "zabbix"
	request_dict = {"jsonrpc":"2.0", "method":procedure_name, "params": {}, "auth": key, "id":get_request_id()}
	for param_key, param_value in params.items():
		request_dict["params"][param_key] = param_value

    return json.dumps(request_dict)

