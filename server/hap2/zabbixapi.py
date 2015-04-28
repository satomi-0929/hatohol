#! /usr/bin/env python
# coding: UTF-8

import urllib2
import json

class ZabbixAPI:
	HEADER = {"Content-Type":"application/json-rpc"}
	def __init__(self, monitoring_server_info):
		self.url = "http://" + monitoring_server_info.ip_address + "/zabbix/api_jsonrpc.php"
		self.auth_token =
			self.get_auth_token(monitoring_server_info.user_name,
								monitoring_server_info.user_passwd)


	def get_auth_token(self, ip_adderss, user_name, user_passwd):
		post = json.dumps({'jsonrpc':'2.0', 'method':'user.authenticate', 'params':{'user':user_name, 'password':user_passwd}, 'auth':None, 'id':1})
		request = urllib2.Request(url, post, HEADER)
		response = urllib2.urlopen(request)
		res_str = response.read()
		res_dict = json.loads(res_str)

		self.result = check_response(res_dict)
		if not self.result:
			return

		return res_dict["result"]


	# The following method gets not only hosts info but also host group membership.
	def get_hosts(self):
		post = json.dumps({"jsonrpc":"2.0", "method":"host.get", "params":{"output":"extend", "selectGroups":"refer", "monitored_hosts":True}, "auth":self.auth_token, "id":1})
		request = urllib2.Request(self.url, post, self.HEADER)
		response = urllib2.urlopen(request)
		res_str = response.read()
		res_dict = json.loads(res_str)

		self.result = check_response(res_dict)
		if not self.result:
			return

		hosts = []
		host_group_membership = []
		for host in res_dict["result"]:
			hosts.append({"hostId":host["hostid"], "hostName":host["name"]})

			group_ids = []
			for groups in host["groups"]:
				group_ids.append(groups["groupid"])

			host_group_membership.append({"hostId":host["id"], "groupIds":group_ids})

		return (hosts, host_group_membership)


	def get_host_groups(self):
		post = json.dumps({"jsonrpc":"2.0", "method":"hostgroup.get", "params":{"output":"extend", "selectHosts":"refer", "real_hosts":True, "monitored_hosts":True}, "auth":self.auth_token, "id":1})
		request = urllib2.Request(zabbix, post, self.HEADER)
		response = urllib2.urlopen(request)
		res_str = response.read()
		res_dict = json.loads(res_str)

		self.result = check_response(res_dict)
		if not self.result:
			return

		host_groups = []
		for host_group in res_dict["result"]:
			host_groups.append({"hostId":host_group["hostid"], "groupName":host_group["name"]})

		return host_groups


	def get_triggers(self, requestSince = None):
		request_dict = {"jsonrpc":"2.0", "method":"trigger.get", "params":{"output":"extend", "monitored_hosts":True}, "auth":self.auth_token, "id":1}
		if requestSince is not None:
				request_dict["params"]["lastChangeSince"] = int(requestSince)

		self.result = check_response(res_dict)
		if not self.result:
			return

		triggers = []
		for trigger in res_dict["result"]:


def get_response_dict(request_dict, auth_key, params):
	post = json.dumps(request_dict)
	request = urllib2.Request(self.url, post, self.HEADER)
	response = urllib2.urlopen(request)
	res_str = response.read()
	res_dict = json.loads(res_str)



def check_response(response_dict):
	if "error" in response_dict:
		return False

	return True
