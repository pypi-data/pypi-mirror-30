#!/usr/bin/env python

from chdlab_jira import CHDLAB_jira
from chdlab_tftp import CHDLAB_tftp, VM_815_28_DUAL_BOOT_TFTP_Server
from chdlab_telnet import CHDLAB_telnet
from chdlab_flash import CHDLAB_flash
from urlparse import urlparse
from distutils.util import strtobool
import argparse
import getpass
import glob
import os
import sys
import time
import pexpect
import logging
import telnetlib
import logging.config


def print_color(string, color):
	colors = {'red':'31', 'yellow':'33', 'blue':'34', 'magenta':'35', 'turquoise':'36', 'white':'37'}
	attr = []
	attr.append(colors[color])
	attr.append('1')
	print '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

def ASSERT(string):
	print_color('ASSERT: %s' %(string), 'red')

def WARNING(string):
	print_color('%s' %(string), 'yellow')

def INFO(string):
	print_color('%s' %(string), 'magenta')

def prompt_user(query):
	sys.stdout.write('%s [y/n]: ' % query)
	val = raw_input()
	try:
		ret = strtobool(val)
	except ValueError:
		sys.stdout.write('Please answer with a y/n\n')
		return prompt(query)
	return ret

class chdlab(object):
	def __init__(self):
		self.logger = logging.getLogger('chdlab')
		self.parent_parser = argparse.ArgumentParser(description="chdlab")
		self.parent_parser.add_argument('--verbose', '-v', action='store_true', help="Verbosity on")
		self.child_parser = self.parent_parser.add_subparsers(title="subcommand", help="Subcommand help", dest='cmd')
		self.telnet_command = self.child_parser.add_parser('telnet', help="telnet to board")
		self.telnet_command.add_argument("board", help="board id")
		self.telnet_command.add_argument('--verbose', '-v', action='store_true', help="Verbosity on")
		self.telnet_command.add_argument('--force', action='store_true', help="force operation even if not your board")
		self.board_copy_command = self.child_parser.add_parser('copy', help="copy to/from board via tftp")
		self.board_copy_command.add_argument("file", nargs="+", help="path of file/s to copy (local or remote - see direction param)")
		self.board_copy_command.add_argument("direction",  choices=['to', 'from'], help="direction of copy - 'to' board or 'from' board")
		self.board_copy_command.add_argument("board", help="board id if direction of copy = 'from', or comma seperated board ids")
		self.board_copy_command.add_argument('-p', '--path', default='./', help="path to which the file will be copied")
		self.board_copy_command.add_argument('--verbose', '-v', action='store_true', help="Verbosity on")
		self.board_copy_command.add_argument('--force', action='store_true', help="force operation even if not your board")
		self.reset_command = self.child_parser.add_parser('reset', help="reset board")
		self.reset_command.add_argument("board", help="board id")
		self.reset_command.add_argument('--verbose', '-v', action='store_true', help="Verbosity on")
		self.reset_command.add_argument('--force', action='store_true', help="force operation even if not your board")
		self.flash_command = self.child_parser.add_parser('flash', help="flash board", epilog='''Examples:
		flash from path: chdlab.py flash [oav] board path
		flash buildbot:	 chdlab.py flash [oav] board branch tag model
			flash board #1 with latest wcci_master grx350 gw model:
					 chdlab flash [oav] 1 wcci_master latest gw
			flash board #1 with specific wcci_master tag gw model:
					 chdlab flash [oav] 1 wcci_master <tag> gw
			flash board #1 with specific wcci_master tag grx330 model:
					 chdlab flash [oav] 1 wcci_master <tag> grx330
			flash board #1 with specific wcci_master tag ire220 model:
					 chdlab flash [oav] 1 wcci_master <tag> ire''', formatter_class=argparse.RawDescriptionHelpFormatter)
		self.flash_command.add_argument("board", help="board id")
		self.flash_command.add_argument("version", nargs='+', help="Path to images or buildbot branch, tag and model (for example: chlab flash -o 5 wcci_master latest grx350")
		self.flash_command.add_argument('-a', '--all', action='store_true', help="Flash all images ((nandboot, bootcore, gphyfirmware, fullimage) instead of only fullimage")
		self.flash_command.add_argument('-o', '--remove-overlay', action='store_true', help="run rm -rf /overlay/*; sync; before flashing")
		self.flash_command.add_argument('--verbose', '-v', action='store_true', help="Verbosity on")
		self.args = self.parent_parser.parse_args()

		if self.args.verbose:
			self.logger.setLevel(logging.DEBUG)

		self.boards = self.args.board.split(',')
		self.jiras = []
		for board in self.boards:
			self.jiras.append(CHDLAB_jira(board))

		self.ci_rel_path = "/nfs/site/proj/chdsw_rel/ci/UGW_SW_" # ci release area
		# flash from buildbot supported models
		self.models = dict.fromkeys(['gw', 'grx350', 'grx350_1600_mr_eth_rt_72'], 'grx350_1600_mr_eth_rt_72')
		self.models.update(dict.fromkeys(['gw330', 'grx330', 'grx330_el_eth_rt_72'],'grx330_el_eth_rt_72'))
		self.models.update(dict.fromkeys(['ire', 'ire220', 'ire220_1600_mr_eth_rt_ire_72'],'ire220_1600_mr_eth_rt_ire_72'))

	def __str__(self):
		return str(self.args)

	def __user_valid__(self, board=None):
		try:
			if self.args.force:
				return True
		except:
			return True

		if board is None:
			jira = self.jiras[0]
			if jira.assignee != getpass.getuser():
				WARNING("User {} is not assigned to board {} (board {} is assigned to {})".format(getpass.getuser(), jira.board, jira.board, jira.assignee))
				return prompt_user("Are you sure?")
			return True
		else:
			for jira in self.jiras:
				if board == jira.board and jira.assignee != getpass.getuser():
					WARNING("User {} is not assigned to board {} (board {} is assigned to {})".format(getpass.getuser(), jira.board, jira.board, jira.assignee))
					return prompt_user("Are you sure?")
			return True

	def __telnet__(self):
		if len(self.boards) > 1:
			ASSERT("{} operation supports only single board".format(self.args.cmd))
			self.telnet_command.print_help()
			sys.exit(1)

		if not self.__user_valid__():
			WARNING("telnet board {} cancelled".format(jira.board))
			sys.exit(1)

		jira = self.jiras[0]
		ip, port = jira.telnet
		self.logger.info("start interactive telnet session to board #{} ({}:{}), press any key to start session, CTRL+D to terminate".format(jira.board, ip, port))
		try:
			tn = telnetlib.Telnet(ip, port)
			tn.interact()
		except KeyboardInterrupt:
			WARNING("\ngot KeyboardInterrupt exception\n")
			raise
		except:
			WARNING("\nUknown exception\n")
			raise

	def __flash__(self):
		if len(self.args.version) == 1:
			path = self.args.version[0]
		else:
			branch, tag, model = tuple(self.args.version)
			path = self.ci_rel_path + branch
			if not os.path.isdir(path):
				raise Exception("unknown branch '{}' ({} - no such directory".format(branch, path))
			if tag == 'latest':
				path = max(glob.glob(path+'/*/'), key=os.path.getctime)
			else:
				path = "{}/{}".format(path, tag)
				if not os.path.isdir(path):
					raise Exception("unknown tag '{}' ({} - no such directory".format(tag, path))
			try:
				model = self.models[model.lower()]
				path = "{}/{}/{}".format(path, model.upper(), model.lower())
				if not os.path.isdir(path):
					raise Exception("model '{}' not supported ({} - no such directory".format(model, path))
			except:
				ASSERT("unknown model '{}'".format(model))
				self.flash_command.print_help()
				raise

		for jira in self.jiras:
			if not self.__user_valid__(jira.board):
				WARNING("{} board {} cancelled".format(self.args.cmd, jira.board))
				continue
			images = ['fullimage']
			if self.args.all:
				if jira.type in {"GRX350", "IRE220"}:
					images=['nandboot', 'bootcore', 'gphyfirmware', 'fullimage']
				elif jira.type in {"GRX330"}:
					images=['nandboot', 'gphyfirmware', 'fullimage']
				else:
					ASSERT("Board type {} not supported, skipping".format(self.jira.type))
					continue
			try:
				self.logger.info("flash board #{} start".format(jira.board))
				f = CHDLAB_flash(jira.board, path, verbose=self.args.verbose, images=images, remove_overlay=self.args.remove_overlay, jira=jira)
				f.flash()
				f.cleanup()
				self.logger.info("flash board #{} done".format(jira.board))
			except Exception as e:
				ASSERT(e)
				continue

	def __reset__(self):
		for jira in self.jiras:
			if not self.__user_valid__(jira.board):
				WARNING("{} board {} cancelled".format(self.args.cmd, jira.board))
				continue
			self.logger.info("reset board #{}".format(jira.board))
			ip, port = jira.apc
			self.logger.debug("board #{} OFF".format(jira.board))
			os.system("snmpset -v1 -cprivate {} .1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.{} i 2 &> /dev/null".format(ip, port))
			time.sleep(3)
			self.logger.debug("board #{} ON".format(jira.board))
			os.system("snmpset -v1 -cprivate {} .1.3.6.1.4.1.318.1.1.12.3.3.1.1.4.{} i 1 &> /dev/null".format(ip, port))

	def __copy_from_board__(self):
		if len(self.boards) > 1:
			ASSERT("{} operation supports only single board".format(self.args.cmd))
			self.board_copy_command.print_help()
			sys.exit(1)

		jira = self.jiras[0]
		if not self.__user_valid__(jira.board):
			WARNING("copy {} from board {} cancelled".format(self.args.file, jira.board))
			sys.exit(1)

		telnet = CHDLAB_telnet(board=jira.board, jira=jira)
		tftp = jira.tftp_secondary
		for file in self.args.file:
			file_name = os.path.basename(file)
			tftppath = tftp.tftppath+"/"
			dir = os.path.dirname(file)
			path = self.args.path

			if not tftp.put_supported:
				raise Exception("PUT not supported for {}".format(tftp.server))

			self.logger.info("copy from board #{}: {}".format(jira.board, file))
			self.logger.debug("file={}, file_name={}, dir={}, path={}".format(file, file_name, dir, path))
			telnet.state_change('linux')
			telnet.write("ip a add {}/24 dev br-lan".format(tftp.get_board_local_ip(jira.board)))
			if dir:
				telnet.write("cd %s" %dir)
			telnet.write("for f in $(ls {}); do tftp -p -l $f {} -r {}/$f; done".format(file_name, tftp.local_ip, tftppath))
			telnet.write("ip -s -s a f to {}/24".format(tftp.get_board_local_ip(jira.board)))
			tftp.copy_from_tftp(file_name, path)

	def __copy_to_board__(self):
		for jira in self.jiras:
			if not self.__user_valid__(jira.board):
				WARNING("copy {} to board {} cancelled".format(self.args.file, jira.board))
				continue

			INFO("copy {} to board {}".format(self.args.file, jira.board))
			tftp = jira.tftp_secondary
			telnet = CHDLAB_telnet(board=jira.board, jira=jira)
			server_ip = tftp.local_ip

			telnet.state_change('linux')
			telnet.write("ip a add {}/24 dev br-lan".format(tftp.get_board_local_ip(jira.board)))
			for f in self.args.file:
				file  = os.path.abspath(f)
				file_name = os.path.basename(file)
				file_perm = oct(os.stat(file).st_mode & 0777)
				path = self.args.path
				if not os.path.exists(file):
					WARNING("{} no such file or directory".format(file))
					continue
				if os.path.isdir(file):
					WARNING("{} is a directory".format(file))
					continue
				self.logger.info("copy {} to board #{}: /tmp/".format(file, jira.board))
				tftp.copy_to_tftp(file)
				tftppath = tftp.tftppath+'/'+file_name
				telnet.write("tftp -g -r {} {} -l {}/{}".format(tftppath, server_ip, path, file_name))
				telnet.write("chmod {} {}/{}".format(file_perm, path, file_name))
			telnet.write("ip -s -s a f to {}/24".format(tftp.get_board_local_ip(jira.board)))

	def run(self):
		if not self.__user_valid__():
			self.logger.info("{} operation cancelled".format(self.args.cmd))
		elif self.args.cmd == 'telnet':
			self.__telnet__()
		elif self.args.cmd == 'flash':
			self.__flash__()
		elif self.args.cmd == 'reset':
			self.__reset__()
		elif self.args.cmd == 'copy':
			if self.args.direction == 'to':
				self.__copy_to_board__()
			elif self.args.direction == 'from':
				self.__copy_from_board__()
		else:
			raise Exception("operation not supported ({})".format(self.args.cmd))

if __name__ == '__main__':
	logging.config.fileConfig(os.path.dirname(__file__)+'/logging.conf')
	try:
		chdlab().run()
	except Exception as e:
		ASSERT(e)
		raise
