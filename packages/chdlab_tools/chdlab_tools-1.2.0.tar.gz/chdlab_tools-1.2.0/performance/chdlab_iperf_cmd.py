import re
import sys

from chdlab_print import Print

TCP_SERVER_CMD_INDEX = 0
TCP_CLIENT_CMD_INDEX = 1
UDP_SERVER_CMD_INDEX = 2
UDP_CLIENT_CMD_INDEX = 3

class IperfCommand:
	"""	IperfCommand represents iperf/iperf3 commands

		attributes:
			type (str):				type is the key in templates used to identify iperf command
			server (str):			iperf command to run at server
			client (str):			iperf comamnd to run at client
	"""
	
	# TODO: set iperf commands according to type from iperf_cmd.conf file instead of writing them here?
	templates = {					 
					"quick-check":  # mandatory parameters for iperf and script to work are in the quick-check, use it as a template
										("iperf3 -s -p PORT > iperf.err &",
										 "iperf3 -c SERVER_HOST -p PORT -t 1 > OUTPUT_FILE &",
										 "iperf -u -s -p PORT -i 1 > OUTPUT_FILE &",
										 "iperf -u -c SERVER_HOST -p PORT -i 1 -t 1 > iperf.err &"),
									 
					"sanity":			("iperf3 -s -p PORT > iperf.err &",
										 "iperf3 -c SERVER_HOST -p PORT -t 30 > OUTPUT_FILE &",
										 "iperf -u -s -p PORT -i 1 > OUTPUT_FILE &",
										 "iperf -u -c SERVER_HOST -p PORT -i 1 -t 30 -b 1000M > iperf.err &"),
										 
					"perf-quick-check":	# used in set_udp_perf_bandwidth
										(None, # not needed for TCP
										 None, # not needed for TCP
										 "iperf -u -s -p PORT -i 1 > OUTPUT_FILE &",
										 "iperf -u -c SERVER_HOST -p PORT -i 1 -t 5 -b BANDWIDTH > iperf.err &"),
										 
					"performance":		("iperf3 -s -p PORT > iperf.err &",
										 "iperf3 -c SERVER_HOST -p PORT -t 300 -O 10 > OUTPUT_FILE &",
										 "iperf -u -s -p PORT -i 1 > OUTPUT_FILE &",
										 "iperf -u -c SERVER_HOST -p PORT -i 1 -t 300 -b 1000M > iperf.err &"),
					
					"endurance":		("iperf3 -s -p PORT > iperf.err &",
										 "iperf3 -c SERVER_HOST -p PORT -t 43200 > OUTPUT_FILE &",
										 "iperf -u -s -p PORT -i 1 > OUTPUT_FILE &",
										 "iperf -u -c SERVER_HOST -p PORT -i 1 -t 43200 -b 1000M > iperf.err &"),
										 
					"downstream-quick":	("iperf3 -s -p PORT > iperf.err &",
										 "iperf3 -c SERVER_HOST -p PORT -R -t 10 > OUTPUT_FILE &",
										 None,	# -R is not supported in iperf2
										 None), # -R is not supported in iperf2
									 
					"downstream-load":	("iperf3 -s -p PORT > iperf.err &",
										 "iperf3 -c SERVER_HOST -p PORT -R -t 300 > OUTPUT_FILE &",
										 None,	# -R is not supported in iperf2
										 None), # -R is not supported in iperf2
										 
					"downstream-low":	("iperf3 -s -p PORT > iperf.err &",
										 "iperf3 -c SERVER_HOST -p PORT -R -t 300 -b 50M > OUTPUT_FILE &",
										 None,	# -R is not supported in iperf2
										 None)	# -R is not supported in iperf2
				}
	""" the syntax of templates is as follows:
		<iperf_command_name>:
							(<TCP_server_command>,
							 <TCP_client_command>,
							 <UDP_server_command>,
							 <UDP_client_command>)
		all of <> above are str
		PORT, SERVER_HOST, OUTPUT_FILE, BANDWIDTH must be replaced according to request
		manfatory requirement for this module to work: all parameters must be separated (e.g. -u -s instead of -us)
	"""
	
	class Error(Exception):
		""" Basic exception for errors raised by IperfCommand """
		
		def __init__(self, iperf_cmd, message="ERROR: IperfCommand operation failed"):

			super(IperfCommand.Error, self).__init__("IperfCommand operation failed ({})\n{}".format(iperf_cmd, message))
			self.iperf_cmd = iperf_cmd
		
	def __init__(self, type):
	
		self.type = type
		
	def __str__(self):
	
		return '%s instance:\n' % (self.__name__) + '\n'.join("%s: %s" % item for item in vars(self).items())
		
	@classmethod
	def create(cls, type, protocol):
		""" accepts only strings and validates them """

		instance = None
		accepted_protocols = ["UDP", "TCP"] # not case sensitive
		protocol = protocol.upper()
	
		# validate type
		if type.lower() not in cls.templates:
			Print.ERROR("Invalid iperf command type: %s" % (type))
			raise ValueError

		# validate and handle protocol
		if protocol not in accepted_protocols:
			Print.ERROR("Not a valid protocol: %s" % (protocol))
			raise ValueError
			
		if protocol == "UDP":
			instance = UDPIperfCommand(type)
		else: # protocol == "TCP"
			instance = TCPIperfCommand(type)
	
		return instance
		
