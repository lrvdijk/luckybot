"""
:mod:`luckybot.irc.protocol.handler` - IRC Protocol handler
-----------------------------------------------------------

This module provides a basic handler class, this class
makes sures the right data will be sent on the right time. You can
easily extend this class and add extra functionality.

.. module:: luckybot.irc.protocol.handler
   :synopsis: IRC Protocol handler

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.irc.protocol import Message, Protocol, IRCException

class ProtocolHandler(object):
	"""
		This class makes sure the right data is sent on the right time
	"""

	def __init__(self, server):
		"""
			Constructor, creates a protocol object

			Functions in the followinf form:
				`def on_command_xxx(message):`
			where xxx is an IRC reply code, will be automaticly
			called when such message arrives.

			:Args:
				* server (:class:`luckybot.irc.protocol.server.Server`): The server object
		"""

		self.protocol = Protocol()
		self.server = server

	def start(self):
		"""
			Called after a connection is opened, this function sends
			the initial commands for an IRC server
		"""

		self.server.send("USER %s 1 * :LuckyBot" % self.server.info['nickname'])
		self.server.send(self.protocol.set_nick(self.server.info['nickname']))

		if 'password' in self.server.info and self.server.info['password']:
			self.server.send(self.protocol.send_pm('nickserv', 'identify %s' % self.server.info['password']))

	def on_line(self, message):
		"""
			Called when a line is received by the bot

			:Args:
				* message (:class:`Message`): The line received as message object

			:Returns:
				String or tuple containing lines to send
		"""

		# Check for PING
		print "<<<", message.raw
		if message.raw.startswith("PING"):
			message.server.send("PONG :%s" % message.raw[6:])

		if message.type == Message.SERVER_MESSAGE:
			if hasattr(self, 'on_command_%s' % message.command):
				func = getattr(self, 'on_command_%s' % message.command)
				func(message)

	def on_command_001(self, message):
		"""
			Called when we successfully authenticated with the server,
			which means we can join channels
		"""

		# Join the channels, if given
		if 'channels' in message.server.info:
			channels = message.server.info['channels'].split(',')
			for channel in channels:
				message.server.send(self.protocol.join(channel.strip()))
