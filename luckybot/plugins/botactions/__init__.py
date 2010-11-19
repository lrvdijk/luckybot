"""
Bot actions
===========

This plugin provides some basic actions for the bot like joining, leaving,
changing the nickname etc.

.. module:: botactions
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.plugin import Plugin
from luckybot.plugin.decorators import command
from luckybot.protocols.irc import Format
from luckybot.connections.irc import IRCServerConnection

class BotActions(Plugin):
	PLUGIN_INFO = {
		'name': 'Bot actions',
		'author': ['Lucas van Dijk'],
		'version': '0.1',
		'description': 'Some bot actions like joining/leaving channels, changing nickname etc.',
		'website': 'http://www.return1.net'
	}

	@command('connect')
	def connect(self, event):
		"""
			Connects to a new IRC server

			Usage: !connect host:port [channels] [nickname] [nickserv pass]
		"""

		# Check if calling user has enough permissions
		if not event.user.is_allowed('admin'):
			event.user.notice(self.language('permission_denied'))
			return

		args = event.message.bot_args.split()

		if len(args) == 0:
			event.user.notice(self.language('connect_usage'))
			return

		hostname, port = args[0].split(':')

		try:
			port = int(port)
		except:
			event.user.notice(self.language('invalid_port'))
			return

		if len(args) == 1:
			info = {
				'hostname': hostname,
				'port': port,
				'nickname': self.server.info['nickname'],
				'channels': '',
				'password': ''
			}
		elif len(args) == 2:
			info = {
				'hostname': hostname,
				'port': port,
				'nickname': self.server.info['nickname'],
				'channels': args[1],
				'password': ''
			}
		elif len(args) == 3:
			info = {
				'hostname': hostname,
				'port': port,
				'nickname': args[2],
				'channels': args[1],
				'password': ''
			}
		else:
			info = {
				'hostname': hostname,
				'port': port,
				'nickname': args[2],
				'channels': args[1],
				'password': args[3]
			}

		server = IRCServerConnection(**info)
		self.bot.servers.append(server)

		event.channel.pm(self.language('added_server'))

	@command('disconnect')
	def disconnect(self, event):
		"""
			Disconnects from current server. Note when keep-alive is enabled
			it wil automatically reconnect
		"""

		# Check if calling user has enough permissions
		if not event.user.is_allowed('admin'):
			event.user.notice(self.language('permission_denied'))
			return

		event.server.send(event.server.protocol.quit(event.message.bot_args))

	@command('join')
	def join(self, event):
		"""
			Join the given channel

			Examples: !join #channel or !join #channel1 #channel2
		"""

		# Check if calling user has enough permissions
		if not event.user.is_allowed('admin'):
			event.user.notice(self.language('permission_denied'))
			return

		args = event.message.bot_args.split()
		error = False
		for channel in args:
			if not channel.startswith('#'):
				errors = True
				continue

			event.server.send(event.server.protocol.join(channel))

		if error:
			event.user.notice(self.language('invalid_channels'))

	@command(['part', 'leave'])
	def part(self, event):
		"""
			Leave the current channel (if no argument is given), or a
			given channel.

			Usage: !part or !part #channel1 #channel2
		"""

		# Check if calling user has enough permissions
		if not event.user.is_allowed('admin'):
			event.user.notice(self.language('permission_denied'))
			return

		channels = []
		if not event.message.bot_args:
			if event.message.channel.startswith('#'):
				channels.append(event.message.channel)
		else:
			args = event.message.bot_args.split()

			error = False
			for channel in args:
				if not channel.startswith('#'):
					continue

				channels.append(channel)

		if not channels:
			event.user.notice(self.language('invalid_channels'))
			return

		for channel in channels:
			event.server.send(event.server.protocol.part(channel))

	@command('exec')
	def execute(self, event):
		"""
			Executes a line of python code
		"""

		if not event.user.is_allowed('head_admin'):
			event.user.notice(self.language('permission_denied'))
			return

		if len(event.message.bot_args) == 0:
			return

		r = None

		try:
			exec event.message.bot_args
		except Exception, e:
			r = e

		if r == "" or r == None:
			event.channel.pm(self.language('no_output'))
		else:
			event.channel.pm(self.language('output', output=r))

	@command('nick')
	def nick(self, event):
		"""
			Change nickname of the bot
		"""

		if not event.user.is_allowed('admin'):
			event.user.notice(self.language('permission_denied'))
			return

		if event.message.bot_args:
			event.server.send(event.server.protocol.set_nick(event.message.bot_args))
