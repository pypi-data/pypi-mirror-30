from __future__ import print_function

import sys
import re
import time
import os

from chdlab_print import Print
from chdlab_endpoint import Endpoint
from chdlab_iperf_cmd import IperfCommand, UDPIperfCommand, TCPIperfCommand

class Stream:
	"""	Stream instance represents IperfCommand from client to server Endpoints
		
		instance attributes:
			client_endpoint (Endpoint):	Endpoint from which the iperf client command should run
			server_endpoint (Endpoint):	Endpoint from which the iperf server command should run
			iperf_cmd (IperfCommand):	IperfCommand used to specify server-client commands and Stream procedures
			results (string, None):		iperf summary: stream description, fail/pass status, TPT [packet_loss] or fail reasons
	"""
	
	class Error(Exception):
	    """ Basic exception for errors raised by Stream """
		
	    def __init__(self, stream, message="ERROR: stream operation failed"):
		
		super(Stream.Error, self).__init__("CHDLAB_jira operation failed ({})\n{}".format(stream, message))
		self.stream = stream
	
	def set_result(self):
	
		self.result = str("%s from %s to %s:\n" % (self.iperf_cmd.type, self.client_endpoint.management_ip, self.server_endpoint.management_ip))
	
	def __init__(self, client_endpoint, server_endpoint, iperf_cmd):
		""" sets Stream's attributes """
	
		self.client_endpoint = client_endpoint
		self.server_endpoint = server_endpoint
		self.iperf_cmd = iperf_cmd
		self.set_result()
		
	def __str__(self):
	
		return 'Stream instance:\n' + '\n'.join("%s: %s" % item for item in vars(self).items())
		
	@classmethod
	def create(cls, client, server, iperf_cmd):
		""" accepts Endpoint object, string of management_ip, string of vm name as client and server
			returns instance of a Stream
		"""
	
		try:
			client_endpoint = Endpoint.create(client)
			server_endpoint = Endpoint.create(server)
		except ValueError:
			Print.ERROR("invalid Stream Endpoints: %s, %s" % (client, server))
			raise ValueError('Stream')
			
		# TODO: add IperfCommand.create that accepts string (from cmd or from config file) and IperfCommand
			
		instance = cls(client_endpoint, server_endpoint, iperf_cmd)

		return instance
		
	def set_iperf_cmd_specifications(self, port):
		""" specifies SERVER_HOST, PORT, CLIENT_FILE and SERVER_FILE according to specific Stream
			mandatory parameters for iperf command to run """
	
		self.iperf_cmd.set_server_host(self.server_endpoint.setup_ip_address)
		self.iperf_cmd.set_port(port)
		self.iperf_cmd.set_output_file_name()
		
###	functions related to running the traffic ###

	def debug_connectivity(self):
		""" tries to help user find cause for Stream not to pass """
		
		self.result += self.client_endpoint.check_ping_pass_to(self.server_endpoint) + '\n'
		self.result += sself.server_endpoint.check_ping_pass_to(self.client_endpoint) + '\n'
			
		self.result += sself.client_endpoint.check_route_to(self.server_endpoint) + '\n'
		self.result += sself.server_endpoint.check_route_to(self.client_endpoint) + '\n'
		
		self.result += sself.client_endpoint.check_link_exists() + '\n'
		self.result += sself.server_endpoint.check_link_exists() + '\n'
			
	@classmethod
	def countdown(cls, seconds, interval=1):
		""" waits the number of seconds specified
			prompts user every specified interval how much time is left """
			
		FOR_LUCK = 2
	
		pad_str = str(' ' * len('%d' % interval))
		seconds = int(seconds) + FOR_LUCK
		
		for i in range(seconds, 0, -interval):
			# do not use prints module
			print('time left: %d seconds %s\r' % (i, pad_str), end='')
			sys.stdout.flush()
			time.sleep(interval)
			
	def run_server(self):
		""" leaves iperf server running """
		
		server_res = self.server_endpoint.send_command(self.iperf_cmd.server)
		Print.INFO("server is running")
		
	def run_client(self):
		""" leaves iperf client running """
	
		self.client_endpoint.send_command(self.iperf_cmd.client)
		Print.INFO("client is running")
	
	def quick_check(self):
		""" verifies a single quick check stream passes
			returns whether it passed
		"""
	
		QUICK_CHECK_PORT = 8000
		endpoint = None
		
		original_time = self.iperf_cmd.get_time()
		self.iperf_cmd.set_time(1)
		
		# execute
		Print.INFO("trying to run quick-check")
		self.result += "quick check: "
		self.run_server()
		self.run_client()
		self.countdown(self.iperf_cmd.get_time())
		
		try:
			self.get_summary_line()
		except:
			self.debug_connectivity()
			raise Stream.Error(self, self.result)
		finally:
			self.clear_logs()
			self.iperf_cmd.set_time(int(original_time))
		
### functions related to data analyzing of iperf results ###

	def get_output_endpoint(self):
		""" returns the endpoint which hold the file with output """
	
		if isinstance(self.iperf_cmd, UDPIperfCommand):
			return self.server_endpoint
		elif isinstance(self.iperf_cmd, TCPIperfCommand):
			return self.client_endpoint
		else:
			raise Stream.Error(self, "Invalid iperf_cmd type")
		
	def get_summary_line(self):
		""" returns summary line if exists, raises error otherwise """
		
		matcher_tp = re.compile(r'.* +(?P<tp>[0-9,.]+ +[M,K]bits/sec).*')
		matcher_pkt_loss = re.compile(r'.* +\((?P<pkt_loss>[0-9,.]+)%\).*')
		
		results_line = None
		
		endpoint = self.get_output_endpoint()
		Print.DEBUG("get_summary_line: output_file_name: %s" % (self.iperf_cmd.get_output_file_name()))
		tail_results = endpoint.send_command("tail -3 " + self.iperf_cmd.get_output_file_name()).splitlines()
		
		for line in tail_results:
			if matcher_tp.search(line):
				results_line = line

		if results_line is not None:
			Print.INFO("data reached server: %s" % (results_line))
			self.result += "passed\n"
			self.result += str(matcher_tp.search(results_line).group('tp') + ' ')	# TPT
			if isinstance(self.iperf_cmd, UDPIperfCommand):
				self.result += " " + str((matcher_pkt_loss.search(results_line)).group('pkt_loss')) + "%"	# packet loss
		else:
			Print.ERROR("data did not reach server")
			self.result += "failed\n"
			self.debug_connectivity()
			raise Stream.Error(self, "data did not reach server")
		
	def get_tp_from_summary(self):
	
		results_line = self.get_summary_line()
		
		if results_line:
			return float((matcher_tp.search(results_line)).group('tp').split(' ')[0])
		else:
			raise Stream.Error(self, "something is wrong. no results")

	def clear_logs(self):
		""" clears the iperf log files on both the server and client """

		output_endpoint = self.get_output_endpoint()
		file_name = self.iperf_cmd.get_output_file_name()

		output_endpoint.send_command("rm \"%s\"" % (file_name))
		self.set_result()
		
		Print.INFO("cleared all log files from %s and cleared result" % (output_endpoint.management_ip))

		# TODO: pytest
		# check_cmd = "ls -l | grep %s" % (file_name)
		# Print.DEBUG("%s: %s" % (check_cmd, output_endpoint.send_command(check_cmd)))
