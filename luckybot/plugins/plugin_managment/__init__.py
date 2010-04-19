"""
Plugin Managment
================

This plugin provides some commands for on the fly plugin (re)loading.

.. module:: plugin_managment
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.plugin import Plugin, PluginException
from luckybot.plugin.decorators import command
from luckybot.irc import Format

class PluginManagment(Plugin):
	PLUGIN_INFO = {
		'name': 'Plugin Managment',
		'authors': ['Lucas van Dijk'],
		'version': '0.1',
		'description': 'Allows on the fly plugin loading, reloading or unloading',
		'website': 'http://www.return1.net'
	}

	@command('load')
	def load(self, event):
		"""
			Loads a given plugin, if it's not loaded

			Usage: !load plugin_dirname
		"""

		if not event.user.is_allowed('head_admin'):
			event.user.notice(self.language('permission_denied'))
			return

		try:
			name = event.message.bot_args
			if name in self.bot.plugins.plugins:
				event.user.notice(self.language('plugin_already_loaded'))
				return

			for dir in self.bot.plugins.plugin_dirs:
				try:
					self.bot.plugins.load_plugin(dir, name)
				except PluginException:
					continue

				break

			if name in self.bot.plugins.plugins:
				# Yay our plugin has been loaded
				event.channel.pm(self.language('plugin_loaded', plugin=name))
			else:
				raise PluginException, self.language('could_not_load_plugin', plugin=name)
		except Exception as e:
			import traceback
			traceback.print_exc()
			event.channel.pm(self.language('error', error=e, type=type(e)))

	@command('unload')
	def unload(self, event):
		"""
			Unloads a given plugin, if it's loaded

			Usage: !unload plugin_dirname
		"""

		if not event.user.is_allowed('head_admin'):
			event.user.notice(self.language('permission_denied'))
			return

		try:
			name = event.message.bot_args
			if not name in self.bot.plugins.plugins:
				event.user.notice(self.language('plugin_not_loaded'))
				return

			if self.bot.plugins.unload_plugin(name):
				# Yay our plugin has been unloaded
				event.channel.pm(self.language('plugin_unloaded', plugin=name))
			else:
				raise PluginException, self.language('could_not_unload_plugin', plugin=name)
		except Exception as e:
			import traceback
			traceback.print_exc()
			event.channel.pm(self.language('error', error=e, type=type(e)))

	@command('reload')
	def reload(self, event):
		"""
			Reloads a given plugin, if it's loaded

			Usage: !reload plugin_dirname
		"""

		if not event.user.is_allowed('head_admin'):
			event.user.notice(self.language('permission_denied'))
			return

		try:
			name = event.message.bot_args
			if not name in self.bot.plugins.plugins:
				event.user.notice(self.language('plugin_not_loaded'))
				return

			self.bot.plugins.reload_plugin(name)
		except Exception as e:
			import traceback
			traceback.print_exc()
			event.channel.pm(self.language('error', error=e, type=type(e)))
		else:
			# Yay our plugin has been unloaded
			event.channel.pm(self.language('plugin_reloaded', plugin=name))

