"""
:mod:`luckybot.plugin.managment` - Plugin Managment
=========================================

This module provides the basic class for our plugin system.

.. module:: luckybot.plugin.managment
   :synopsis: Plugin Managment

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

import sys
import os
import re
import imp
import inspect
import gc
from abc import ABCMeta
from datetime import timedelta, datetime

from luckybot.protocols.irc import Message
from luckybot.language import Language

TYPE_COMMAND = 1
TYPE_USER_EVENT = 2
TYPE_SERVER_EVENT = 3
TYPE_REGEXP_RAW = 4
TYPE_REGEXP_MESSAGE = 5
TYPE_TIMER = 6

class PluginException(Exception):
	pass

class Plugin(object):
	"""
		Base plugin class, each plugin should derive from this one
	"""

	__metaclass__ = ABCMeta

	def __init__(self, bot, plugin_dir, dirname):
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

		if not 'version' in self.PLUGIN_INFO:
			self.PLUGIN_INFO['version'] = ''

		self.bot = bot

		if os.path.exists(os.path.join(plugin_dir, dirname, 'language.conf')):
			self.language = Language(self.bot.settings.get('Bot', 'language'),
				self.bot.settings.get('Bot', 'default_color'),
				{'pfx': self.bot.settings.get('Bot', 'command_prefix')}
			)

			self.language.load_language(os.path.join(self.PLUGIN_INFO['plugin_dir'],
				self.PLUGIN_INFO['dirname'], 'language.conf'
			))

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

class PluginManager(object):
	"""
		This class handles plugin (re)loading
	"""

	def __init__(self, bot, disabled=[]):
		"""
			Constructor, initializes some members
		"""

		self.bot = bot
		self.disabled = disabled
		self.plugin_dirs = []

		self.plugins = {}

		self.commands = []
		self.user_events = []
		self.server_events = []
		self.message_regexps = []
		self.raw_regexps = []
		self.timers = []

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
		self.timers.extend(plugin.get_functions_for_type(TYPE_TIMER))
		self.plugins[name] = plugin

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

	def unload_plugin(self, name):
		"""
			Unload a given plugin.

			:Args:
				* name (string): The name of the plugin to unload.
				  This can be either the directory name, or the name specified
				  in the plugin metadata
		"""

		# try to find the plugin
		# based on dirname or the plugin name
		if not name in self.plugins:
			got_plugin = False
			for plugin in self.plugins:
				if name == self.plugins[plugin].PLUGIN_INFO['name']:
					name = self.plugins[plugin].PLUGIN_INFO['dirname']
					got_plugin = True
					break

			if got_plugin == False:
				name = False

		if name == False:
			return False

		# Remove all functions
		functions = self.plugins[name].get_functions_for_type(TYPE_COMMAND)
		for function in functions:
			self.commands.remove(function)

		functions = self.plugins[name].get_functions_for_type(TYPE_SERVER_EVENT)
		for function in functions:
			self.server_events.remove(function)

		functions = self.plugins[name].get_functions_for_type(TYPE_USER_EVENT)
		for function in functions:
			self.user_events.remove(function)

		functions = self.plugins[name].get_functions_for_type(TYPE_REGEXP_MESSAGE)
		for function in functions:
			self.message_regexps.remove(function)

		functions = self.plugins[name].get_functions_for_type(TYPE_REGEXP_RAW)
		for function in functions:
			self.raw_regexps.remove(function)

		functions = self.plugins[name].get_functions_for_type(TYPE_TIMER)
		for function in functions:
			self.timers.remove(function)

		if hasattr(self.plugins[name], 'destroy'):
			self.plugins[name].destroy()

		del self.plugins[name]

		gc.collect()

		return True

	def reload_plugin(self, name):
		"""
			Reloads a given plugin

			:Args:
				* name (string): Name of the plugin
		"""

		if name in self.plugins:
			plugin_dir = self.plugins[name].PLUGIN_INFO['plugin_dir']
			self.unload_plugin(name)
			self.load_plugin(plugin_dir, name)


	def get_plugin_class(self, directory, name):
		"""
			Loads the plugin class from the given plugin
		"""

		if not os.path.exists(os.path.join(directory, name, '__init__.py')):
			raise PluginException, "Plugin %s does not exist" % name

		try:
			(file, pathname, desc) = imp.find_module(name, [directory])
			module_obj = imp.load_module(name, file, pathname, desc)
		except ImportError:
			import traceback
			traceback.print_exc()
			raise PluginException, "Could not load plugin %s" % name
		finally:
			if file:
				file.close()

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

		plugin = plugin_cls(self.bot, directory, name)

		return plugin

	def check_event(self, proxy):
		"""
			Checks for an incoming event if there's any plugin to be
			called.

			:Args:
				* message (:class:`luckybot.plugin.proxy.PluginProxy`): Plugin proxy object
		"""

		# Create new event objevt
		message = proxy.message

		if self.raw_regexps:
			# Call plugins which want to perform a regexp on the raw
			# message
			for function in self.raw_regexps:
				# Match the regexp
				regexp = re.compile(function.pattern, function.modifiers)
				match = regexp.match(message.raw)

				if match:
					function(proxy, match)

		if self.commands:
			# Check for command plugins
			if hasattr(message, 'bot_command'):
				for function in self.commands:
					if message.bot_command.lower() in function.command:
						function(proxy)

		if self.server_events:
			# Server replies
			if message.type == Message.SERVER_MESSAGE:
				for function in self.server_events:
					if message.command in function.event:
						function(proxy)

		if self.user_events:
			# User proxys
			if message.type == Message.USER_MESSAGE:
				for function in self.user_events:
					if message.command in function.event:
						function(proxy)

		if self.message_regexps:
			if message.type == Message.USER_MESSAGE and message.command == "PRIVMSG":
				for function in self.message_regexps:
					# Match the regexp
					regexp = re.compile(function.pattern, function.modifiers)
					match = regexp.match(message.message)

					if match:
						function(proxy, match)

	def check_timers(self):
		"""
			Checks for plugin timers, and calls them again, after the given
			amount of time
		"""

		for timer in self.timers:
			if not timer.timer.last_call:
				timer.timer.last_call = datetime.now()
				timer()
			else:
				if (timer.timer.last_call + timedelta(seconds=timer.timer.seconds)) < datetime.now():
					timer.timer.last_call = datetime.now()
					timer()



