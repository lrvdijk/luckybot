"""
Bot information
===============

This plugin provides some basic info of the bot, like registered
commands, uptime, credits and more.

.. module:: botinfo
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.plugin import Plugin, TYPE_COMMAND
from luckybot.plugin.decorators import command, serverevent
from luckybot.protocols.irc import Format
import os.path
from datetime import datetime
import time

class BotInfo(Plugin):
	PLUGIN_INFO = {
		'name': 'Bot Information',
		'author': ['Lucas van Dijk'],
		'version': '0.1',
		'description': 'Some basic bot information like commands, uptime and credits',
		'website': 'http://www.return1.net'
	}

	@command('uptime')
	def uptime(self, event):
		"""
			Shows how long the bot is running
		"""

		# Calculate timediff
		timediff = datetime.now() - self.bot.start_time
		diff = {
			'days': timediff.days,
			'hours': timediff.seconds / 3600,
			'minutes': (timediff.seconds % 3600) / 60,
			'seconds': (timediff.seconds % 3600) % 60
		}

		event.channel.pm(self.language('uptime', diff=diff))

	@command('lag')
	def lag(self, event):
		"""
			Checks the lag between luckybot and the IRC server
		"""

		event.server.send("PING :LAG{0}".format(time.time()))
		self.send_to_channel = event.message.channel

	@serverevent('PONG')
	def lag_response(self, event):
		"""
			Calculates the lag, when PONG reply from the server has been
			received.
		"""

		# create a float from the time received
		time_sent = 0
		try:
			time_sent = float(event.message.message[3:])
		except Exception as e:
			print e
			event.server.send(event.server.protocol.pm(
				self.send_to_channel, self.language('invalid_response')
			))
			return

		lag = round(time.time() - time_sent, 5)

		event.server.send(event.server.protocol.pm(
			self.send_to_channel, self.language('lag', lag=lag)
		))

		self.send_to_channel = ""

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
					if self.bot.plugins.plugins[plugin].PLUGIN_INFO['name'].lower() == name.lower():
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

			if 'author' in plugin_obj.PLUGIN_INFO:
				authors = self.language('created_by', authors=', '.join(plugin_obj.PLUGIN_INFO['author']))

				if 'website' in plugin_obj.PLUGIN_INFO:
					authors += ' - %s' % plugin_obj.PLUGIN_INFO['website']

				event.user.pm(authors)

			functions = plugin_obj.get_functions_for_type(TYPE_COMMAND)
			if functions:
				event.user.pm(self.language('plugin_commands'))

				for function in functions:
					# Get some information from the docstring
					command_doc = "{c}{pfx}{command}{n} - {desc}"
					if function.__doc__:
						doc_parts = function.__doc__.replace("!", self.bot.settings.get('Bot', 'command_prefix')).split("\n\n")

						desc = ""
						for i, part in enumerate(doc_parts):
							if i % 2:
								desc += "{c}"

							part = " ".join([line.strip() for line in part.split("\n")])
							desc += part.strip()

							if i % 2:
								desc += "{n}"

							desc += " - "

						desc = desc.format(c=Format.color(self.bot.settings.get('Bot', 'default_color')),
							n=Format.normal()
						)[0:-3]
					else:
						desc = ""

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



