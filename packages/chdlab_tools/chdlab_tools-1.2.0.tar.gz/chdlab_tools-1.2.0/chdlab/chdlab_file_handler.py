import glob
from chdlab_print import Print

class FileHandler:

	@staticmethod
	def open_input_file(file_name):
		""" tries opening a file to be used as input """

		try:
			input_file = open(file_name, 'r')
		except Exception as e:
			Print.ERROR("Could not open %s: %s" % (file_name, e))
			raise e
				
		Print.DEBUG("Opened file '%s' successfuly" % (file_name))
		return input_file
		
	@staticmethod
	def __prompt_if_file_exists(file_name):
		""" notifies user if file exists, lets him decide whether to continue """
			
		if glob.glob(file_name):
		
			Print.INFO("File '%s' exists, and will be overwriten" % (file_name))
			user_input = "no input"
			
			while user_input.upper() not in {"Y", "N"}:
				user_input = raw_input("Continue? enter (Y/N)")
				
			if user_input == "N":
				raise RuntimeError
			
	@staticmethod
	def open_output_file(file_name, prompt=False):
		""" tries opening a file to be used as output """

		if prompt:
			FileHandler.__prompt_if_file_exists(file_name)
			
		try:
			output_file = open(file_name, 'w+')
		except OSError: # file exists
			output_file = io.FileIO(file_name, 'w') # overrides existing file
		except Exception as e:
			Print.ERROR("Could not open %s: %s" % (file_name, e))
			raise e
				
		Print.DEBUG("Opened file '%s' successfuly" % (file_name))
		return output_file
