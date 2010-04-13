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
from luckybot.irc.protocol.server import Server

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

				server = Server(**config)
				servers.append(server)

		return servers

	def start(self):
		"""
			Creates for each server a subprocess, and runs the bot
		"""

		servers = self.get_servers()

		# Open connections
		for server in servers:
			server.connect()

		num_alive = len(servers)

		# Our main loop
		while True:
			try:
				# Loop through each server and check if there's any data
				for server in servers:
					data = server.connection.recv()

					if data:
						message = server.handler.protocol.parse_line(data)

						# pass it through our protocol handler
						server.handler.on_line(message)

						# TODO: Pass it through all plugins

					# Check which processes are alive and which are not
					if not server.connection.is_alive():
						if self.settings.getboolean('Bot', 'keep_alive'):
							server.connect()
						else:
							num_alive -= 1

				if num_alive == 0:
					break
			except KeyboardInterrupt:
				for server in servers:
					server.send("QUIT :LuckyBot - http://luckybot.return1.net")
					server.connection.close()

				break

bot = LuckyBot()
