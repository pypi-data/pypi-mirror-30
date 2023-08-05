#!/usr/bin/env python

from chdlab_jira import CHDLAB_jira
from chdlab_telnet import CHDLAB_telnet
from chdlab_buildbot import CHDLAB_buildbot
from urlparse import urlparse
import argparse
import getpass
import os
import sys
import time
import pexpect
import logging
import telnetlib
import logging.config
import re

TIMEOUT_LINUX_TO_UBOOT = 3
TIMEOUT_UBOOT_TO_LINUX = 10

def print_color(string, color):
	colors = {'red':'31', 'yellow':'33', 'blue':'34', 'magenta':'35', 'turquoise':'36', 'white':'37'}
	attr = []
	attr.append(colors[color])
	attr.append('1')
	print '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

def ASSERT(string):
	print_color('ASSERT: %s' %(string), 'red')

class CHDLAB_flash(object):
	def __init__(self, board, path, verbose=False, user='admin', password='admin', images=['fullimage'], remove_overlay=False, jira=None):
		self.logger = logging.getLogger('flash_board')
		if verbose:
			self.logger.setLevel(logging.DEBUG)
		self.user = user
		self.images_dict = {'fullimage' : 'fullimage.img', 'nandboot' : 'u-boot-nand.bin', 'bootcore' : 'uImage_bootcore', 'gphyfirmware' : 'gphy_firmware.img'}
		self.images = images
		self.password = password
		self.remove_overlay = remove_overlay
		self.board = board
		if not jira:
			self.jira = CHDLAB_jira(board, verbose=verbose)
		else:
			self.jira = jira
		if self.jira.type not in {"GRX350", "IRE220", "GRX330"}:
			raise Exception("Board type {} not supported (JIRA={})".format(self.jira.type, self.jira.issue))
		if self.jira.assignee != getpass.getuser():
			raise Exception("User {} is not assigned to board {} (board {} is assigned to {}) - this incident will be reported!".format(getpass.getuser(), board, board, self.jira.assignee))

		self.telnet = CHDLAB_telnet(board=self.board, jira=self.jira, verbose=verbose)
		self.tftp = self.jira.tftp
		self.buildbot = None
		self.path = path
		if self.jira.type.lower() not in self.path.lower():
			raise Exception("Trying to flash {} board with wrong images ({})".format(self.jira.type, self.path))
		try:
			self.buildbot = CHDLAB_buildbot(path)
			self.logger.info("download images from buildbot %s" %str(self.buildbot))
			self.path = self.buildbot.download("/tmp/{}".format(getpass.getuser()))
			self.logger.info("download images done")
		except:
			self.logger.debug("non buildbot path[=%s]" %path)
			pass

		if not os.path.isdir(self.path):
			raise Exception("Invalid images path %s (must be a directory)" %self.path)
		for image in images:
			image_path = self.path+'/'+self.images_dict[image]
			if not os.path.exists(image_path):
				raise Exception("{} selected but does not exist ({} - no such file)".format(image, image_path))
		self.tftp.copy_to_tftp(self.path)
		self.tftppath = self.tftp.tftppath+'/'+os.path.basename(os.path.dirname(self.path+'/'))+'/'

	def __str__(self):
		return "flash board #{} (setup #{} jira {}) images: path={}, types={}, remove_overlay={}".format(self.board, self.jira.setup, self.jira.issue, self.path, self.images, self.remove_overlay)

	def uboot_set_env(self):
		self.logger.debug("set uboot params")
		self.telnet.write("setenv tftppath {}".format(self.tftppath))
		self.telnet.write("setenv ipaddr {}".format(self.tftp.get_board_local_ip(self.board)))
		self.telnet.write("setenv serverip {}".format(self.tftp.local_ip))
		self.telnet.write("saveenv")

	def uboot_set_mac(self):
		if self.jira.board_mac:
			self.logger.info("update MAC address to {}".format(self.jira.board_mac))
			self.telnet.write("set ethaddr {}".format(self.jira.board_mac))
			self.telnet.write("saveenv")

	def uboot_update_image(self, type):
		if type not in {'nandboot', 'bootcore', 'gphyfirmware', 'fullimage'}:
			raise Exception("Invalid update image type {}".format(type))

		self.logger.info("update image: {}".format(type))
		self.telnet.write("run update_{}; reset".format(type))

	def flash(self):
		self.logger.info(str(self))
		if self.remove_overlay:
			self.telnet.state_change("linux")
			self.telnet.write("rm -rf /overlay/*; sync;")
		self.telnet.state_change("uboot")
		for image in self.images:
			self.uboot_set_env()
			self.uboot_update_image(image)
		self.uboot_set_mac()
		self.logger.info("Done, trigger reset")
		self.telnet.write_raw("reset\n")

	def cleanup(self):
		if self.buildbot:
			self.buildbot.cleanup()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='flash board')
	parser.add_argument("board", help="Board ID")
	parser.add_argument("path", help="Path to images (local path or buildbot path)")
	parser.add_argument('-v', '--verbose', action='store_true', help="Include debug prints in flash_board")
	parser.add_argument('-a', '--all', action='store_true', help="Flash all images ((nandboot, bootcore, gphyfirmware, fullimage) instead of only fullimage")
	parser.add_argument('-o', '--remove-overlay', action='store_true', help="run rm -rf /overlay/*; sync; before flashing")
	args = parser.parse_args()

	logging.config.fileConfig(os.path.dirname(__file__)+'/logging.conf')

	images = ['fullimage']
	if args.all:
		images=['nandboot', 'bootcore', 'gphyfirmware', 'fullimage']

	try:
		f = CHDLAB_flash(args.board, args.path, verbose=args.verbose, images=images, remove_overlay=args.remove_overlay)
		f.flash()
		f.cleanup()
	except Exception as e:
		ASSERT(e)
		raise

