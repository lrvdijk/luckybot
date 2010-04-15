"""
Bot information
===============

This plugin provides some basic info of the bot, like registered
commands, uptime, credits and more.

.. module:: botinfo
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.controller import LuckyBot
from luckybot.language import Language
from luckybot.plugin import Plugin, TYPE_COMMAND
from luckybot.plugin.decorators import command
from luckybot.irc import Format
import os.path

class BotActions(Plugin):
	PLUGIN_INFO = {
		'name': 'Bot Information',
		'author': ['Lucas van Dijk'],
		'version': '0.1',
		'description': 'Some basic bot actions like join, part etc',
		'website': 'http://www.return1.net'
	}

	def initialize(self):
		"""
			Loads our language
		"""

		self.bot = LuckyBot.get_bot()

		self.language = Language(self.bot.settings.get('Bot', 'language'),
			self.bot.settings.get('Bot', 'default_color'),
			{'pfx': self.bot.settings.get('Bot', 'command_prefix')}
		)

		print self.PLUGIN_INFO

		self.language.load_language(os.path.join(self.PLUGIN_INFO['plugin_dir'],
			self.PLUGIN_INFO['dirname'], 'language.conf'
		))

	@command(['help', 'info'])
	def help(self, event):
		"""
			Displays some bot information

			Usage: !help or !info
		"""

		event.channel.pm("{c}{b}LuckyBot v5{b} - Created by Lucas van Dijk. http://luckybot.return1.net".format(
			c=Format.color(self.bot.settings.get('Bot', 'default_color')),
			b=Format.bold(),
			n=Format.normal()
		))
		event.channel.pm(self.language('more_information'))

	@command(['plugins', 'plugin'])
	def plugins(self, event):
		"""
			Shows a list of plugins, or specific plugin information

			Usage: !plugins or !plugin name
		"""

		if event.message.bot_args:
			name = event.message.bot_args
			# try to get the plugin instance
			if not name in self.bot.plugins.plugins:
				got_plugin = False

				for plugin in self.bot.plugins.plugins:
					if self.bot.plugins.plugins[plugin].PLUGIN_INFO['name'] == name:
						name = self.bot.plugins.plugins[plugin].PLUGIN_INFO['dirname']
						got_plugin = True

				if not got_plugin:
					name = False

			if not name:
				event.channel.pm(self.language('plugin_not_found'))
				return

			plugin_obj = self.bot.plugins.plugins[name]

			event.user.pm("{c}{b}{plugin[name]} {plugin[version]}".format(
				c=Format.color(self.bot.settings.get('Bot', 'default_color')),
				b=Format.bold(),
				plugin=plugin_obj.PLUGIN_INFO
			))

			if 'description' in plugin_obj.PLUGIN_INFO:
				event.user.pm(plugin_obj.PLUGIN_INFO['description'])

			if 'authors' in plugin_obj.PLUGIN_INFO:
				authors = "%s %s" % (self.language('created_by'), ', '.join(plugin_obj.PLUGIN_INFO['authors']))

				if 'website' in plugin_obj.PLUGIN_INFO:
					authors += ' - %s' % plugin_obj.PLUGIN_INFO['website']

				event.user.send_pm(authors)

			functions = plugin_obj.get_functions_for_type(TYPE_COMMAND)
			if functions:
				event.user.pm(self.language('plugin_commands'))

				for function in functions:
					# Get some information from the docstring
					doc_parts = function.__doc__.split("\n\n")
					command_doc = "{c}{pfx}{command}{n} - {desc}"

					desc = ""
					for i, part in enumerate(doc_parts):
						if i % 2:
							desc += "{c}"
						part = part.replace("\n", " ")
						desc += part.strip()

						if i % 2:
							desc += "{n}"

						desc += " - "

					desc = desc.format(c=Format.color(self.bot.settings.get('Bot', 'default_color')),
						n=Format.normal()
					)[0:-3]

					doc = command_doc.format(c=Format.color('darkred'),
						b=Format.bold(),
						n=Format.normal(),
						pfx=self.bot.settings.get('Bot', 'command_prefix'),
						command=function.command[0],
						desc=desc
					)

					event.user.pm(doc)

					if len(function.command) > 1:
						for i in range(1, len(function.command)):
							doc = command_doc.format(c=Format.color('darkred'),
								b=Format.bold(),
								n=Format.normal(),
								pfx=self.bot.settings.get('Bot', 'command_prefix'),
								command=function.command[i],
								desc=self.language('alias_for', alias=function.command[0])
							)

							event.user.pm(doc)
		else:
			# Send list with plugin names
			buffer = ""
			for plugin in self.bot.plugins.plugins:
				plugin_obj = self.bot.plugins.plugins[plugin]
				buffer += "{0}, ".format(plugin_obj.PLUGIN_INFO['name'])

				if len(buffer) > 250:
					event.channel.pm(buffer[0:-2])
					buffer = ""

			if buffer:
				event.channel.pm(buffer[0:-2])

			event.channel.pm(self.language('plugin_information'))



