import os
import re
import sys
import subprocess

from chdlab_print import Print

class Endpoint:
	"""	Endpoint instance represents a Linux VM machine in the lab
		class controls multiple Endpoints
	
		class variables:
			endpoints (Endpoint set):		set of Endpoints

		instance attributes:
			management_ip (str - ID):		ip address that is part of the management network
												management_ip is used as the object identifier
			setup_interface (str, None):		interface in vm machine that is connecetd to the setup
			setup_ip_address (str, None):	ip address that is part of the test setup (if exists)
	"""
	
	endpoints = []

	def __init__(self, management_ip):
		""" sets Endpoint identifier """

		self.management_ip = management_ip
		self.dummy = 1
		
	def __eq__(self, other): 
		""" compares Endpoints' management_ip
			meaning defining management_ip them as Endpoint identifier
		"""
		
		if isinstance(other, Endpoint):
			return self.management_ip == other.management_ip
			
		return False

	def __str__(self):
	
		return 'Endpoint instance\n' + '\n'.join("%s: %s" % item for item in vars(self).items())
		
###	input validation ###

	@staticmethod
	def get_vm_address(name):
		""" returns management_ip of vm name if is valid, if not valid, return False """
		
		matcher_vm_name = re.compile(r'(?P<nic_number>[0-9]+)vm(?P<vm_number>[0-9]+)')
		MIN_NIC_NUMBER = 814
		MAX_NIC_NUMBER = 816
		MIN_VM_NUMBER = 1
		MAX_VM_NUMBER = 28

		vm_name = matcher_vm_name.search(name.lower())
		if vm_name is None:
			Print.DEBUG("%s is not a valid vm name" % (name))
			return False
			
		nic_number = int(vm_name.group('nic_number'))
		vm_number = int(vm_name.group('vm_number'))
		
		if nic_number < MIN_NIC_NUMBER or nic_number > MAX_NIC_NUMBER or vm_number < MIN_VM_NUMBER or vm_number > MAX_VM_NUMBER:
			Print.DEBUG("%s is a non existing vm" % (vm_name))
			return False
		
		management_ip = "10.124.123." + str((nic_number - MIN_NIC_NUMBER) * MAX_VM_NUMBER + vm_number)
		
		Print.DEBUG("%s's management_ip is %s" % (name, management_ip))
		
		return management_ip
		
	@staticmethod
	def valid_management_ip(address):

		if "10.124.122." not in address and "10.124.123." not in address:
			Print.DEBUG("address %s is not a lab management ip address" % (address))
			return False
			
		return True
	
	@classmethod
	def create(cls, input):
		"""	accepts Endpoint object, string of management_ip, string of vm name
			returns instance of an Endpoint and adds it to the endpoints set if needed
		"""
		instance = None
		
		if not isinstance(input, Endpoint) and not isinstance(input, str):
			Print.ERROR("%s is not a valid Endpoint.create input" % (input))
			raise ValueError('Endpoint')
		
		if isinstance(input, Endpoint): # input is Endpoint - will not create duplicates
			instance = input	
		else:							# input is string
			management_ip = cls.get_vm_address(input)
			if management_ip:				# input is string of vm name
				instance = cls(str(management_ip))
			elif cls.valid_management_ip(input):		# input is string of vm address
				instance = cls(input)
			else:						# invalid input
				Print.ERROR("invalid Endpoint create input: %s" % (input))
				raise ValueError('Endpoint')
				
		# adds instance only if it does not exist in the endpoints set
		try:
			instance = cls.endpoints[cls.endpoints.index(instance)]
		except ValueError as e:
			Print.DEBUG("instance does not exist in endpoints set")
			cls.endpoints.append(instance)
		else:
			Print.DEBUG("instance already exists in endpoints set")
		
		return instance

