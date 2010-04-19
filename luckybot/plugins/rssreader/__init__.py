"""
RSS Reader
==========

This plugin is a simple RSS reader. You can add favorite RSS feeds,
which you can call later to read it and display the latest entries.

.. module:: rssreader
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

try:
	from xml.etree import ElementTree
except ImportError:
	try:
		from elementtree import ElementTree
	except ImportError:
		raise

from luckybot.plugin import Plugin
from luckybot.plugin.decorators import command
from luckybot.irc import Format
from rssreader.db import Feed
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
import urllib2 as urllib
import re

class RssException(Exception):
	pass

class RssFeed(object):
	"""
		Reads RSS feeds
	"""

	def __init__(self, url):
		self.url = url

	def get_xml(self, url):
		"""
			Gets an Element object for the given URL

			:Args:
				* url (string): The url to read

			:Returns:
				Element object (of elementtree module)
		"""

		data = urllib.urlopen(url)

		try:
			tree = ElementTree.ElementTree(file=data)
		finally:
			data.close()

		if not tree or tree == None:
			raise RssException, 'Could not parse XML'

		return tree.getroot()

	def read(self, max=5):
		"""
			Reads the RSS feed

			:Args:
				* max (int): Maximum number of items to read
		"""

		xml = self.get_xml(self.url)
		self.title = xml.find('channel').find('title').text

		self.items = []

		items = xml.find('channel').findall('item')

		i = 0
		while i < min(max, len(items)):
			try:
				description = items[i].find('description').text.encode('utf-8')
			except:
				description = ''

			try:
				link = items[i].find('link').text.encode('utf-8')
			except:
				link = ''

			if items[i].find('title').text.startswith('ADV:'):
				max += 1
				i += 1
				continue

			item = {
				'title': items[i].find('title').text.encode('utf-8'),
				'description': description,
				'link': link
			}

			self.items.append(item)
			i += 1

	def __iter__(self):
		return iter(self.items)

class Rss(Plugin):
	PLUGIN_INFO = {
		'name': 'RSS Reader',
		'author': ['Lucas van Dijk'],
		'version': '0.1',
		'description': 'Reads RSS feed. and shows the latest entries in channel',
		'website': 'http://www.return1.net'
	}

	def initialize(self):
		"""
			Initializer, creates our database table if needed
		"""

		self.db_session = self.bot.session_class()

		Feed.metadata.bind = self.bot.db_engine
		Feed.metadata.create_all()

		query = self.db_session.query(Feed).filter_by(is_approved=True, register_as_command=True)
		for feed in query:
			self.read_rss.command.append(feed.name)


	def validate_url(self, url):
		"""
			Checks if the given url is a valid url

			:Args:
				url (string): The url to check
		"""

		regexp = re.compile('([\w]+?://[\w\#$%&~/.\-;:=,?@\[\]+]*)$')
		return regexp.match(url) != None

	def get_url(self, name):
		"""
			Retreives the url from database for a given feed name

			:Args:
				* name (string): The name of the feed

			:Returns:
				None if the feed isn't found, else the URL
		"""
		query = self.db_session.query(Feed).filter_by(
			name=name, is_approved=True
		)

		feed = query.first()

		return None if feed is None else feed.url

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

	@command('feeds')
	def list_feeds(self, event):
		"""
			Lists all available RSS feeds
		"""

		query = self.db_session.query(Feed).filter_by(is_approved=True)

		event.channel.pm(self.language('available_feeds'))
		buffer = ""
		for row in query:
			buffer += row['name'] + ", "

			if len(buffer) > 255:
				event.channel.pm(buffer[0:-2])
				buffer = ""

		if buffer:
			event.channel.pm(buffer[0:-2])

	@command('addfeed')
	def add_feed(self, event):
		"""
			Allows users to submit their own feed, they need to be approved
			by a moderator first

			Usage: !addfeed name url
		"""

		try:
			args = event.message.bot_args.split(' ', 1)

			# Check for enough arguments
			if len(args) == 1:
				raise RssException, self.language('addfeed_syntax')

			url = Format.remove(args[1])

			# Check URL
			if not self.validate_url(url):
				raise RssException, self.language('invalid_url')

			name = Format.remove(args[0])

			# Check if the name is already in use
			if self.db_session.query(Feed).filter_by(name=name).count() > 0:
				raise RssException, self.language('name_in_use')

			regexp = re.compile('^[a-zA-Z0-9\-_.]+$')
			if not regexp.match(name):
				raise RssException, self.language('invalid_name')

			feed = Feed(name, url, True if event.user.is_allowed('moderator') else False)
			self.db_session.add(feed)
			self.db_session.commit()

			event.user.notice(self.language('feed_added'))
		except RssException as error:
			event.channel.pm(error)

	@command('reviewfeed')
	def review_feed(self, event):
		"""
			This command can be used by moderators to approve added feeds.

			Usage: !reviewfeed

			To approve a feed: !reviewfeed name yes

			To register a feed as direct command: !reviewfeed name as_command

			To delete a feed: !reviewfeed name no
		"""

		if not event.user.is_allowed('moderator'):
			event.user.notice(self.language('permission_denied'))
			return

		args = event.message.bot_args.split()

		if len(args) == 0:
			# Display a list of unapproved feeds
			query = self.db_session.query(Feed).filter_by(is_approved=False)

			event.user.notice(self.language('unapproved_feeds'))
			for feed in query:
				event.user.notice(self.language('review_feed_template', feed=feed))
		elif len(args) == 2:
			feed = self.db_session.query(Feed).filter_by(name=Format.remove(args[0])).first()

			if not feed:
				event.user.notice(self.language('not_found'))
			else:
				if args[1] in ['yes', 'ok', 'good', 'as_command']:
					feed.is_approved = True
					if args[1] == 'as_command':
						feed.register_as_command = True

					self.db_session.commit()
					event.user.notice(self.language('feed_approved'))

					if args[1] == 'as_command':
						self.bot.plugins.reload_plugin(self.PLUGIN_INFO['dirname'])

				elif args[1] in ['no', 'wrong', 'delete']:
					self.db_session.delete(feed)
					self.db_session.commit()

					event.user.notice(self.language('feed_deleted'))
				else:
					event.user.notice(self.language('review_syntax'))
		else:
			event.user.notice(self.language('review_syntax'))
