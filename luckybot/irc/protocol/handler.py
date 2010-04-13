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

from luckybot import bot
from luckybot.irc.protocol import Protocol, IRCException

class ProtocolHandler(object):
	"""
		This class makes sure the right data is sent on the right time
	"""

	def __init__(self):
		"""
			Constructor, creates a protocol object

			Functions in the followinf form:
				`def on_command_xxx(message):`
			where xxx is an IRC reply code, will be automaticly
			called when such message arrives.
		"""

		self.protocol = Protocol()

	def on_line(self, message):
		"""
			Called when a line is received by the bot

			:Args:
				* message (:class:`Message`): The line received as message object

			:Returns:
				String or tuple containing lines to send
		"""

		# Check for PING
		if message.raw.startswith("PING"):
			message.connection.send("PONG :%s" % message.raw[6:])

		if message.type == Message.SERVER_MESSAGE:
			if hasattr(self, 'on_command_%s' % message.command):
				func = getattr(self, 'on_command_%s' % message.command)
				func(message)

	def on_command_001(self, message):
		"""
			Called when we successfully authenticated with the server,
			which means we can join channels
		"""


