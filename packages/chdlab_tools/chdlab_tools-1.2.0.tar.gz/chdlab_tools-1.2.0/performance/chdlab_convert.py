import sys
# guidelines:
#	sys.exit(0) - successful termination
#	sys.exit(1) - all kinds of errors
#	sys.exit(2) - command line syntax errors
import re
import io
import os
import pandas							
from pandas.io.excel import ExcelWriter # writing to and modifying excel
import argparse							# parsing arguments
import glob								# finding filename patterns

from prints import Prints

# macthers
matcher_iperf = re.compile(r'^\[ +[0-9]')
matcher_second = re.compile(r'.* +(?P<second>[0-9]+.[0-9]+)\-')
matcher_tp = re.compile(r'.* +(?P<tp>[0-9,.]+) +(?P<tp_unit>[M,K])bits/sec .*') 
matcher_tp_zero = re.compile(r'.* +(?P<tp_zero>0).00 +bits/sec .*') # TODO: find a way to match "0.00 bits/sec" in one matcher? or just use "0.00 bits/sec" in line

# final output to user
def print_results(error_list, cycles, drops):
	colorama.init(autoreset=True)

	print("\n")
	print("############################")
	print("iperf log conversion results")
	print("############################\n")

	# TODO: gather average/max/min of entire iperf test
	if cycles > 1:
		print("%i cycles were run" % cycles)
	elif cycles == 1:
		print("one cycle was run")
		
	if drops:
		print("there were %i drops to zero in TP" % drops)
		
	print('')
	for i in range(len(error_list)):
		Prints.ERROR("line %i: \"%s\": %s" % (error_list[i][0], error_list[i][1], error_list[i][2]))
			
	print('')
	colorama.init(autoreset=True)
	input('press ENTER to open the results file')

##################
# file handeling #
##################
def open_input_file(file_name):

	try:
		input_file = open(file_name, 'r+')
	except FileNotFoundError:
		#Prints.ERROR("file \'%s\' not found" % (file_name))
		print("file \'%s\' not found" % (file_name))
		sys.exit(2)
	except IOError:
		#Prints.ERROR("IOError with \'%s\'" % (file_name))
		print("IOError with \'%s\'" % (file_name))
		sys.exit(2)
		
	#Prints.DEBUG("opened file '%s' successfuly" % (file_name))
	print("opened file '%s' successfuly" % (file_name))
	return input_file
	
def open_output_file(file_name):
	
	accepted_input = {"Y", "N", "y", "n"}
	exit_input = {"N", "n"}
	
	if glob.glob(file_name):
		Prints.INFO("file '%s' exists, and will be overwriten" % (file_name))
		user_input = input("continue? enter (Y/N)")
		while user_input  not in accepted_input:
			user_input = input("continue? enter (Y/N)")
		if user_input in exit_input:
			sys.exit(2)
	
	try:
		output_file = open(file_name, 'r+')
	except FileNotFoundError:
		output_file = io.FileIO(file_name, 'w')
		output_file = open(file_name, 'r+')
	except IOError:
		#Prints.ERROR("IOError with \'%s\'" % (input_file_name))
		print("IOError with \'%s\'" % (input_file_name))
		sys.exit(2)
		
	#Prints.DEBUG("opened file '%s' successfuly" % (file_name))
	print("opened file '%s' successfuly" % (file_name))
	return output_file

##################
# main functions #
##################