###	iperf parameters gets ###
		
	def get_summary_line(self, stream):
		""" "abstract" method - raises an error """
		raise IperfCommand.Error(self, "get_summary_line is an \"abstract\" method. Should be called from child classes.")
		
	def get_protocol(self):
		""" returns protocol according to child class """
	
		if isinstance(self, UDPIperfCommand):
			return "UDP"
		if isinstance(self, TCPIperfCommand):
			return "TCP"
		
	def get_param(self, param, endpoint="client"):
		""" tries finding param in endpoint specified, if exists returns value, raises an Exception otherwise """
	
		if endpoint == "client":
			param_split = self.client.split(param)
		elif endpoint == "server":
			param_split = self.server.split(param)
		else:
			raise IperfCommand.Error(self, "not a valid endpoint specified: %s" % (endpoint))

		try:
			param_value = param_split[1].split()[0] # tries finding the first word after param
		except IndexError:
			raise IperfCommand.Error(self, "no \"%s\" param specified" % (param))
			
		return param_value

	def get_output_file_name(self):
		""" "abstract" method - raises an error """
		raise IperfCommand.Error(self, "get_output_file_name is an \"abstract\" method. Should be called from child classes.")

	def get_time(self):
		""" returns the time iperf command should run """
		
		DEFAULT_TIME = 10
		
		try:
			time_value = self.get_param("-t")
		except: # no -t param specified
			iperf_time = DEFAULT_TIME
		else:
			iperf_time = time_value
			
		try:
			time_value = self.get_param("-O")
		except:
			pass
		else:
			iperf_time = str( int(iperf_time) + int(time_value))

		return int(iperf_time)
		
	def get_port(self):
		""" returns the iperf command port """
		return self.get_param("-p")
		
###	iperf parameters sets ###
		
	def set_param(self, param, new_value, endpoint="client"):

		if endpoint == "client":
			iperf_cmd_string = self.client
		elif endpoint == "server":
			iperf_cmd_string = self.server
		else:
			raise IperfCommand.Error(self, "Invlid endpoint specified: %s" % (endpoint))
	
		if param not in iperf_cmd_string: # adds param
			iperf_cmd_string = re.sub(">", str(param + " " + new_value + " >"), iperf_cmd_string)
		else: # replaces param
			param_value = iperf_cmd_string.split(param)[1].split()[0] # gets the first word after the specified param
			iperf_cmd_string = re.sub(param + " " + param_value, param + " " + new_value, iperf_cmd_string)
			
		if endpoint == "client":
			self.client = iperf_cmd_string
		elif endpoint == "server":
			self.server = iperf_cmd_string
			
		Print.DEBUG("iperf_cmd_string: %s" % (iperf_cmd_string))
		return iperf_cmd_string
		
###	mandatory parameters specifications - used in Stream's set_iperf_cmd_specifications###
		
	def set_port(self, port):
		
		self.set_param("-p", str(port))
		self.set_param("-p", str(port), "server")
		
	def set_server_host(self, server_host):
	
		self.set_param("-c", server_host)
		
	def set_output_file_name(self):
		""" "abstract" method - raises an error """
		raise IperfCommand.Error(self, "set_output_file_name is an \"abstract\" method. Should be called from child classes.")
		
###	non-mandatory parameters specifications ###
		
	def set_bandwidth(self, bandwidth):
	
		self.set_param("-b", str(bandwidth) + "M")
		
	def set_time(self, time):
	
		self.set_param("-t", str(time))
		
### child classes of IperfCommand ###
		
class TCPIperfCommand(IperfCommand):

	def __init__(self, type):
		IperfCommand.__init__(self, type)
		
		self.server = self.templates[self.type][TCP_SERVER_CMD_INDEX]
		self.client = self.templates[self.type][TCP_CLIENT_CMD_INDEX]
		
		if self.server == None or self.client == None:
			raise IperfCommand.Error(self, "\"%s\" type of iperf command is not supported with TCP" % (self.type))
			
	def __str__(self):
	
		return 'TCPIperfCommand instance\n' + '\n'.join("%s: %s" % item for item in vars(self).items())
			
###	mandatory parameters specifications ###
		
	def set_output_file_name(self):

		self.set_param(">", self.type + '_' + self.get_protocol() + '_' + self.get_port() + '.log')
			
###	data analyzing ###

	def get_output_file_name(self):

		return self.get_param(">")

class UDPIperfCommand(IperfCommand):

	def __init__(self, type):
		IperfCommand.__init__(self, type)
	
		self.server = self.templates[self.type][UDP_SERVER_CMD_INDEX]
		self.client = self.templates[self.type][UDP_CLIENT_CMD_INDEX]
		
		if self.server == None or self.client == None:
			raise IperfCommand.Error(self, "\"%s\" type of iperf command is not supported with UDP" % (self.type))

	def __str__(self):
	
		return 'UDPIperfCommand instance\n' + '\n'.join("%s: %s" % item for item in vars(self).items())
			
###	mandatory parameters specifications ###
		
	def set_output_file_name(self):
	
		self.set_param(">", self.type + '_' + self.get_protocol() + '_' + self.get_port() + '.log', "server")
			
###	data analyzing ###

	def get_output_file_name(self):

		return self.get_param(">", "server")
	