#!/usr/bin/env python

import argparse
from urlparse import urlparse
import os
import logging

class CHDLAB_buildbot(object):
	def __parse__(self):
		self.parsed_url = urlparse(self.url)
		if self.parsed_url.scheme == "http":
			list = filter(None, self.parsed_url.path.split('/'))
			if list[0] != 'buildbot':
				raise Exception("invalid buildbot url[=%s]" %(self.url))
			try:
				self.branch, self.tag, self.model = list[1], list[2], list[3]
			except IndexError:
				raise Exception("Invalid buildbot url[=%s]" %(self.url))
			self.base_url = "{}://{}/buildbot".format(self.parsed_url.scheme, self.parsed_url.netloc)

		elif self.parsed_url.scheme == "file":
			list = filter(None, self.parsed_url.path.split('/'))
			self.tag, self.model = list[6], list[7]
		else:
			raise Exception("invalid scheme[=%s] for url[=%s]" %(self.parsed_url.scheme, self.url))

	def __str__(self):
		return "branch={}, tag={}, model={}, path={}".format(self.branch, self.tag, self.model.lower(), self.parsed_url.path)

	def __init__(self, url):
		self.branch = "beerocks_1.1"
		self.url = url
		self.logger = logging.getLogger('buildbot')
		self.cleanup_path = None
		self.__parse__()

	def download(self, path='./'):
		print "download start"
		if self.parsed_url.scheme == "http":
			_path = os.path.abspath("{}/{}".format(path, self.tag))
			url = "{}/{}/{}/{}/bin/lantiq/{}".format(self.base_url, self.branch, self.tag, self.model.upper(), self.model.lower())
			cmd = 'wget --no-proxy -P {path} -q -r --level=0 -np -nH --cut-dirs=6 --no-parent --reject="index.html" --accept="fullimage.img,gphy_firmware.img,u-boot-nand.bin,uImage_bootcore,manifest_*" "{url}/"'.format(path=_path, url=url)
			self.logger.debug(cmd)
			os.system(cmd)
			self.cleanup_path = "{}/{}".format(_path, self.model).split(self.buildbot.model, 1)[0]
			return _path+'/'+self.model
		else:
			# no need to download, just return the path
			return self.parsed_url.path

	def cleanup(self):
		if self.cleanup_path:
			self.logger.info("delete downloaded data {}".format(self.cleanup_path))
			os.system("rm -rf {}".format(self.cleanup_path))
			self.cleanup_path = None

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='chdlab buildbot')
	parser.add_argument("url", help="buildbot url")
	args = parser.parse_args()
	
	print CHDLAB_buildbot(args.url).download()