###	Endpoints set operations ###

	def clear_unused_endpoint(self):
		""" remove Endpoint that is not referenced anywhere but at the Endpoints set """
		
		# TODO: why is it 5?
		MIN_REF_NUM = 5
	
		if sys.getrefcount(self) == MIN_REF_NUM:
			self.endpoints.remove(self)
			Print.DEBUG("removing: %s\nbecause it is not used" % (str(self)))

	@classmethod
	def apply_to_all_endpoints(cls, function):
		""" apply the specified function to all Endpoints in Endpoints set """
		
		Print.DEBUG("applying %s to all Endpoints in Endpoint set" % (function.__name__))
		
		try:
			for endpoint in cls.endpoints:
				function(endpoint)
		except NameError:
			Print.ERROR("invalid function: %s" % (function))
			raise
			
	@classmethod		
	def prepare_all_endpoints(cls):
	
		cls.apply_to_all_endpoints(cls.prepare_endpoint)
		Print.INFO("finished preparing all Endpoints")
		
	@classmethod
	def clear_all_unused_endpoints(cls):
		""" removes all Endpoints that are not referenced anywhere but at the Endpoints set """
		
		cls.apply_to_all_endpoints(cls.clear_unused_endpoint)
		Print.INFO("finished clearing all unused Endpoints")
		
	@classmethod
	def str_all_endpoints(cls):
		""" returns a string of all Endpoints in Endpoint set """
	
		output = ""
	
		for endpoint in cls.endpoints:
			output += str(endpoint) + '\n'
			
		return output
		
###	setup related functions ###
	
	def send_command(self, command):
		""" tries sending command to vm using sshpass """
	
		Print.DEBUG("management_ip: %s command: %s" % (self.management_ip, command))
		full_command = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} \"{}\"".format('libit', 'libit', self.management_ip, command)

		try:
			pipe = subprocess.Popen(full_command, stdout=subprocess.PIPE, shell=True)
			ssh_stdout, ssh_error = pipe.communicate()
			#ssh_stdout, ssh_error = pipe.communic_numberate()
		except subprocess.CalledProcessError as e:
			raise RuntimeError("command '{}' return with error (code {}): \"{}\"".format(e.cmd, e.returncode, e.output))
		except:
			Print.ERROR("unexpected error: %s" % (sys.exc_info()[0]))
			raise
			
		if ssh_stdout:
			Print.DEBUG("ssh_stdout:\n%s" % (ssh_stdout))
		if ssh_error:
			Print.ERROR("ssh_error:\n%s" % (ssh_error))
			
		return ssh_stdout

	def get_setup_details(self):
		""" gets setup_interface and setup_ip_address
			returns the setup_ip_address in case it exists
			only supports eth (because of sole support to VMs in lab)
			it is the user's responsibility to set the IP addresses in the setup
			exits in any other case
		"""
	
		matcher_eth_interface = re.compile(r'.*(?P<eth_interface>eth[1-9]).*')
		matcher_eth_interface_address = re.compile(r'.*(?P<eth_interface>eth[1-9]).*\n.*addr:(?P<eth_addr>[0-9,\.]+).*')
		
		ifconfig_result = self.send_command("ifconfig")

		if not ifconfig_result:
			Print.ERROR("no ifconfig result")
			raise RuntimeError
		else: # ifconfig returned result
			eth_interface = matcher_eth_interface.search(ifconfig_result)
			if not eth_interface:
				Print.ERROR("no eth interface in ifconfig")
				raise RuntimeError
			else: # eth interface exists
				self.setup_interface = str(eth_interface.group('eth_interface'))
				Print.DEBUG("setup interface detected: %s" % (self.setup_interface))
				eth_address = matcher_eth_interface_address.search(ifconfig_result)
				if not eth_address:
					Print.ERROR("no IP address assigned to %s interface. it is the user's responsibility to set the IP addresses in the setup" % (self.setup_interface))
					raise RuntimeError
				else: # address assigned to eth interface
					eth_addr = str(eth_address.group('eth_addr'))
					self.setup_ip_address = eth_addr
					Print.DEBUG("%s assigned address: %s" % (self.setup_interface, self.setup_ip_address))
					
		return self.setup_ip_address
		
	def check_iperfs_running(self):
		""" checks whether iperfs are running in this Endpoint
			returns pid(s) if they exist """
		
		return self.send_command("pidof iperf") + self.send_command("pidof iperf3")
		
	def clear_iperfs(self):
		""" kills all running iperfs at Endpoint """
	
		iperfs_pids = self.check_iperfs_running()
		
		if iperfs_pids:
			self.send_command("echo libit | sudo -S kill -9 " + iperfs_pids)
			
			if self.check_iperfs_running():
				Print.ERROR("kill failed. something keeps iperfs running.")
				raise RuntimeError("kill failed. something keeps iperfs running.")
			
		Print.INFO("%s is cleared of running iperfs" % (self.management_ip))
		
	def prepare_endpoint(self):
		""" all prerequisites needed for running an iperf
			Endpoint should be ready
		"""
	
		self.get_setup_details()
		self.clear_iperfs()
		
	def is_ready(self):
		""" checks all prerequisites for running an iperf """
	
		return self.setup_ip_address != None and check_iperfs_running() == None
		
	@classmethod
	def clear_all_iperfs(cls):
		""" clears all running iperfs in all endpoints """
	
		cls.apply_to_all_endpoints(cls.clear_iperfs)
		
