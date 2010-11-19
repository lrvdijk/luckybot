"""
:mod:`luckybot.ui.console` - Console logger UI
==============================================

UI which consists of a simple console logger

.. module:: luckybot.ui.console
   :synopsis: Console logger UI

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.ui.base import UI
from luckybot.ui.termcolor import colored

class ConsoleUI(UI):
	"""
		Represents the console UI, which simpels writes any data to
		stdout
	"""

	def __init__(self, bot):
		bot.add_listener('servers_loaded', self.start)

	def start(self, bot):
		"""
			Called by the bot when all servers are loaded
		"""

		for server in bot.servers:
			server.add_listener('connected', self.on_connected)
			server.add_listener('data_in', self.data_in)
			server.add_listener('data_out', self.data_out)
			server.add_listener('closed', self.on_closed)

	def data_in(self, server, data):
		print colored("<<< %s" % data, 'yellow')

	def data_out(self, server, data):
		print colored(">>> %s" % data, 'blue')

	def on_connected(self, server):
		print colored('[%s] connected' % str(server), 'green')

	def on_closed(self, server):
		print colored('[%s] closed' % str(server), 'red')
