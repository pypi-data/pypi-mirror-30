import sys
sys.path.insert(0, '..')
import os
import logging

from chdlab_jira import CHDLAB_jira
import datetime

MAX_BOARDS = 65
""" before updating this value, run reset_file() """

BOARDS_LAST_ASSIGNEE_FILE = "/local/sgaidi/chdlab/lab_management/chdlab_boards_assignee_list.txt"
WIFI_CLIENTS_LAST_ASSIGNEE_FILE = "/local/sgaidi/chdlab/lab_management/chdlab_wifi_clients_assignee_list.txt"
ALLOCATION_DAYS = 7

class JiraAllocation:
	"""	manages time allocation of assignee for each specified jira type in the LAB jira
		is called using crontab in sgaidi's enviornment (currently every dat at 10:00am)
		comment out the cron job if you are making any changes

		class variables:
			logger (logger object):			logger from CHDLAB_jira module
		
		instance attributes:
			jira_type (str):				name of child class of CHDLAB_jira
			assignee_file_name (str):		full path of file that holds all assignees since last time this module was called
			saved_value (list):				list of saved values in file
											index is the jira id, content is the assignee
"""

	logger = CHDLAB_jira.logger

	def __init__(self, jira_type):

		self.jira_type = jira_type
		
		if jira_type == "board":
			self.assignee_file_name = BOARDS_LAST_ASSIGNEE_FILE
		elif jira_type == "wifi client":
			self.assignee_file_name = WIFI_CLIENTS_LAST_ASSIGNEE_FILE
		else:
			self.logger.error("not supported child class of CHDLAB_jira: {}".format(type(jira_type).__name__))
			raise ValueError
		
		self.saved_values = [0]
		self.read_file()
		self.update_values()
		self.write_file()
		
		# in case file is messed up and there's no copy:
		#self.reset_file()

### time allocation operations ###
		
	def unassign(self, jira, id):

		self.logger.info("jira #%02d passed allocation time!" % (id))
		jira.issue.update(assignee=None)
		self.saved_values[id] = "Unassigned"

		current_comments = CHDLAB_jira.connection.comments(jira.issue)
		self.logger.debug("comments:\n%s" % (current_comments))

		for comment in current_comments:
			if CHDLAB_jira.CHDLAB_COMMENT in comment.body:
				comment.delete()

	def give_allocation_to(self, jira):
		""" gives specified jira more time allocation """

		new_allocation = unicode(datetime.datetime.now().date() + datetime.timedelta(days=ALLOCATION_DAYS))
		new_allocation = new_allocation + "T10:00:00.000+0200"
		self.logger.info("new jira allocation: {}".format(new_allocation))
		jira.issue.update(customfield_10342=new_allocation)
		
	@staticmethod
	def is_allocation_required(jira):
		""" sets the allocation restrictions rules for jira """
	
		not_required_setups = ["Demo", "UserTest", "Multi AP"]
		
		for setup in not_required_setups:
			if setup in jira.summary:
				return False
		
		return True
		
### file handeling ###

	def validate_line(self, line):

		if line == "":
			self.logger.critical("empty line")
			sys.exit(1)

		split = line.split(':')

		if len(split) != 2:
			self.logger.critical("invalid line")
			sys.exit(1)

		return split[0], split[1]

	def read_file(self):

		with open(self.assignee_file_name, 'r') as file:
		
			for i in range(1,MAX_BOARDS):

				self.logger.debug("checking jira #%02d" % (i))
				assignee = "None"

				line = file.readline()
				jira_id, assignee = self.validate_line(line)
				if jira_id is None or int(jira_id) != i:
					self.logger.error("invalid line: {}".format(line))
					sys.exit(1)

				self.saved_values.append(assignee[:-1]) # remove newline
				
	def write_file(self):

		with open(self.assignee_file_name, 'w+') as file:
		
			for i in range(1,MAX_BOARDS):
				file.write(str(i) + ":" + self.saved_values[i] + "\n")

	def reset_file(self):

		with open(self.assignee_file_name, 'w+') as file:
		
			for i in range(1,MAX_BOARDS):

				jira = self.get_jira(i)
				if jira is None:
					assignee = "None"
				else:
					assignee = jira.assignee

				file.write(str(i) + ":" + assignee + "\n")
				
### main operations ###
				
	def get_jira(self, id):
		""" tries retrieving the CHDLAB_jira object """

		self.logger.info("Trying to get %s #%02d" % (self.jira_type, id))

		jira = None

		try:
			jira = CHDLAB_jira.create(id, self.jira_type)
		except :
			self.logger.warning("No jira with id #{} was found!".format(id))
			if jira is not None:
				jira.assignee = "None"

		return jira

	def update_values(self):

		for i in range(1,MAX_BOARDS):

			jira = self.get_jira(i)

			if jira is not None and JiraAllocation.is_allocation_required(jira): # valid jira
			
				if jira.assignee != self.saved_values[i]: # assignee changed - update allocation and file
				
					self.logger.info("Assignee of jira #%02d (%s) was changed to %s" % (i, self.saved_values[i], jira.assignee))
					self.give_allocation_to(jira)
					self.saved_values[i] = jira.assignee
					
				elif jira.assignee != "Unassigned" and jira.assignee != "None":
					# assignee is valid and was not changes since previous run - check allocation
					end_of_allocation = datetime.datetime.strptime(jira.issue.fields.customfield_10342.split('.')[0], "%Y-%m-%dT%H:%M:%S")

					if datetime.datetime.now() >= end_of_allocation: # end of allocation
						self.unassign(jira, i)

					elif datetime.datetime.now() + datetime.timedelta(days=1) >= end_of_allocation: # notify tomorrow ends allocation
						CHDLAB_jira.leave_comment(jira, "This issue is scheduled to be unassigned tomorrow at 10:00am")
							
					elif datetime.datetime.now() + datetime.timedelta(days=ALLOCATION_DAYS) <= end_of_allocation:
						# user tried allocating more time than allowed - fix and notify
						CHDLAB_jira.leave_comment(jira, "You cannot allocate more than a week for each issue")
						self.give_allocation_to(jira)

if __name__ == "__main__":
	logging.config.fileConfig('./logging.conf')

	JiraAllocation("board")
	JiraAllocation("wifi client")
	JiraAllocation.logger.info("finished executing successfully")
