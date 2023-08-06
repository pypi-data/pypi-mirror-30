# -*- coding: utf-8 -*-
import configparser
import json

class Config(object):
	"""docstring for Config"""


	def __init__(self, path):
		self.cp = configparser.ConfigParser()
		self.cp.read(path)

	def get_link_inf(self):
		res = {}
		res['host'] = self.cp['LINK']['host']+':'+self.cp['LINK']['port']
		res['db'] = self.cp['LINK']['database']
		return res

	def get_fields_inf(self):
		res = {}

		for x in self.cp['FIELDS']:
			res[x] = json.loads(self.cp['FIELDS'][x])

		return res

	def get_time(self, time):
		return self.cp['LIMITS'][time]

if __name__ == '__main__':
	c = Config('./config/aptexp.conf')
	print(c.get_link_inf())
	print(c.get_fields_inf())

		