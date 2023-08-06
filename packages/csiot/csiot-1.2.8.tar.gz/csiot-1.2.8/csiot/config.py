import sys
import os

def find_config():
	if os.path.exists("%s/.csiot.conf" % os.environ["HOME"]):
		return "%s/.csiot.conf" % os.environ["HOME"]
	if os.path.exists("/etc/csiot.conf"):
		return "/etc/csiot.conf"

class Config(dict):
	def __init__(self):
		super().__init__()

		self.path = find_config()
		if not self.path:
			raise IOError("unable to find configuration file")

		self.parse()

	def parse(self):
		data = []
		with open(self.path) as f:
			data = f.readlines()
		for line in data:
			line = line.rstrip().strip()
			pos = line.find('#')
			if pos:
				data = line[:pos - 1]
			pos = line.find('=')
			if not pos:
				continue

			self.__setitem__(line[:pos - 1], line[pos + 2:])




