#!/usr/bin/env python

import logging
import logging.config
import argparse
import os
import getpass
import ipaddress

class tftp_server(object):
	def __init__(self, root, path, ip, local_ip, user, password, put_supported=False, name="Unknown TFTP Server"):
		self.name = name
		self.root = root
		self.ip = ip
		self.local_ip = local_ip
		self.user = user
		self.password = password
		self.path = path
		self.put_supported = put_supported

	def __str__(self):
		return "{}: root={} path={} ip={} local_ip={} user={} password={} put_supported={}".format(self.name, self.root, self.path, self.ip, self.local_ip, self.user, self.password, self.put_supported)


CHD_DEFAULT_TFTP_SERVER = tftp_server(name="CHD Default TFTP", root="/home/tftproot", path="localDisk/users", ip="10.100.242.25", local_ip="198.62.1.1", user="syncuser", password="qwerty")
VM_815_28_DUAL_BOOT_TFTP_Server = tftp_server(name="VM_815_28_DUAL_BOOT_TFTP_Server", root="/tftpboot", path="localDisk/users", ip="10.124.123.56", local_ip="198.63.1.1", user="libit", password="libit", put_supported=True)
DEFAULT_TFTP_SERVER = CHD_DEFAULT_TFTP_SERVER

class CHDLAB_tftp(object):
	def __init__(self, server=DEFAULT_TFTP_SERVER, verbose=False):
		self.server = server
		self.root = server.root
		self.ip = server.ip
		self.local_ip = server.local_ip
		self.user = server.user
		self.password = server.password
		self.path = server.path
		self.put_supported = server.put_supported
		self.fullpath = "{}/{}/{}/".format(self.root, self.path, getpass.getuser())
		self.tftppath = "{}/{}".format(self.path, getpass.getuser()) # updated after copy operation
		self.logger = logging.getLogger('tftp')
		if verbose:
			self.logger.setLevel(logging.DEBUG)
		self.__mkdir__(self.fullpath)

	def get_board_local_ip(self, board):
		return ipaddress.ip_network(unicode("%s/24" %self.local_ip), strict=False).network_address+int(board)+100

	def __mkdir__(self, path):
		self.logger.debug("mkdir -p {} at {}@{}".format(path, self.user, self.ip))
		cmd="sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} mkdir -p {}".format(self.password, self.user, self.ip, path)
		self.logger.debug(cmd)
		os.system(cmd)
		#cmd="sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} chmod 777 {}".format(self.password, self.user, self.ip, path)
		#self.logger.debug(cmd)
		#os.system(cmd)

	def copy_to_tftp(self, lpath):
		if not os.path.exists(lpath):
			raise Exception("No such file or diretocry ({})".format(lpath))
		self.logger.info("copy {} to {}@{}:{}".format(os.path.abspath(lpath), self.user, self.ip, self.fullpath))
		cmd = "sshpass -p {} scp -r {} {}@{}:{}".format(self.password, os.path.abspath(lpath), self.user, self.ip, self.fullpath)
		self.logger.debug(cmd)
		return os.system(cmd)

	def copy_from_tftp(self, rpath, lpath="./"):
		self.logger.info("copy {}@{}:{} to {}".format(self.user, self.ip, self.fullpath+rpath, lpath))
		cmd = "sshpass -p {} scp -r {}@{}:{} {}".format(self.password, self.user, self.ip, self.fullpath+rpath, lpath)
		self.logger.debug(cmd)
		return os.system(cmd)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='chdlab tftp')
	parser.add_argument("path", help="Path to images")
	parser.add_argument('-v', '--verbose', action='store_true')
	args = parser.parse_args()

	logging.config.fileConfig(os.path.dirname(__file__)+'/logging.conf')

	tftp = CHDLAB_tftp(verbose=args.verbose)
	tftp.copy_to_tftp(args.path)

