"""
Gameserver Stats
================

This plugin retreives information about a specific game server, and
outputs it to the channel.

.. module:: gameserver
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from xml.etree import ElementTree
from luckybot.plugin import Plugin
from luckybot.plugin.decorators import command
from luckybot.irc import Format
from gameserver.db import Server
from sqlalchemy.orm import sessionmaker
import re
import socket

from serverstats import Gameserver, GameserverException
from serverstats.protocols.hl import SourceProtocol

class BaseTemplate(object):
	"""
		Server vars -> irc message mapper
	"""

	def __init__(self, server):
		self.server = server

	def get_vars(self):
		raise NotImplementedError

class SourceTemplate(BaseTemplate):
	"""
		Template for source servers
	"""

	def get_vars(self):
		return {
			'ip': self.server.addr[0],
			'port': str(self.server.addr[1]),
			'name': self.server.info['server_name'],
			'map': self.server.info['map'],
			'num_players': str(self.server.info['num_players']),
			'max_players': str(self.server.info['max_players'])
		}

class GameserverPlugin(Plugin):
	PLUGIN_INFO = {
		'name': 'Gameserver',
		'author': ['Lucas van Dijk'],
		'version': '0.1',
		'description': 'Retreives gameserver information',
		'website': 'http://www.return1.net'
	}

	SUPPORTED_GAMES = {
		'source': ('source', 'css', 'dods')
	}

	PROTOCOL_MAP = {
		'source': SourceProtocol
	}

	def initialize(self):
		"""
			Initializer, creates our database table if needed
		"""

		self.db_session = self.bot.session_class()

		Server.metadata.bind = self.bot.db_engine
		Server.metadata.create_all()

	@command('gameserver')
	def get_gameserver_stats(self, event):
		"""
			Called when gameserver command is used
		"""

		try:
			args = event.message.bot_args.split()

			if len(args) == 1:
				# preset
				name = Format.remove(args[0])

				query = self.db_session.query(Server).filter_by(
					name=name, is_approved=1
				)

				row = query.first()

				if not row:
					raise GameserverException, self.language('server_does_not_exists')

				ip = row.ip
				port = row.port
				game = row.game
			elif len(args) == 2:
				addr = args[1].split(':', 1)
				ip = addr[0]
				try:
					port = int(addr[1])
				except:
					raise GameserverException, self.language('invalid_port')

				game = args[0]
			else:
				raise GameserverException, self.language('gameserver_syntax')

			protocol = None
			# check if game is supported
			for game_type, aliasses in self.SUPPORTED_GAMES.iteritems():
				if game in aliasses:
					protocol = self.PROTOCOL_MAP[game_type]
					break

			if protocol == None:
				raise GameserverException, self.language('not_supported')

			# Let's get some stats
			try:
				server = Gameserver(protocol, (ip, port))
				server.query('info')
			except socket.gaierror:
				raise GameserverException, self.language('could_not_connect')

			template = SourceTemplate(server)
			event.channel.pm(self.language('gameserver_template1', **template.get_vars()))
			event.channel.pm(self.language('gameserver_template2', **template.get_vars()))
		except GameserverException, e:
			event.user.notice(str(e))
		except:
			event.user.pm(self.language('something_went_wrong'))
			import traceback
			traceback.print_exc()

	@command(['rss', 'feed', 'last'])
	def read_rss(self, event):
		"""
			Displays the last entries of a RSS feed

			Usage: !rss name or !rss url
		"""

		try:
			if not event.message.bot_command in ['rss', 'feed', 'last']:
				url = event.message.bot_command
			else:
				url = Format.remove(event.message.bot_args)

			# Check URL
			if not self.validate_url(url):
				url = self.get_url(url)
				if not url:
					raise RssException, self.language('not_found')

			rss = RssFeed(url)

			if event.message.bot_command == 'last':
				rss.read(1)
			else:
				rss.read(5)

			event.channel.pm(self.language('rss_title', title=rss.title))
			for item in rss:
				event.channel.pm(self.language('rss_item', title=item['title'], url=item['link']))
		except RssException as error:
			event.channel.pm(error)

	@command('gameservers')
	def list_feeds(self, event):
		"""
			Lists all available gameserver presets
		"""

		query = self.db_session.query(Server).filter_by(is_approved=True)

		event.channel.pm(self.language('available_presets'))
		buffer = ""
		for row in query:
			buffer += row.name + ", "

			if len(buffer) > 255:
				event.channel.pm(buffer[0:-2])
				buffer = ""

		if buffer:
			event.channel.pm(buffer[0:-2])

	@command('addgameserver')
	def add_server(self, event):
		"""
			Allows users to submit their own gameserver, they need to be approved
			by a moderator first

			Usage: !addgameserver name gametype ip:port
		"""

		try:
			args = Format.remove(event.message.bot_args).split()

			if len(args) != 3:
				raise GameserverException, self.language('addgameserver_syntax')

			# Check for supported game
			game = None
			for game_type, aliasses in self.SUPPORTED_GAMES.iteritems():
				if args[1] in aliasses:
					game = game_type
					break

			if game == None:
				raise GameserverException, self.language('not_supported')

			addr = args[2].split(':', 1)
			ip = addr[0]
			try:
				port = int(addr[1])
			except:
				raise GameserverException, self.language('invalid_port')

			name = args[0]

			# Check if the name is already in use
			if self.db_session.query(Server).filter_by(name=name).count() > 0:
				raise GameserverException, self.language('already_exists')

			regexp = re.compile('^[a-zA-Z0-9\-_.]+$')
			if not regexp.match(name):
				raise GameserverException, self.language('invalid_name')

			server = Server(name, game, ip, port, True if event.user.is_allowed('moderator') else False)
			self.db_session.add(server)
			self.db_session.commit()

			event.user.notice(self.language('add_success' if event.user.is_allowed('moderator') else 'needs_review'))
		except GameserverException as error:
			event.channel.pm(error)

	@command('reviewserver')
	def review_servers(self, event):
		"""
			This command can be used by moderators to approve added servers.

			Usage: !reviewserver

			To approve a server: !reviewserver name yes

			To delete a server: !reviewfeed name no
		"""

		if not event.user.is_allowed('moderator'):
			event.user.notice(self.language('permission_denied'))
			return

		args = event.message.bot_args.split()

		if len(args) == 0:
			# Display a list of unapproved feeds
			query = self.db_session.query(Server).filter_by(is_approved=False)

			event.user.notice(self.language('unapproved_feeds'))
			for server in query:
				event.user.notice(self.language('item', server=server))
		elif len(args) == 2:
			server = self.db_session.query(Server).filter_by(name=Format.remove(args[0])).first()

			if not server:
				event.user.notice(self.language('not_found'))
			else:
				if args[1] in ['yes', 'ok', 'good']:
					server.is_approved = True

					self.db_session.commit()
					event.user.notice(self.language('server_approved'))
				elif args[1] in ['no', 'wrong', 'delete']:
					self.db_session.delete(server)
					self.db_session.commit()

					event.user.notice(self.language('server_deleted'))
				else:
					event.user.notice(self.language('review_syntax'))
		else:
			event.user.notice(self.language('review_syntax'))
