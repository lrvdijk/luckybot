"""
:mod:`luckybot.bot` - Main controller class
-------------------------------------------

This is our main bot controller, manages plugins, servers and more

.. module:: luckybot.bot
   :synopsis: Main controller class

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from ConfigParser import SafeConfigParser
from luckybot import base_path, user_path
from luckybot.connections.multiprocess import MultiProcessConnection

class LuckyBot(object):
	"""
		Main application controller
	"""

	def __init__(self):
		"""
			Constructor, initializes some basic bot functionality
		"""

		# Load settings
		self.settings = SafeConfigParser()
		if os.path.exists(path.get_personal_file('settings.ini')):
			self.settings.read(user_path('settings.ini'))
		else:
			self.settings.read(base_path('data', 'settings.ini'))

	def get_servers(self):
		"""
			Reads the configuration file, and checks which servers
			to connect to
		"""

		servers = []
		sections = self.settings.sections()
		regexp = re.compile(r'^Server(\d+)$', re.I)

		for section in sections:
			match = regexp.match(section)
			if match:
				config = {}
				for option in self.settings.options(section):
					config[option] = self.settings.get(section, option)
				servers.append(config)

		return servers

	def start(self):
		"""
			Creates for each server a subprocess, and runs the bot
		"""

bot = LuckyBot()
