#! /usr/bin/env python

import os
import daemon.runner
import json
import urllib2
import time
import hap_lib

valid_procedures_of_server = {"exchangeProfile":True, "gertMonitoringServer":True, "getLastInfo":True, "putItems":True, "putHistory":True, "updateHosts":True, "updateHostGroups":True, "updateHostGroupMembership":True, "updateTriggers":True, "updateEvents":True, "updateHostParent":True, "updateArmInfo":True}

class zabbix_procedures(hap_lib.base_procedures):
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


def check_request(json_string):
    json_dict = hap_lib.convert_string_to_dict(json_string)
    if isinstance(json_dict, str):
        hap_lib.send_json_to_que(hap_lib.create_error_json(json_dict))

    result = hap_lib.check_implement_method(json_dict["method"])
    if result in not None:
        hap_lib.send_json_to_que(hap_lib.create_error_json(result, json_dict["id"]))

    result = hap_lib.check_argument_is_correct(json_dict["method"])
    if result in not None:
        hap_lib.send_json_to_que(hap_lib.create_error_json(result, json_dict["id"]))

    return json_dict


def turn_on_procedure(json_string):
    valid_json_dict = check_request(json_string)
	if isinstance(valid_json_dict, dict):
   		locals().[valid_json_dict["method"]](valid_json_dict)
    	引数どうやって入れるか考える
	else:
		return


def get_auth_key():
	zabbix = "http://10.0.3.11/zabbix/api_jsonrpc.php"
	header = {"Content-Type":"application/json-rpc"}
	user = "Admin"
	passwd = "zabbix"
	temlate_dict = {"jsonrpc":"2.0", "method":None, "params": {}, "auth": None, "id":None}

    post = json.dumps({'jsonrpc':'2.0', 'method':'user.authenticate', 'params':{'user':user, 'password':passwd}, 'auth':None, 'id': 1})
    request = urllib2.Request(zabbix, post, header)
    response = urllib2.urlopen(request)
    res_str = response.read()
    res_dic = json.loads(res_str)

    return res_dic["result"]


def get_hosts_info(key):
	post = json.dumps({'jsonrpc':'2.0', 'method':'host.get', 'params':{"output":"extend"}, 'auth':key, 'id':1})
	request = urllib2.Request(zabbix, post, header)
	response = urllib2.urlopen(request)
	res_str = response.read()
	res_dic = json.loads(res_str)

	return res_dict


def send_hosts_info(option):
	hosts_info_dict = get_hosts_info()

	res_dict = res_dict[params]
	for host in range(len(res_dic["result"])):
		res_array = ["{hostId":{res_dic["result"][host]["name"]

	hap_lib.send_json_to_que(json_string)


def routine_update():				
	send_hosts_info("UPDATE")


def main():
    daemon_runner = daemon.runner.DaemonRunner()


if __name__ == '__main__':
    key = get_auth_key()
    with daemon.DaemonContext(pidfile=PIDLockFile('/var/run/hap-zabbixd.pid')):