### debugging setup connectivity issues ###

	def check_ping_pass_to(self, other_endpoint):
		""" returns whether the ping passed from self to other_endpoint """
		
		ping_result = self.send_command("ping -c1 " + other_endpoint.setup_ip_address)
		Print.DEBUG("ping_result: %s" % (ping_result))
		
		if "0 received" in ping_result:
			result = "ping from %s to %s did not pass" % (self.setup_ip_address, other_endpoint.setup_ip_address)
			Print.ERROR(result)
			return result
		
		Print.INFO("ping passed from %s to %s" % (self.setup_ip_address, other_endpoint.setup_ip_address))
		return ""
	
	def check_route_to(self, other_endpoint):
		""" returns whether a route from self to other_endpoint exists
			assumes all setup networks have a netmask of 255.255.255.0
		"""
	
		# set expected results
		expected_destination = re.sub(r'.[0-9]+$', '.', other_endpoint.setup_ip_address)
		matcher_route = re.compile(r'%s[0-9,\/]+ (?P<through>\w+).*'%expected_destination)

		# get results
		route_result = self.send_command("ip route")
		Print.DEBUG("ip_route_result: %s" % (route_result))
	
		# parse results
		matcher_result = matcher_route.search(route_result)
		if matcher_result:
			through_result = str(matcher_result.group('through'))
		else:
			Print.DEBUG("no matcher_results")
		
		# verify results
		if matcher_result and ('dev' or 'via' is through_result):
			Print.INFO("route to destination %s - exists" % (other_endpoint.setup_ip_address))
			return ""
		
		result = "no route to destination %s" % (other_endpoint.setup_ip_address)
		Print.ERROR(result)
		return result

	def check_link_exists(self):
		""" returns whether there's a link in self's setup_interface """
	
		matcher_link = re.compile(r'.*Link detected: (?P<link>\w+).*')
	
		ethtool_result = self.send_command("echo libit | sudo -S ethtool " + self.setup_interface)
		
		link = matcher_link.search(ethtool_result)
		if link == None:
			Print.ERROR("could not retrieve link state of %s in %s" % (self.setup_interface, self.management_ip))
			raise RuntimeError
		
		if str((matcher_link.search(ethtool_result)).group('link')) is 'No':
			result = "no link at %s" % (self.setup_interface)
			Print.ERROR(result)
			return result
			
		Print.INFO("link at %s exists" % (self.setup_interface))
		return ""
		
""" test Endpoint class is working:
	# TODO: later implement with pytest

ep1 = Endpoint.create("10.124.123.21")
ep2 = Endpoint.create("814vm21")
ep3 = Endpoint.create("814vm19")
Print.INFO(Endpoint.str_all_endpoints()) # there should be only 2 Endpoints
Print.INFO("id(ep1): %s, id(ep2): %s" % (id(ep1), id(ep2))) # id's should be identical, no duplicates
ep1.prepare_endpoint()
Print.INFO(ep1) # setup_interface and setup_ip_address should be updated (assuming they exist)
Print.INFO(ep2) # results should be the same
ep1.send_command("ps -a") # results should be shown in debug logs
Print.INFO(Endpoint.str_all_endpoints()) # ep1's setup_interface and setup_ip_address should be updated, no duplicates
Endpoint.clear_all_unused_endpoints() # no Endpoints should be removed
del(ep1)
Endpoint.clear_all_unused_endpoints() # no Endpoints should be removed
del(ep3)
Endpoint.clear_all_unused_endpoints() # ep3 should be removed
Print.INFO(Endpoint.str_all_endpoints()) # there should be only 1 Endpoint (ep1)
"""
