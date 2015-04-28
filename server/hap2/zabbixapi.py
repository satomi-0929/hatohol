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


	self.hosts = []
	self.host_group_membeship = []
	# The following method gets not only hosts info but also host group membership.
	def get_hosts(self, prev):
		prev.hosts = self.hosts
		prev.host_group_membership = self.host_group_membership
		self.hosts = []
		self.host_group_membership = []

		post = json.dumps({"jsonrpc":"2.0", "method":"host.get", "params":{"output":"extend", "selectGroups":"refer", "monitored_hosts":True}, "auth":self.auth_token, "id":1})
		request = urllib2.Request(self.url, post, self.HEADER)
		response = urllib2.urlopen(request)
		res_str = response.read()
		res_dict = json.loads(res_str)

		self.result = check_response(res_dict)
		if not self.result:
			return

		for host in res_dict["result"]:
			self.hosts.append({host["hostid"]:host["name"]})

			group_ids = []
			for groups in host["groups"]:
				group_ids.append(groups["groupid"])

			self.host_group_membership.append({host["id"]:group_ids})


	def get_host_groups(self):
		post = json.dumps({"jsonrpc":"2.0", "method":"hostgroup.get", "params":{"output":"extend", "selectHosts":"refer", "real_hosts":True, "monitored_hosts":True}, "auth":self.auth_token, "id":1})
		request = urllib2.Request(zabbix, post, self.HEADER)
		response = urllib2.urlopen(request)
		res_str = response.read()
		res_dict = json.loads(res_str)

		self.result = check_response(res_dict)
		if not self.result:
			return

		for host in res_dict["result"]:
			self.hosts.append({host["hostid"]:host["name"]})

			group_ids = []
			for groups in host["groups"]:
				group_ids.append(groups["groupid"])

			self.host_group_membership.append({host["id"]:group_ids})


	def get_triggers(self, requestSince = None):
		request_dict = {"jsonrpc":"2.0", "method":"trigger.get", "params":{"output":"extend", "monitored_hosts":True}, "auth":self.auth_token, "id":1}
		if requestSince is not None:
				request_dict["params"]["lastChangeSince"] = int(requestSince)
		post = json.dumps(request_dict)
		request = urllib2.Request(self.url, post, self.HEADER)
		response = urllib2.urlopen(request)
		res_str = response.read()
		res_dict = json.loads(res_str)

		self.result = check_response(res_dict)
		if not self.result:
			return

		triggers = []
		for trigger in res_dict["result"]:



def check_response(response_dict):
	if "error" in response_dict:
		return False

	return True