# TODO: split this to smaller functions
def convert_iperf_to_csv(input_file, output_file, error_list, column):

	input_line_number = 0
	output_line_number = 0
	# TODO: add instruction to user to add iperf command in input log? and then set interval_dif difference by that (not 1 by default)
	interval_dif = 1.0
	iterations = 0
	prev_second = 0
	prev_tp = 0
	drops = 0
	cycles = 0

	for input_line in input_file:
		# if it's an iperf interval / summary line
		if matcher_iperf.search(input_line):
		
			# if it's not an iperf summary line
			if ("sender" not in input_line) and ("receiver" not in input_line): 
				
				second = matcher_second.search(input_line)
				if second: # if it's an iperf interval
						
					second_o = second.group('second')
					tp = matcher_tp.search(input_line)
					
					if (tp or ' 0.00 ' in input_line):
						if tp:
							tp_unit_o = tp.group('tp_unit')
							tp_o = float(tp.group('tp'))
							if tp_unit_o == 'K':
								tp_o = tp_o / 1024
						else:
							tp_o = 0.0
							if (prev_tp != 0.0):
								drops += 1
								#Prints.INFO('line %i: drop #%i seen in log' % (input_line_number, drops))
								print('line %i: drop #%i seen in log' % (input_line_number, drops))
						
						if prev_second + interval_dif != float(second_o):
							if float(second_o) == 0.0:
								cycles += 1
								Prints.INFO('line %i: start of cycle #%i' % (input_line_number, cycles))
							else:
								text = re.sub(r'[\n]','', input_line)
								#error_list.append((input_line_number, text, "not continuous iperf intervals"))
								#Prints.ERROR("file %s: line %i: '%s': not continuous iperf intervals" % (input_file.name, input_line_number, text))
								print("file %s: line %i: '%s': not continuous iperf intervals" % (input_file.name, input_line_number, text))
						
						prev_second = float(second_o)
						prev_tp = tp_o

						output_line = output_file.readline()
						if output_line:
							if output_line_number < len(output_line):
								output_line = output_line[output_line_number].replace(output_line, output_line + ("%s, %s\n" % (second_o, tp_o)))
							else:
								#Prints.ERROR("file %s: line %i: out of lines range" % (input_file.name, input_line_number))
								print("file %s: line %i: out of lines range" % (input_file.name, input_line_number))
								#Prints.DEBUG("output_line: %s" % (output_line))
						else: # write to file
							output_file.write("%s, %s\n" % (second_o, tp_o))
						output_line_number += 1
						
						# write to file
						#if second and (tp or ' 0.00 ' in line):
						#output_file.write("%s, %s\n" % (second_o, tp_o))
						
						iterations += 1
					
		input_line_number += 1
					
	#Prints.INFO('input_line %i: end of last cycle' % (input_line_number))
	print('input_line %i: end of last cycle' % (input_line_number))
	
	# input_file_date = re.split('_| |-|%',input_file_name)
	# TODO: maybe use matcher to detect actual date format?
	
	return iterations

# parse and validate arguments from user
def parse_arguments(argv):

	# guidelines (not all implemented)
	# input_file_path is mandatory
	# no output_file_path => input + .xlsx
	# '*' in input_file_path => convert_iperf_to_csv all files with the pattern, put each file in seperate sheet
	# --date == true => file(s) must be date formatted, each sheet seperated according to day, each day with all day chart + breakpoints below
	# --verbose == true => set debug_log as 1 and add Prints.DEBUG() prints in useful places
	
	parser = argparse.ArgumentParser()
	parser.add_argument("input_file_path", help="path of input file. '*' are accepted for convert_iperf_to_csving multiple files.", type=str)		 
	parser.add_argument('-o', "--output_file_path", help="specify output file path and name of excel, '.xlsx' suffix will be added.", nargs=1, type=str)	
	parser.add_argument('-d','--date', help="convert_iperf_to_csvs the input files assuming their names are date formatted.", action='store_true')				 
	parser.add_argument('-v','--verbose', help="increase output verbosity. Print Prints.DEBUG logs.", action='store_true')					 
	args = parser.parse_args()
	
	input_file_path = args.input_file_path
	
	asterisk = input_file_path.count('*')
	if asterisk != 0: 
		#Prints.INFO("all files that fit the pattern %s will be convert_iperf_to_csved, there will be a different sheet for each file" % (input_file_path))
		print("all files that fit the pattern %s will be convert_iperf_to_csved, there will be a different sheet for each file" % (input_file_path))
		
	# no output file path specified
	if args.output_file_path == None:
		# set output file path the same as the input and remove suffix
		output_file_path = os.path.splitext(args.input_file_path)[0]
		if asterisk != 0:
			output_file_path = output_file_path.replace('*', '')
	else:
		output_file_path = args.output_file_path
	
	# csv is the medium database
	# TODO: maybe change this, and use csv only for excel
	output_file_path = output_file_path + ".csv"
	#Prints.INFO("output file path is set to '%s'" % (output_file_path))
	print("output file path is set to '%s'" % (output_file_path))
		
	if args.date:
		#Prints.INFO("each file will be in a different sheet according to the start date formatted in file name")
		print("each file will be in a different sheet according to the start date formatted in file name")
		
	# find input file(s) specified by user
	filenames_list = glob.glob(input_file_path)
	num_of_files = len(filenames_list)
	if num_of_files < 1:
		#Prints.ERROR("input file path '%s' was not found" % (input_file_path))
		print("input file path '%s' was not found" % (input_file_path))
		sys.exit(2)
		
	output_file = open_output_file(output_file_path)
	
	#Prints.INFO("Number of files that will be converted: %i" % (num_of_files))
	print("Number of files that will be converted: %i" % (num_of_files))

	# date and input_file_path are in args
	return {'args': args, 'output_file_path': output_file_path, 'output_file': output_file, 'filenames_list': filenames_list, 'num_of_files': num_of_files}

