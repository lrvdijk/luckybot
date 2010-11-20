"""
:mod:`luckybot.bot` - Main controller class
===========================================

This is our main bot controller, manages plugins, servers and more

.. module:: luckybot.bot
   :synopsis: Main controller class

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot import base_path, user_path, __version__
from luckybot.processes import ProcessManager
from luckybot.plugin import PluginManager, PluginProxy
from luckybot.auth import Authentication
from luckybot.signals import SignalEmitter
from luckybot.connections.irc import IRCServerConnection

from ConfigParser import SafeConfigParser
from datetime import datetime
import optparse
import os
import re
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class LuckyBot(SignalEmitter):
	"""
		Main application controller
	"""

	available_events = ('servers_loaded',)
	bot = None

	def __init__(self):
		"""
			Constructor, initializes some basic bot functionality
		"""

		SignalEmitter.__init__(self)

		# setup option parser
		self.parser = optparse.OptionParser(usage="%prog [options]",
			version="LuckyBot v%s" % __version__)
		self.parser.add_option('-u', '--ui', dest="ui",
			help="GUI type: currently only console supported",
			default="console")

		options, args = self.parser.parse_args(sys.argv)

		temp = __import__('luckybot.ui.%s' % options.ui.lower())
		ui_module = getattr(temp.ui, options.ui.lower())
		if not hasattr(ui_module, '%sUI' % options.ui.title()):
			raise ImportError, "UI type %s.%sUI doesn't exists" % (ui_module.__name__, options.ui.title())

		ui_class = getattr(ui_module, '%sUI' % options.ui.title())
		self.ui = ui_class(self)

		self.start_time = None

		# Load settings
		self.settings = SafeConfigParser()
		if os.path.exists(user_path('settings.conf')):
			self.settings.read(user_path('settings.conf'))
		else:
			self.settings.read(base_path('data', 'settings.conf'))

		# Setup database
		self.db_engine = create_engine(self.settings.get('Bot', 'database'))
		self.db_engine.connect()
		self.session_class = sessionmaker(bind=self.db_engine)
		self.db_session = self.session_class()

		# Setup authentication
		# Builtin groups
		groups = {
			'head_admin': 1,
			'admin': 2,
			'moderator': 3
		}
		users = {}

		for option in self.settings.options('Groups'):
			groups[option] = self.settings.getint('Groups', option)

		for option in self.settings.options('Admins'):
			users[option] = self.settings.get('Admins', option)

		self.auth = Authentication(groups, users)

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

				config['prefix'] = self.settings.get('Bot', 'command_prefix')

				server = IRCServerConnection(**config)
				servers.append(server)

		return servers

	def start(self):
		"""
			Creates for each server a subprocess, and runs the bot
		"""

		self.start_time = datetime.now()

		# Load plugins
		self.plugins = PluginManager(self)
		self.plugins.load_plugins(base_path('plugins'))

		self.servers = self.get_servers()

		# Add listeners
		for server in self.servers:
			server.add_listener('data_in', self.data_in)

		self.emit_signal('servers_loaded')

		process_manager = ProcessManager(self.servers, self.settings.getboolean('Bot', 'keep_alive'))
		num_alive = len(self.servers)

		# Our main loop
		while num_alive > 0:
			try:
				num_alive = process_manager.check_processes()

			except KeyboardInterrupt:
				break

	def data_in(self, server, data):
		"""
			Event handler when a server receives data
		"""

		message = server.protocol.parse_line(data)

		# Setup plugin proxy
		proxy = PluginProxy(server, message, self)

		# Pass it through all plugins
		try:
			self.plugins.check_event(proxy)
		except Exception as e:
			import traceback
			traceback.print_exc()
			
			server.send(server.protocol.pm(message.channel, "BOOM Error: %s" % (str(e))))
			

