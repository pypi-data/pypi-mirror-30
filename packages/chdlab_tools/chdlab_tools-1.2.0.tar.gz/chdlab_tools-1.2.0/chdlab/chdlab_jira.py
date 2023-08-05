#!/usr/bin/env python

from chdlab_tftp import CHDLAB_tftp, tftp_server, VM_815_28_DUAL_BOOT_TFTP_Server
import sys
from restkit import Resource, BasicAuth, request
import paramiko
import json
import argparse
import re
import os
import logging

JIRA_URL="http://iapp180.iil.intel.com:8080/rest/api/latest/issue"

class CHDLAB_jira(object):
	"""Class for Jira handling"""

	class Error(Exception):
	    """Basic exception for errors raised by jira"""
	    def __init__(self, jira, msg=None):
		if msg is None:
		    msg = "ERROR: jira operation failed"
		super(CHDLAB_jira.Error, self).__init__("CHDLAB_jira operation failed (url={}, board={}, setup={}, issue={})\n{}".format(jira.url, jira.board, jira.setup, jira.issue, msg))
		self.jira = jira

	def __query(self):
		r = Resource("%s/%s" % (self.url, self.issue))
		try:
		    res = r.get(headers = {'Content-Type' : 'application/json'})
		except Exception,ex:
		    print("parse jira: %s " % ex.msg)
		    raise

		if res.status_int != 200:
			self.logger.error("parse jira: status %s" % res.status_int)
			raise

		# Convert the text in the reply into a Python dictionary
		return json.loads(res.body_string())['fields']

    
	def __get_board_id(self):
		return re.search(r'\d+', self.summary).group()

	def __get_board_mac(self):
		return self.__query()['customfield_11500']

	def __get_lan_vm(self):
		return self.__query()['customfield_11800']

	def __get_apc(self):
		try:
			apc = self.__query()['customfield_11101'].split(':')[1:]
			return [x.encode('UTF8').strip() for x in apc]
		except AttributeError:
			self.logger.warning("no apc! ({})".format(str(self)))
			pass
		return None

	def __get_telnet(self, arm=False):
		try:
			if not arm: 
				telnet = self.__query()['customfield_11103'].split(':')[1:]
			else: 
				telnet = self.__query()['customfield_11102'].split(':')[1:]
			return [x.encode('UTF8').strip() for x in telnet]
		except Exception as e:
			raise CHDLAB_jira.Error(self, "Failed to read telnet ip and port from JIRA")

	def __str__(self):
			return "board #{} setup #{} issue #{}".format(self.board, self.setup, self.issue)

	def __init__(self, board, conf=os.path.dirname(__file__)+"/setups.conf", url=JIRA_URL, verbose=False):
		self.logger = logging.getLogger('jira')
		self.url = url
		self.board = None
		self.setup = None
		self.issue = None

		with open(conf, 'r') as f:
			for line in f:
				line = line.strip()
				if line and not line.startswith("#"):
					_setup, _board, _issue =  tuple(line.split(":"))
					if _board == board:
						self.board = _board
						self.setup = _setup
						self.issue = _issue

		if not self.board:
			raise CHDLAB_jira.Error(self, "Invalid board id {}, does not exist in {}".format(board, os.path.abspath(conf)))

		self.summary = self.__query()['summary']
		self.assignee = self.__query()['assignee']['name']
		self.board_mac = self.__get_board_mac()
		self.apc = self.__get_apc()
		self.lan_vm = self.__get_lan_vm()
		if int(self.board) != int(self.__get_board_id()):
			raise CHDLAB_jira.Error(self, "board id {} does not match to JIRA board id {}".format(board, self.__get_board_id()))

		if "GRX350" in self.summary:
			self.type = "GRX350"
			self.telnet = self.__get_telnet(arm=False)
			self.tftp = CHDLAB_tftp(verbose=verbose)
			self.tftp_secondary = CHDLAB_tftp(server=VM_815_28_DUAL_BOOT_TFTP_Server)
		elif "GRX330" in self.summary:
			self.type = "GRX330"
			self.telnet = self.__get_telnet(arm=False)
			self.tftp = CHDLAB_tftp(verbose=verbose)
			self.tftp_secondary = CHDLAB_tftp(server=VM_815_28_DUAL_BOOT_TFTP_Server)
		elif "IRE220" in self.summary:
			self.type = "IRE220"
			self.telnet = self.__get_telnet(arm=False)
			self.tftp = CHDLAB_tftp(verbose=verbose, server=tftp_server(root="/tftpboot", path="localDisk/users", ip=self.lan_vm, local_ip="198.63.1.1", user="libit", password="libit", put_supported=True))
			self.tftp_secondary = self.tftp
		elif "CGP" in self.summary:
			self.type = "GRX750"
			self.telnet = self.__get_telnet(arm=False)
			self.telnet_arm = self.__get_telnet(arm=True)
			self.tftp = CHDLAB_tftp(verbose=verbose)
			self.tftp_secondary = CHDLAB_tftp(server=VM_815_28_DUAL_BOOT_TFTP_Server)
		else:
			raise CHDLAB_jira.Error(self, "Invalid board type (summary is {}, but it should include either GRX350 or GRX750)".format(self.summary))
  
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='chdlab')
	parser.add_argument("board", help="Board ID")
	args = parser.parse_args()

	logging.config.fileConfig(os.path.dirname(__file__)+'/logging.conf')

	jira = CHDLAB_jira(args.board)
	print "url: ", jira.url
	print "issue: ", jira.issue
	print "summary: ", jira.summary
	print "board id: ", jira.board
	print "board type: ", jira.type
	print "assignee: ", jira.assignee
	print "apc: ", jira.apc
	print "telnet: ", jira.telnet
