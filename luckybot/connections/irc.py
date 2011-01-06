"""
:mod:`luckybot.connections.irc` - IRC Server handling
=====================================================

This module provides the class used for communicating with any IRC
server.

.. module:: luckybot.connections.irc
   :synopsis: IRC Server handling

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.protocols import IRCProtocol
from luckybot.connections import BaseConnection
from luckybot.network import MultiProcessSocket
import socket

class IRCServerConnection(BaseConnection):
	"""
		Represents an IRC server
	"""

	def __init__(self, *args, **kwargs):
		"""
			Constructor, sets the server info.

			:Args:
				* Argument names should be
				  the same as the directives in the [Server] section in
				  the ini file
		"""

		BaseConnection.__init__(self, *args, **kwargs)

		if 'hostname' not in kwargs:
			raise KeyError, "No hostname specified for the server"

		connection_class = kwargs['connection_class'] if 'connection_class' in kwargs else MultiProcessSocket

		self.connection = connection_class(socket.SOCK_STREAM)
		self.protocol = IRCProtocol(self)
		self.buffer = ""

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
		self.emit_signal('connected')

	def send(self, line):
		"""
			Sends the given line to the IRC server, and automatically
			adds a newline (as required in the IRC RFC).
		"""

		self.connection.send("%s\n" % line)
		self.emit_signal('data_out', line.strip())

	def recv(self):
		"""
			Reads a line from the connection, simple proxy method
			to the connection recv method
		"""

		data = self.connection.recv()

		if data:
			self.buffer += data
			self.check_buffer()

		return data

	def close(self):
		"""
			Another proxy method for closing the connection with this
			server
		"""

		self.emit_signal('closed')
		return self.connection.close()

	def check_buffer(self):
		"""
			Checks if a newline is in the buffer (which means end of
			command), and appends it to the recv queue if so
		"""

		pos = self.buffer.find("\n")

		if pos != -1:
			data = self.buffer[0:pos+1]
			self.emit_signal('data_in', data)

			self.buffer = self.buffer[pos+1:]

			if self.buffer.find("\n") != -1:
				self.check_buffer()

	def __str__(self):
		return self.info['hostname']

