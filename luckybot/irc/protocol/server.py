"""
:mod:`luckybot.irc.protocol.server` - IRC Server handling
=========================================================

This module provides a class from, which you can access all server
data, and, if it's connected, the connection it self.

.. module:: luckybot.irc.protocol.server
   :synopsis: IRC Server handling

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.irc.protocol.handler import ProtocolHandler
from luckybot.connections.multiprocess import MultiProcessConnection
import socket

class Server(object):
	"""
		Represents an IRC server
	"""

	def __init__(self, bot, *args, **kwargs):
		"""
			Constructor, sets the server info.

			:Args:
				* Argument names should be
				  the same as in the directives for the [Server] section in
				  the ini file
		"""

		if 'hostname' not in kwargs:
			raise KeyError, "No hostname specified for the server"

		self.info = kwargs
		self.connection = MultiProcessConnection(socket.SOCK_STREAM)
		self.handler = ProtocolHandler(self)
		self.bot = bot

	def connect(self):
		"""
			Sets up a connection for this server, and connects to it
		"""

		# Default values
		if 'port' in self.info:
			try:
				self.info['port'] = int(self.info['port'])
			except:
				self.info['port'] = 6667
		else:
			self.info['port'] = 6667


		if not 'nickname' in self.info:
			self.info['nickname'] = 'LuckyBot'


		self.connection.open((self.info['hostname'], self.info['port']))
		self.handler.start()

	def send(self, line):
		"""
			Sends the given line to the IRC server, and automaticly
			adds a newline (as required).
		"""

		self.connection.send("%s\n" % line)
		self.bot.ui.data_out(line.strip())
