import re
import os
import sys
import time
import argparse

from chdlab_print import Print
from chdlab_file_handler import FileHandler
from chdlab_endpoint import Endpoint
from chdlab_stream import Stream
from chdlab_iperf_cmd import IperfCommand, UDPIperfCommand, TCPIperfCommand
from chdlab_jira import CHDLAB_jira
from chdlab_telnet import CHDLAB_telnet

start_time = time.time()
PERF_LIB_PATH = "./performance/"
PERF_OUTPUT_NAME = "traffic_run_summary.out"

# TODO: temporary
#BOARD_NUMBER = "23"
#CPU_record_file_name = "CPU_recording.txt"
#board_jira = CHDLAB_jira(BOARD_NUMBER)
#board_telnet = CHDLAB_telnet(BOARD_NUMBER)
#board_telnet.state_change("linux")
#board_telnet.__prepare__()
		
class TrafficRun:
	""" TrafficRun represents multiple Streams running simultaneously 
		makes sure there are no conflicts when running multiple Streams (port numbers and kill_iperf) and no waste of time and resources (same Endpointss used in multiple Stream)
		
		class variables:
			port (int):					initial port number to be incremented for each Streami
			summary (string):				summary of all TrafficRuns

		instance attributes:
			name (str):					friendly name
			streams (Stream list):		all Streams to be run
			sleep (int):				time [seconds] to sleep for traffic to finish running (for fetching logs and running next TrafficRuns if exist)
			result (string):			iperf outputs of streams (success/fail, TPT, packet loss, etc)
	"""

	@staticmethod
	def single_stream(board_jira, argv):
		
		protocol = "TCP"	# default value
			
		parser = argparse.ArgumentParser()
		parser.add_argument("source", help="ip address of vm or vm name from which to run iperf client. e.g. \"814vm01\" or \"10.124.123.1\".", type=str)
		parser.add_argument("destination", help="ip address of vm or vm name from which to run iperf server. e.g. \"814vm01\" or \"10.124.123.1\".", type=str)
		parser.add_argument("type", help="look at iperf_list at iperf_cmd.py for specifics.", type=str)
		parser.add_argument('-u', '--udp', help="use UDP protocol. used TCP by default.", action='store_true')
		parser.add_argument('-b', '--board', help='id of board to get CPU load from', default=None)
		parser.add_argument('-e', '--excel', help="generate graph in excel from iperf output files. not yet supported.", action='store_true')
		args = parser.parse_args(argv)
			
		tr = TrafficRun("TrafficRun parsed from command line")
			
		if args.udp:
			protocol = "UDP"
			
		tr.add_stream(Stream.create(args.source, args.destination, IperfCommand.create(args.type, protocol)))
		tr.execute()

		if args.excel:
			# TODO:
			# get all of the output files to enviorment using scp
			# change converty.py to be a class so it could be imported
			# change convert.py so it will separate results to different sheets (for each stream in current cases)
			# run convert.pt *.log with separation of sheets
			pass

	@staticmethod
	def parse_from_file(file_name):

		traffic_runs = []
		number_of_trs = 0
		line_number = 1
		summary = ""
		
		start_time = time.time()
		
		# input file handeling
		input_file = FileHandler.open_input_file(file_name)
		
		for input_line in input_file:
		
			# try to parse line
			if input_line[0] != '#':
				# if it is a traffic name line
				if input_line[0] == '%':
					traffic_runs.append(TrafficRun(input_line[1:-1]))
					number_of_trs += 1
				else:
					args = input_line.split()
					if len(args) != 4 and len(args) != 0:
						Print.ERROR("file %s: line %i: invalid number of arguments" % (file_name, line_number))
						sys.exit(1)
					# tries parsing arguemnts
					if len(args) != 0:
						traffic_runs[number_of_trs-1].add_stream(Stream.create(args[0], args[1], IperfCommand.create(args[2], args[3])))
			line_number += 1
			
		input_file.close()
		
		# executing, recording CPU load and TPT
		#board_telnet.write_raw("rm %s" % (CPU_record_file_name))
		
		for tr in traffic_runs:
			tr.execute()

		Print.INFO("execution time: %s seconds" % (time.time() - start_time)) # could also just try: time python traffic_run.py ...

	
        summary = "Summary of TrafficRun\n"
	output_file = None
	DEFAULT_SLEEP = 30 # used 30 seconds because of mpstat command
	port = 10000

	@staticmethod
	def wisp_stability():

		cycle = 1

		tr = TrafficRun("Stability")
		STA5_16 = Endpoint.create("814VM16")
		STA5_61 = Endpoint.create("10.124.123.61")
		DUT_19 = Endpoint.create("814vm19")
		STA24_18 = Endpoint.create("814vm18")
		FAR_21 = Endpoint.create("814vm21")
		FAR_43 = Endpoint.create("10.124.123.43")

		for endpoint in Endpoint.endpoints:
			endpoint.send_command("rm *.log")

		tr.add_stream(Stream.create(FAR_43, DUT_19, IperfCommand.create("endurance", "UDP")))
		tr.add_stream(Stream.create(STA5_61, FAR_21, IperfCommand.create("endurance", "TCP")))
		tr.add_stream(Stream.create(FAR_21, STA5_16, IperfCommand.create("endurance", "TCP")))
		tr.add_stream(Stream.create(FAR_43, STA24_18, IperfCommand.create("endurance", "TCP")))

		while (True):

			Print.INFO("executing %s cycle #%d" % (tr.name, cycle))

			if tr.prepare_streams():

				for stream in tr.streams:
					file_name = stream.iperf_cmd.get_output_file_name()
					file_name = file_name.replace(".log", str("_cycle_%d" % (cycle)) + ".log")
					stream.iperf_cmd.set_client_param(">", file_name)
					stream.iperf_cmd.set_server_param(">", file_name)

				tr.run_requested_streams()
				tr.gather_results()

			result = str("\n" + tr.name + "\n" + tr.result)
			TrafficRun.summary += result
			TrafficRun.output_file.write(result)

			Print.RESULT("finished %s:\n%s" % (tr.name, result))
			cycle += cycle + 1


	def __init__(self, name):
	
		if TrafficRun.output_file is None:
			TrafficRun.output_file = FileHandler.open_output_file(PERF_LIB_PATH + PERF_OUTPUT_NAME)
		self.name = name
		self.streams = []
		self.sleep = self.DEFAULT_SLEEP
		self.result = ""
		
	@classmethod
	def create(cls, name):
	
		cls.name = name
		
	def add_stream(self, stream):
		""" adds Stream to Stream list
			modifies TrafficRun sleeps if needed
		"""
	
		# checks whether Stream already exists
		if stream in self.streams:
			Print.ERROR("exact stream already exists in TrafficRun")
			raise RuntimeError
		else: # update time needed to wait for TrafficRun to finish
			self.streams.append(stream)
			iperf_time = stream.iperf_cmd.get_time()
			if self.sleep and iperf_time > self.sleep:
				self.sleep = iperf_time
				Print.DEBUG("sleep: %d" % (self.sleep))
		
	def apply_to_all_streams(self, function):
		""" apply the specified function to all Streams in Stream set """
		
		Print.DEBUG("applying %s to all Streams in Stream set" % (function.__name__))
		
		try:
			for stream in self.streams:
				function(stream)
		except NameError:
			Print.ERROR("invalid function: %s" % (function))
			raise
		
