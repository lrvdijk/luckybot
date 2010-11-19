"""
:mod:`luckybot.protocols.irc` - IRC Protocol abstaction
=======================================================

This module will help you communicate with an IRC server, as it provides
an abstraction of the IRC protocol.

.. module:: luckybot.protocols.irc
   :synopsis: IRC Protocol abstraction

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.protocols.base import Message

import re

class IRCException(Exception):
	pass

class IRCProtocol(object):
	"""
		This class provides an abstraction of the IRC protocol, and handles
		incoming IRC messages.

		Functions in the following form:
			`def on_command_xxx(message):`
		where xxx is an IRC reply code, will be automaticly
		called when such message arrives.
	"""

	def __init__(self, server):
		"""
			Constructor, creates a protocol object

			:Args:
				* server (:class:`luckybot.connections.irc.IRCServerConnection`): The server object
		"""

		self.server = server
		self.server.add_listener('connected', self.start)
		self.server.add_listener('data_in', self.on_line)

	def start(self, server):
		"""
			Called after a connection is opened, this function sends
			the initial commands for an IRC server
		"""

		self.server.send("USER %s 1 * :LuckyBot" % self.server.info['nickname'])
		self.server.send(self.set_nick(self.server.info['nickname']))

		if 'password' in self.server.info and self.server.info['password']:
			self.server.send(self.pm('nickserv', 'identify %s' % self.server.info['password']))

	def on_line(self, server, data):
		"""
			Called when a full line of an IRC message has received.
			We parse the message, respond to ping, and call functions
			related to the IRC reply code
		"""

		message = self.parse_line(data)

		# Check for PING
		if message.raw.startswith("PING"):
			self.server.send("PONG :%s" % message.raw[6:])

		if message.type == Message.SERVER_MESSAGE:
			if hasattr(self, 'on_command_%s' % message.command):
				func = getattr(self, 'on_command_%s' % message.command.lower())
				func(message)

	def on_command_001(self, message):
		"""
			Called when we successfully authenticated with the server,
			which means we can join channels
		"""

		# Join the channels, if given
		if 'channels' in self.server.info:
			channels = self.server.info['channels'].split(',')
			for channel in channels:
				self.server.send(self.join(channel.strip()))

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

				args = {
					'sender': message_from,
					'command': command,
					'params': params,
					'nick': match2.group(1),
					'realname': match2.group(2),
					'hostname': match2.group(3),
					'message': params[params.find(':')+1:],
					'channel': channel
				}

				cmd_prefix = self.server.info['prefix']
				message = args['message']

				# Check if a bot command is called
				if command == 'PRIVMSG' and message[0:len(cmd_prefix)] == cmd_prefix:
					space_pos = message.find(' ', len(cmd_prefix))
					if space_pos == -1:
						space_pos = len(message)

					bot_command = message[len(cmd_prefix):space_pos]
					args['bot_command'] = bot_command
					args['bot_args'] = message[space_pos+1:]

				return_obj = Message(Message.USER_MESSAGE, data, **args)
			else:
				args = {
					'sender': message_from,
					'command': command,
					'params': params,
					'message': params[params.find(':')+1:]
				}

				return_obj = Message(Message.SERVER_MESSAGE, data, **args)

			return return_obj
		else:
			return Message(Message.RAW_MESSAGE, data)

	def pm(self, dest, message):
		"""
			Sends a message to a channel or nickname

			:Args:
				* dest (string): The destination of the message (nickname or channel)
				* message (string): The message to send
		"""

		return "PRIVMSG %s :%s" % (dest, message)

	def notice(self, dest, message):
		"""
			Sends a notice to a channel or nickname

			:Args:
				* dest (string): The destination of the message (nickname or channel)
				* message (string): The message to send
		"""

		return "NOTICE %s :%s" % (dest, message)

	def action(self, dest, message):
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

	def quit(self, message=""):
		"""
			Quits from the IRC server

			:Args:
				* message (string): Optional quit message
		"""

		return "QUIT %s" % message

class Format(object):
	"""
		This class can be used to format messages sent to the IRC server
	"""

	black = 1
	darkblue = 2
	green = 3
	red = 4
	darkred = 5
	purple = 6
	orange = 7
	yellow = 8
	lightgreen = 9
	aqua = 10
	lightblue = 11
	blue = 12
	violet = 13
	grey = 14
	lightgrey = 15
	white = 16

	@classmethod
	def color(self, color):
		"""
			Add a color to a message

			:Args:
				* color (string): The name of the color
		"""
		try:
			code = getattr(self, color)
		except:
			code = 1

		return "\x03%02.f" % (code)

	@classmethod
	def normal(self):
		"""
			Reset to the default color
		"""
		return "\x0F"

	@classmethod
	def bold(self):
		"""
			Make the text bold
		"""
		return "\x02"

	@classmethod
	def reverse(self):
		"""
			Make the text italic (doet not work for all clients)
		"""
		return "\x16"

	@classmethod
	def underline(self):
		"""
			Underline the text
		"""
		return "\x1F"

	@classmethod
	def remove(self, string):
		"""
			Remove all format in the given string

			:Args:
				* string (string): The string to cleanup
		"""

		regexp = re.compile('(?:(?:\x03[0-9]+)|(?:\x0F|\x02|\x16|\x1F))', re.I)

		return regexp.sub('', string)
