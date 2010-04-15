"""
:mod:`luckybot.irc.protocol` - IRC Protocol parser
--------------------------------------------------

This module will help you communicate with an IRC server, as it provides
an abstraction of the IRC protocol.

.. module:: luckybot.irc.protocol
   :synopsis: IRC Protocol abstraction

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

import re

class IRCException(Exception):
	pass

class Message(object):
	"""
		This class represents a line from the server
	"""

	RAW_MESSAGE = 0
	USER_MESSAGE = 1
	SERVER_MESSAGE = 2

	def __init__(self, type, raw, sender="", command="", params="", nick="", realname="", hostname="", message="", channel=""):
		self.type = type
		self.raw = raw
		self.sender = sender
		self.command = command
		self.params = params
		self.nick = nick
		self.realname = realname
		self.hostname = hostname
		self.message = message
		self.channel = channel
		self.connection = None

	def __str__(self):
		return self.raw

class Protocol(object):
	"""
		This class provides an abstraction of the IRC protocol
	"""

	def parse_line(self, data):
		"""
			Parses a line from the server into an object with useful
			attributes.

			:Args:
				* data (string): THe line received from the server
		"""

		if len(data) == 0:
			return None

		if data[0] == ':':
			# Get all message parts
			regexp = re.compile(r'\:(.*?) ([a-z0-9]+) (.*?)\r?\n', re.I)
			match = regexp.match(data)

			message_from = match.group(1)
			command = match.group(2)
			params = match.group(3).strip()

			return_obj = None

			# Check from who this message came
			if message_from.find("@") != -1:
				# Message came from a user
				# Retreive nick etc
				regexp2 = re.compile(r'(.*?)!(.*?)@(.*?)$')
				match2 = regexp2.match(message_from)

				# Get the channel
				regexp = re.compile(r'#([^ ]+)')

				match = regexp.match(params)
				# Set channel to the nickname if it was a private message
				# to the bot
				if match:
					channel = '#%s' % match.group(1)
				else:
					channel = match2.group(1)

				return_obj = Message(Message.USER_MESSAGE, data, message_from, command, params, match2.group(1), match2.group(2), match2.group(3), params[params.find(':')+1:], channel)
			else:
				return_obj = Message(Message.SERVER_MESSAGE, data, message_from, command, params, message=params[params.find(':')+1:])

			return return_obj
		else:
			return Message(Message.RAW_MESSAGE, data)

	def send_pm(self, dest, message):
		"""
			Sends a message to a channel or nickname

			:Args:
				* dest (string): The destination of the message (nickname or channel)
				* message (string): The message to send
		"""

		return "PRIVMSG %s :%s" % (dest, message)

	def send_notice(self, dest, message):
		"""
			Sends a notice to a channel or nickname

			:Args:
				* dest (string): The destination of the message (nickname or channel)
				* message (string): The message to send
		"""

		return "NOTICE %s :%s" % (dest, message)

	def send_action(self, dest, message):
		"""
			Sends an 'action' message to a given destination
			Like you use the /me command on a normal IRC client

			:Args:
				* dest (string): The destination of the message (nickname or channel)
				* message (string): The message to send
		"""

		return self.send_pm(dest, "\001ACTION %s\001" % message)

	def join(self, channel):
		"""
			Joins a given channel

			:Args:
				* channel (string): The channel to join
		"""

		if not channel.startswith('#'):
			channel = '#%s' % (channel)

		return "JOIN %s" % channel

	def part(self, channel):
		"""
			Leaves a given channel

			:Args:
				* channel (string): The channel to leave
		"""

		if not channel.startswith('#'):
			channel = '#%s' % channel

		return "PART %s" % channel

	def set_nick(self, nickname):
		"""
			Changes the nickname

			:Args:
				* nickname (string): The new nickname
		"""

		return "NICK %s" % nickname

	def kick(self, channel, nickname, reason = ""):
		"""
			Kicks a specified user

			:Args:
				* channel (string): The channel to kick the user from
				* nickname (string): The nickname of the user
				* reason (string): Optional reason
		"""

		return "KICK %s %s :%s" % (channel, nickname, reason)
