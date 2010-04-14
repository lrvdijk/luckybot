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

class PluginException(Exception):
	pass

class Plugin(object):
	"""
		Base plugin class, each plugin should derive from this one
	"""

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
		self.user = User(message)
		self.channel = Channel(message)

class PluginLoader(object):
	"""
		This class handles plugin (re)loading
	"""

	def __init__(self, plugin_dir):
		"""
			Constructor, initializes some members

			:Args:
				* plugin_dirs (list|tuple): List of directories to load plugins from
		"""

		self.plugin_dirs = plugin_dirs
		self.plugins = []

	def load_plugin(self, name):
		"""
			Loads a given plugin

			:Args:
				* name (string): The directory name of the plugin
		"""

		for dir in self.plugin_dirs:
			plugin = self.get_plugin_class(dir, name)

			self.plugins.append(plugin)

	def load_plugins(self, plugins):
		"""
			Loads the given plugins

			:Args:
				* plugins (list|tuple): List of the plugin names to load
		"""

		for name in plugins:
			self.load_plugin(name)

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

		plugin = plugin_cls(self, dir, name)

		return plugin
