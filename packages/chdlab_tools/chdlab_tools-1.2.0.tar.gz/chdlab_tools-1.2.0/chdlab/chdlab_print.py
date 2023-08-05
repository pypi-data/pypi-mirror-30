import re

""" creates a colorful and unified output to user
	DEBUG logs can be switched on/off by setting debug_log_enabled to True/False
"""

debug_log_enabled = True

def clear_whitespace(string):
	""" minimizes whitespaces in string """
	string = re.sub(r'\n$','', string)
	string = re.sub(r' +$', '', string)
	return string
			
def print_color(string, color):
	""" prints output colorfuly """
	string = clear_whitespace(string)
	colors = {'red':'31', 'yellow':'33', 'blue':'34', 'magenta':'35', 'turquoise':'36', 'white':'37'}
	attr = []
	attr.append(colors[color])
	attr.append('1')
	print '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

class Print:
	
	@staticmethod
	def ERROR(string):
		"""	guidelines:
			syscalls errors
			input syntax errors
		"""
		print_color('ERROR:\t%s' % (string), 'red')
	#	output_error_file.write(str("\n" + tr.name + "\n" + tr.result))

	@staticmethod
	def ASSERT(string):
		"""	guidelines:
			connectivity issues
			permission issues
		"""
		print_color('ASSERT:\t%s' % (string), 'yellow')

	@staticmethod
	def DEBUG(string):
		"""	add these according to your needs """
		if debug_log_enabled:
			print_color('DEBUG:\t%s' % (string), 'blue')
		
	@staticmethod
	def INFO(string):
		""" guidelines:
			i/o files
			iperf results analysis
			configuration changes
		"""
		print(string)
		
	@staticmethod
	def RESULT(string):
		""" results of a test that finished successfuly """
		print_color('RESULT:\t%s' % (string), 'turquoise')