###	Stream modifications ###
		
	@classmethod
	def set_iperf_cmd_specifications(cls, stream):
	
		stream.set_iperf_cmd_specifications(cls.port)
		cls.port += 1
	
	def set_all_iperf_cmd_specifications(self):
	
		for stream in self.streams:
			self.set_iperf_cmd_specifications(stream)
		Print.INFO("all iperf commands were specified in order to run %s" % (self.name))

	# TODO: put in another function in traffic run
	# board_telnet.write_raw("echo \"%s\" >> %s" % (self.name, CPU_record_file_name))
	# board_telnet.write_raw("mpstat -I SUM -P ALL 20 1 >> %s &" % (CPU_record_file_name))
	
	def optimize_udp_perf_bandwidth(self):
		"""	assumes all iperf commands are UDP performance with the same time specified
			measures all total TP results when using bandwidth between MIN_BANDWIDTH and MAX_BANDWIDTH with BANDWIDTH_INTERVAL for TEST_INTERVAL seconds 
			then returns the bandwidth which resulted with the best TP """
	
		MAX_BANDWIDTH = 1000
		TEST_INTERVAL = 5
		BANDWIDTH_INTERVAL = 100
		MIN_BANDWIDTH = 100
		
		current_bandwidth = MIN_BANDWIDTH
		max_tp = 0.0
		max_tp_bandwidth = 0
		
		original_time = self.streams[0].iperf_cmd.get_time()
		self.sleep = TEST_INTERVAL

		for stream in self.streams:
			stream.iperf_cmd.set_time(TEST_INTERVAL)
		
		while current_bandwidth <= MAX_BANDWIDTH:
			
			# execute
			Print.INFO("trying bandwidth %i" % (current_bandwidth))

			for stream in self.streams:
				stream.iperf_cmd.set_bandwidth(current_bandwidth)

			self.run_requested_streams()
			
			tp_sum = 0
			
			# summarize total tp
			for stream in self.streams:
				
				try:
					results = stream.get_tp_from_summary()
				except:
					Print.DEBUG("coudl not get tp")
				else:
					tp_sum += results
					
			Print.DEBUG("tp_sum: %s" % (tp_sum))
				
			# update maximum tp and bandwidth
			if tp_sum > max_tp:
				max_tp = tp_sum
				max_tp_bandwidth = current_bandwidth

			current_bandwidth += BANDWIDTH_INTERVAL
			
		Print.INFO("bandwidth chosen: %i" % (max_tp_bandwidth))
		
		for stream in self.streams:
			stream.iperf_cmd.set_bandwidth(max_tp_bandwidth)
			stream.iperf_cmd.set_time(original_time)

		self.sleep = original_time
	
	def prepare_streams(self):
		""" verify all streams pass and modifies them if needed
			returns whether TrafficRun is ready to be executed """
		
		quick_check_fail = False
		
		Endpoint.prepare_all_endpoints()
		self.set_all_iperf_cmd_specifications()
		
		# verify iperf passes
		for stream in self.streams:
			try:
				stream.quick_check()
			except:
				quick_check_fail = True
				self.result += stream.result
				
		# if at least one Stream cannot pass, TrafficRun will not be executed
		if quick_check_fail:
			Print.INFO("setup is not ready in order to execute %s" % (self.name))
			return False
			
		# special adjustments needed for performance UDP traffic
		# changes bandwidth if at least one udp performance Stream exists
		for stream in self.streams:
			if stream.iperf_cmd.type == 'performance' and stream.iperf_cmd.get_protocol() == 'UDP':
				self.optimize_udp_perf_bandwidth()
				break

		return True
	
	def run_requested_streams(self):

		Print.INFO("running iperf commands")
		Endpoint.clear_all_iperfs()
		self.apply_to_all_streams(Stream.run_server)
		self.apply_to_all_streams(Stream.run_client)
		Stream.countdown(self.sleep)
			
	def gather_results(self):
		""" gathers each stream's results and returns whether any stream failed """
	
		Print.INFO("gathering results")
		run_fail = False
	
		for stream in self.streams:
			# TODO: create a get_results() in stream

			try:
				stream.get_summary_line()
			except: # data did not reach server
				Print.ERROR("something is wrong. although quick-check passed, this iperf_cmd did not:\n%s" % (stream.iperf_cmd))
				run_fail = True

			self.result += stream.result + '\n'
			# TODO: retrieve CPU recording file content
			
		return not run_fail

	def clear_logs(self):

		Print.INFO("clearing log files")

		for stream in self.streams:
			stream.clear_logs()

	def execute(self):

		Print.INFO("executing %s" % (self.name))

		if self.prepare_streams():
			self.run_requested_streams()
			self.gather_results()
			self.clear_logs()

		result = str("\n" + self.name + "\n" + self.result)
		TrafficRun.summary += result
		TrafficRun.output_file.write(result)

		Print.RESULT("finished %s:\n%s" % (self.name, result))

# used for parsing arguments from command line
if __name__ == "__main__":

	if len(sys.argv) > 1:

		if len(sys.argv) == 2:
			TrafficRun.parse_from_file(sys.argv[1])
		else:
			TrafficRun.single_stream(sys.argv[1:])

		TrafficRun.output_file.close()
		Print.RESULT(TrafficRun.summary)
	else:
		Print.ERROR("invalid number of arguments")
		
"""	
 example usage:

s = TrafficRun("test1", True)
STA5_16 = Endpoint.create("814VM16")
STA5_61 = Endpoint.create("10.124.123.61")
DUT_19 = Endpoint.create("814vm19")

s.add_stream(Stream.create(STA5_16, STA5_61, IperfCommand("sanity", "tcp")))
s.add_stream(Stream.create("814vm18", DUT_19, IperfCommand("sanity", "tcp")))
s.add_stream(Stream.create(STA5_61, STA5_16, IperfCommand("sanity", "UDP")))
s.add_stream(Stream.create(DUT_19, STA5_16, IperfCommand("stability", "UDP")))
s.execute()
"""
