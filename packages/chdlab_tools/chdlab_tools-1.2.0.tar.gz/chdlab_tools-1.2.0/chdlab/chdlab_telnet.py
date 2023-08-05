#!/usr/bin/env python

from chdlab_jira import CHDLAB_jira
import telnetlib
import argparse
import os
import sys
import time
import logging
import logging.config

TIMEOUT_LINUX_TO_UBOOT = 3
TIMEOUT_UBOOT_TO_LINUX = 15

class CHDLAB_telnet(object):
	def __init__(self, board, user='admin', password='admin', verbose=False, jira=None):
		self.logger = logging.getLogger('telnet')
		if verbose:
			self.logger.setLevel(logging.DEBUG)
		if jira:
			self.jira = jira
		else:
			self.jira = CHDLAB_jira(board)
		self.user = user
		self.password = password
		ip, port = self.jira.telnet
		self.tn = telnetlib.Telnet(ip, port)

	def __str__(self):
		return "telnet {}:{}".format(self.ip, self.port)

	def __prepare__(self):
		self.tn.read_very_eager()
		self.tn.write("\n")
		while (1):
			index, match, data = self.tn.expect(['GRX(500|330) #', '(.*?)@.*?:.*?[\$,\#]', 'Hit any key to stop autoboot:', 'ugwcpe.intel.com login:', 'Password:'])
			if index == 0:
				self.logger.debug('>> UBOOT shell')
				return 'uboot'
			elif index == 1:
				self.logger.debug('>> Linux UGW prompt')
				return 'linux'
			elif index == 2:
				self.logger.debug('UBOOT Interactive countdown...')
				self.tn.write("\n")
			elif index == 3:
				self.logger.debug('>> Linux UGW login (user) --> enter username')
				self.tn.write("{}\n".format(self.user))
			elif index == 4:
				self.logger.debug('>> Linux UGW login (password)--> enter password')
				self.tn.write("{}\n".format(self.password))
			else:
				self.logger.error('unexpected index='+str(index))

	def write_raw(self, cmd):
		if self.jira.type == "IRE220":
			for c in cmd:
				time.sleep(0.01)
				self.tn.write(c)
				time.sleep(0.01)
		else:
			self.tn.write("%s" %cmd)

	def write(self, cmd):
		self.logger.info("command: %s" %cmd)
		self.__prepare__()
		self.write_raw("%s\n" %cmd)
		self.__prepare__()

	def state_change(self, new_state):
		state = self.__prepare__()
		if state == new_state:
			self.logger.debug("state {} --> state {}, skipped".format(state, new_state))
			return

		self.logger.info("state {} --> state {}".format(state, new_state))
		if state == 'linux' and new_state == 'uboot':
			while state != new_state:
				self.write_raw("reboot\n")
				time.sleep(TIMEOUT_LINUX_TO_UBOOT)
				state = self.__prepare__()
			return state
		elif state == 'uboot' and new_state == 'linux':
			self.write_raw("reset\n")
			while state != new_state:
				time.sleep(TIMEOUT_UBOOT_TO_LINUX)
				state = self.__prepare__()
			return state
		else:
			raise Exception("Invalid state tranistion request ({} --> {})".format(state, new_state))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='telnet board')
	parser.add_argument("board", help="Board ID")
	parser.add_argument("cmd", help="command")
	parser.add_argument('-v', '--verbose', action='store_true', help="Include debug prints in flash_board")
	
	args = parser.parse_args()

	logging.config.fileConfig(os.path.dirname(__file__)+'/logging.conf')

	t = CHDLAB_telnet(args.board, verbose=args.verbose)
	t.write(args.cmd)
