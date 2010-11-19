"""
:mod:`luckybot.plugin.proxy` - Plugin Proxy Classes
===================================================

This module provides some proxy classes useful for plugins.

.. module:: luckybot.plugin.proxy
   :synopsis: Plugin Proxy classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

class PluginProxy(object):
	"""
		Plugin event, an object of this class will be passed to the plugin
		containing all the info he needs
	"""

	class Channel(object):
		"""
			Wrapper class to create a better API for communicating
			with user/channel
		"""

		def __init__(self, server, message):
			self.server = server
			self.message = message

		def pm(self, data):
			self.server.send(self.server.protocol.pm(self.message.channel, data))

		def notice(self, data):
			self.server.send(self.server.protocol.notice(self.message.channel, data))

		def action(self, data):
			self.server.send(self.server.protocol.action(self.message.channel, data))

		def part(self):
			self.server.send(self.server.protocol.part(self.message.channel))

		def __str__(self):
			return self.message.channel

	class User(object):
		"""
			Wrapper class to create a better API for communicating
			with user/channel
		"""

		def __init__(self, server, message, bot):
			self.server = server
			self.message = message
			self.bot = bot

		def pm(self, data):
			self.server.send(self.server.protocol.pm(self.message.nick, data))

		def notice(self, data):
			self.server.send(self.server.protocol.notice(self.message.nick, data))

		def action(self, data):
			self.server.send(self.server.protocol.action(self.message.nick, data))

		def kick(self):
			self.server.send(self.server.protocol.kick(self.message.channel, self.message.nick))

		def is_allowed(self, group):
			return self.bot.auth.is_allowed(self.message.hostname, group)

		@property
		def nick(self):
			return self.message.nick

		@property
		def hostname(self):
			return self.message.hostname

		def __str__(self):
			return self.message.nick

	def __init__(self, server, message, bot):
		"""
			Constructor, creates our members
		"""
		self.server = server
		self.message = message

		# Create some dummy objects for a nice api to say things
		self.user = PluginProxy.User(server, message, bot)
		self.channel = PluginProxy.Channel(server, message)
