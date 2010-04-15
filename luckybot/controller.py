"""
:mod:`luckybot.bot` - Main controller class
===========================================

This is our main bot controller, manages plugins, servers and more

.. module:: luckybot.bot
   :synopsis: Main controller class

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from ConfigParser import SafeConfigParser
from luckybot import base_path, user_path, __version__
from luckybot.irc.protocol import Message
from luckybot.irc.protocol.server import Server
from luckybot.ui import UI
from luckybot.ui.console import ConsoleUI
from luckybot.plugin import PluginManager
from datetime import datetime
import optparse
import os
import re
import sys
from datetime import datetime
from sqlalchemy import create_engine

class LuckyBot(object):
	"""
		Main application controller
	"""

	bot = None

	def __init__(self):
		"""
			Constructor, initializes some basic bot functionality
		"""

		# setup option parser
		self.parser = optparse.OptionParser(usage="%prog [options]",
			version="LuckyBot v%s" % __version__)
		self.parser.add_option('-u', '--ui', dest="ui",
			help="GUI type: currently only console supported",
			default="console")

		options, args = self.parser.parse_args(sys.argv)
		self.ui = UI.get(options.ui)()
		self.start_time = None

		# Load settings
		self.settings = SafeConfigParser()
		if os.path.exists(user_path('settings.conf')):
			self.settings.read(user_path('settings.conf'))
		else:
			self.settings.read(base_path('data', 'settings.conf'))

		# Setup database
		self.db = create_engine(self.settings.get('Bot', 'database'))

	@classmethod
	def get_bot(cls):
		"""
			Get the bot object
		"""

		if cls.bot == None:
			cls.bot = LuckyBot()

		return cls.bot

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

				server = Server(self, **config)
				servers.append(server)

		return servers

	def start(self):
		"""
			Creates for each server a subprocess, and runs the bot
		"""

		self.start_time = datetime.now()

		# Load plugins
		self.plugins = PluginManager()
		self.plugins.load_plugins(base_path('plugins'))

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
						self.ui.data_in(data.strip())
						message = server.handler.protocol.parse_line(data)
						message.server = server

						# Check if bot command is called
						if (message.type == Message.USER_MESSAGE and
									message.command == 'PRIVMSG'):
							cmd_prefix = self.settings.get('Bot', 'command_prefix')

							# A message sent in PM/Channel
							if message.message[0:len(cmd_prefix)] == cmd_prefix:
								space_pos = message.message.find(' ', len(cmd_prefix))
								if space_pos == -1:
									space_pos = len(message.message)

								command = message.message[len(cmd_prefix):space_pos]
								message.bot_command = command
								message.bot_args = message.message[space_pos+1:]

						# pass it through our protocol handler
						server.handler.on_line(message)

						# Pass it through all plugins
						self.plugins.check_event(message)

					# Check which processes are alive and which are not
					if not server.connection.is_alive:
						if self.settings.getboolean('Bot', 'keep_alive'):
							# Check once in the three minutes
							if not hasattr(server, 'lastcheck') or (date_time.now() - server.last_check).seconds > 180:
								server.last_check = datetime.now()
								server.connect()
								print "New process"
						else:
							num_alive -= 1

				if num_alive == 0:
					break
			except KeyboardInterrupt:
				break