def main(argv):

	i = 1
	iterations = 0
	
	drops = 0
	cycles = 0
	
	error_list = []
	
	filenames_list = 0
	input_file_path = -1
	output_file_path = -1
	output_file = -1
	
	dict = parse_arguments(argv)
	filenames_list = dict['filenames_list']
	output_file_path = dict['output_file_path']
	output_file = dict['output_file']
	num_of_files = dict['num_of_files']
	
	# TODO: add remove-file function adn fix related bugs
	for file_name in filenames_list:
		if(file_name == output_file_path):
			#Prints.ERROR("will not convert_iperf_to_csv file '%s' since it is supose to be the output file" % (file_name))
			print("will not convert_iperf_to_csv file '%s' since it is supose to be the output file" % (file_name))
			filenames_list.remove(file_name)
		else:
			iterations += convert_iperf_to_csv(open_input_file(file_name), output_file, error_list, 1)
		
	output_file.close()
	#Prints.INFO('all results were written to \'%s\'' % (output_file_path))
	print('all results were written to \'%s\'' % (output_file_path))
		
	# replace to .xlsx format for graphs and stuff
	base = os.path.splitext(output_file_path)[0]
	new_output_file_path = base + ".xlsx"
	
	# remove any .xlsx file with the sepcified name if exists
	try:
		os.remove(new_output_file_path)
	except OSError:
		pass
	
	# TODO: add function for this
	# convert_iperf_to_csv .csv output file to .xlsx output file with chart
	writer = pandas.ExcelWriter(new_output_file_path, engine='xlsxwriter')
	#Prints.DEBUG("base \"%s\"" % (base))
	pandas.read_csv(output_file_path).to_excel(writer, sheet_name=base)
	workbook  = writer.book
	worksheet = writer.sheets[base]
	chart = workbook.add_chart({'type': 'line'})									# chart type
	
	# TODO: update column B (at output_file.write) to set actual seconds (otherwise will override previous cycles)
	#chart.add_series({'values': '=' + base + '!$C$2:$C$' + str(iterations+1),		# set Y axis
	#				  'line': {'width': 1.00},										# line thickness
	#				  'categories': '=' + base + '!$B$2:$B$' + str(iterations+1)})	# set X axis
	
	chart.add_series({'values': '=' + base + '!$C$2:$C$' + str(iterations+1),		# set Y axis
					  'line': {'width': 1.00}})										# set X axis
					  
	chart.set_size({'width': 1800, 'height': 850})
	# TODO: add day according to inupt file
	chart.set_title({'name': base})
	worksheet.insert_chart('A1', chart)
	writer.save()
	writer.close()
	
	# remove .csv output file
	try:
		os.remove(output_file_path)
	except OSError:
		pass
	
	#Prints.INFO('output file name changed to \'%s\'' % (new_output_file_path))
	print('output file name changed to \'%s\'' % (new_output_file_path))

	print_results(error_list, cycles, drops)
	
	# only supported in Windows
	os.startfile(new_output_file_path)

if __name__ == "__main__": 
	main(sys.argv[1:])