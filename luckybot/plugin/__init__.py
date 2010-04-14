"""
:mod:`luckybot.plugin` - Plugin Managment
-----------------------------------------

This module provides the basic class for our plugin system.

.. module:: luckybot.plugin
   :synopsis: Plugin Managment

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

import sys
import os
import re
import imp
import inspect
from abc import ABCMeta

TYPE_COMMAND = 1
TYPE_USER_EVENT = 2
TYPE_SERVER_EVENT = 3
TYPE_REGEXP_RAW = 4
TYPE_REGEXP_MESSAGE = 5

class PluginException(Exception):
	pass

class Plugin(object):
	"""
		Base plugin class, each plugin should derive from this one
	"""

	__metaclass__ = ABCMeta

	def __init__(self, plugin_dir, dirname):
		"""
			Initializes some basic plugin info

			:Args:
				* plugin_dir (string): The directory where the plugin lives in
				* dirname (string): The name of the plugin directory
		"""

		if not hasattr(self, 'PLUGIN_INFO'):
			raise PluginException, "Plugin %s has no PLUGIN_INFO defined" % dirname

		self.PLUGIN_INFO['plugin_dir'] = plugin_dir
		self.PLUGIN_INFO['dirname'] = dirname

	def get_functions_for_type(self, type):
		"""
			Gets all plugin handler functions for a given type

			:Args:
				* type (int): The function handler type
		"""

		members = dir(self)
		functions = []

		for member in members:
			if member[0] == '_':
				continue

			if hasattr(getattr(self, member), 'handler_type'):
				if getattr(self, member).handler_type == type:
					functions.append(getattr(self, member))
		return functions

class Event(object):
	"""
		Plugin event, an object of this class will be passed to the plugin
		containing all the info he needs
	"""

	class Channel(object):
		"""
			Wrapper class to create a better API for communicating
			with user/channel
		"""

		def __init__(self, message):
			self.message = message

		def pm(self, data):
			self.message.server.send(
				self.message.server.handler.protocol.send_pm(self.message.channel, data)
			)

		def notice(self, data):
			self.message.server.send(
				self.message.server.handler.protocol.send_notice(self.message.channel, data)
			)

		def action(self, data):
			self.message.server.send(
				self.message.server.handler.protocol.send_action(self.message.channel, data)
			)

		def part(self):
			self.message.server.send(
				self.message.server.handler.protocol.part(self.message.channel)
			)

		def __str__(self):
			return self.message.channel

	class User(object):
		"""
			Wrapper class to create a better API for communicating
			with user/channel
		"""

		def __init__(self, message):
			self.message = message

		def pm(self, data):
			self.message.server.send(
				self.message.server.handler.protocol.send_pm(self.message.nick, data)
			)

		def notice(self, data):
			self.message.server.send(
				self.message.server.handler.protocol.send_notice(self.message.nick, data)
			)

		def action(self, data):
			self.message.server.send(
				self.message.server.handler.protocol.send_action(self.message.nick, data)
			)

		def kick(self):
			self.message.server.send(
				self.message.server.handler.protocol.kick(self.message.nick)
			)

		def __str__(self):
			return self.message.nick

	def __init__(self, message):
		"""
			Constructor, creates our members
		"""

		self.message = message

		# Create some dummy objects for a nice api to say things
		self.user = Event.User(message)
		self.channel = Event.Channel(message)

class PluginManager(object):
	"""
		This class handles plugin (re)loading
	"""

	def __init__(self, disabled=[]):
		"""
			Constructor, initializes some members
		"""

		self.disabled = disabled
		self.plugin_dirs = []

		self.plugins = []

		self.commands = []
		self.user_events = []
		self.server_events = []
		self.message_regexps = []
		self.raw_regexps = []

	def load_plugin(self, dir, name):
		"""
			Loads a given plugin

			:Args:
				* name (string): The directory name of the plugin
		"""

		plugin = self.get_plugin_class(dir, name)

		if hasattr(plugin, 'initialize'):
			plugin.initialize()

		self.commands.extend(plugin.get_functions_for_type(TYPE_COMMAND))
		self.user_events.extend(plugin.get_functions_for_type(TYPE_USER_EVENT))
		self.server_events.extend(plugin.get_functions_for_type(TYPE_SERVER_EVENT))
		self.raw_regexps.extend(plugin.get_functions_for_type(TYPE_REGEXP_RAW))
		self.message_regexps.extend(plugin.get_functions_for_type(TYPE_REGEXP_MESSAGE))
		self.plugins.append(plugin)

	def load_plugins(self, dir):
		"""
			Loads the given plugins

			:Args:
				* dir (string): Directory to load plugins from
		"""

		if not os.path.isdir(dir):
			return

		for file in os.listdir(dir):
			if file[0] == '_' or file[0] == '.' or not os.path.isdir(os.path.join(dir, file)):
				continue

			if file in self.disabled:
				continue

			self.load_plugin(dir, file)

		if dir not in self.plugin_dirs:
			self.plugin_dirs.append(dir)

	def get_plugin_class(self, directory, name):
		"""
			Loads the plugin class from the given plugin
		"""

		path = os.path.join(directory, name)

		if not os.path.isdir(path) or not os.path.exists(os.path.join(path, '__init__.py')):
			raise PluginException, "Plugin %s does not exist" % name

		sys.path.insert(0, path)
		module_obj = imp.load_source(name, os.path.join(path,'__init__.py'))
		sys.path = sys.path[1:]

		# Check for the base plugin class, by looping through each class
		# defined in the module, and checking if it derives from Plugin
		plugin_cls = None
		for cls in module_obj.__dict__.values():
			if hasattr(cls, '__module__'):
				if inspect.isclass(cls) and cls.__module__ == name:
					if issubclass(cls, Plugin):
						plugin_cls = cls
						break

		if plugin_cls == None:
			raise PluginException, "Plugin %s has no base pluginclass defined" % name

		plugin = plugin_cls(dir, name)

		return plugin

	def check_event(self, message):
		"""
			Checks for an incoming event if there's any plugin to be
			called.

			:Args:
				* message (:class:`luckybot.irc.protocol.Message`): The message received from the server
		"""

		# Create new event objevt
		event = Event(message)

		if self.raw_regexps:
			# Call plugins which want to perform a regexp on the raw
			# message first
			for function in self.raw_regexps:
				# Match the regexp
				regexp = re.compile(function.pattern, function.modifiers)
				match = regexp.match(message.raw)

				if match:
					function(event, match)

		if self.commands:
			# Check for command plugins
			if hasattr(message, 'bot_command'):
				for function in self.commands:
					if message.bot_command in function.command:
						function(event)

		if self.server_events:
			# Server replies
			if message.type == Message.SERVER_MESSAGE:
				for function in self.server_events:
					if message.command in function.events:
						function(event)

		if self.user_events:
			# User events
			if message.type == Message.USER_MESSAGE:
				for function in self.user_events:
					if message.command in function.events:
						function(event)

		if self.message_regexps:
			if message.type == Message.USER_MESSAGE and message.command == "PRIVMSG":
				for function in self.message_regexps:
					# Match the regexp
					regexp = re.compile(function.pattern, function.modifiers)
					match = regexp.match(message.message)

					if match:
						function(event, match)



