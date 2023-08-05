#!/usr/bin/env python

import sys
sys.path.insert(0, './performance')
#from chdlab_traffic_run import TrafficRun
from chdlab_print import Print
from chdlab_jira import CHDLAB_jira
from chdlab_telnet import CHDLAB_telnet
import time
import random


CALTEST_EP_NUMBER = 0
CALTEST_SSID = 1
CALTEST_PASSWORD = 2

class WISP:
	"""	class WISP allows making configuration changes to WISP using caltest

		class variables:
			caltest (dictionary):	specifies caltest value (including default)

		instance attributes:
			telnet (CHDLAB_telnet):	allows execution of caltest commands and checking DUT's status
	"""

	caltest = {	"2.4G":	("1",
				"FAR_24",
				"12345678"),
			"5G":	("2",
				"FAR_5",
				"12345678")}
	"""	caltest values:
		<BACKHAUL> : (<ENDPOINT_NUMBER>,<SSID>,<PASSWORD>)
	"""

	def __init__(self, board_number):

		self.telnet = CHDLAB_telnet(board_number)
		self.telnet.state_change("linux")
		self.telnet.__prepare__()
	
### WISP configuration changes ###

	def write_cal(self, cmd):

		self.telnet.write_raw('echo -en \"%s\n\" >> /tmp/calwrite\n' % (cmd))

	def connect_wisp(self, backhaul="2.4G", ssid=None, password=None):

		Print.INFO("trying to connect on %s backhaul" % (backhaul))

		# specify caltest values
		caltest_backhaul = self.caltest[backhaul]

		backhaul = caltest_backhaul[CALTEST_EP_NUMBER]
		if ssid is None:
			ssid = caltest_backhaul[CALTEST_SSID]
		if password is None:
			password = caltest_backhaul[CALTEST_PASSWORD]

		Print.INFO("backhaul: %s, ssid: %s, password: %s" % (backhaul, ssid, password))

		# executecaltest command
		self.telnet.write_raw("rm /tmp/calwrite\n")
		
		self.write_cal("object:Device.X_INTEL_COM_WISP.EndPoint.%s: :MODIFY" % (backhaul))
		self.write_cal("param:Enable: :true")
		self.write_cal("object:Device.X_INTEL_COM_WISP.Profile.%s: :MODIFY" % (backhaul))
		self.write_cal("param:SSID: :%s" % (ssid))
		self.write_cal("object:Device.X_INTEL_COM_WISP.Profile.%s.Security: :MODIFY" % (backhaul))
		self.write_cal("param:KeyPassphrase: :%s" % (password))
		
		self.telnet.write_raw('caltest -s /tmp/calwrite -c WEB\n')

	def disconnect_wisp(self, backhaul="2.4G"):

		Print.INFO("trying to disconnect from %s backhaul" % (backhaul))

		caltest_backhaul = self.caltest[backhaul]

		Print.INFO("backhaul: %s" % (backhaul))

		self.telnet.write_raw("rm /tmp/calwrite\n")
		
		self.write_cal("object:Device.X_INTEL_COM_WISP.EndPoint.%s: :MODIFY" % (caltest_backhaul[0]))
		self.write_cal("param:Enable: :false")

		self.telnet.write_raw('caltest -s /tmp/calwrite -c WEB\n')

### checking DUT's status ###
	
	def check_wlan_mode(self, timeout=5):

		WLAN0_MODE = "802.11bgn"
		WLAN2_MODE = "802.11anac"

		result = "no result"

		Print.INFO("checking iwconfig")
		self.telnet.tn.read_very_eager()
		
		self.telnet.tn.write("iwconfig wlan2\n")
			
		try:
			result = self.telnet.tn.read_until(WLAN2_MODE, timeout)
		except:
			Print.ERROR(sys.exc_info()[0])
		finally:
			if WLAN2_MODE not in result:
				Print.ERROR("wlan2 is not in correct mode!")
				Print.DEBUG(result)
				raise

		self.telnet.tn.write("iwconfig wlan0\n")
	
		try:
			result = self.telnet.tn.read_until(WLAN0_MODE, timeout)
		except:
			Print.ERROR(sys.exc_info()[0])
		finally:
			if WLAN0_MODE not in result:
				Print.ERROR("wlan0 is not in correct mode!")
				Print.DEBUG(result)
				raise

		Print.INFO("wlan modes are OK")
		
	def check_wraper(self):

		time.sleep(20)
	
		for i in range(1,6):

			time.sleep(15)

			try:
				self.check_wlan_mode()
			except:
				Print.INFO("try #%d not successfull" % (i))
			else:
				return
	
		Print.ERROR("could not get valid wlan modes after 5 retries")	
		sys.exit(1)

	@staticmethod
	def run_test():

		wisp = WISP("49")

		while(1):

			if random.randint(0,1) == 1:
				backhaul = "2.4G"
			else:
				backhaul = "5G"

			wisp.connect_wisp(backhaul)
			wisp.check_wraper()
			wisp.disconnect_wisp(backhaul)
			wisp.check_wraper()

WISP.run_test()

