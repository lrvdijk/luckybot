"""
RSS Reader
==========

This plugin is a simple RSS reader. You can add favorite RSS feeds,
which you can call later to read it and display the latest entries.

.. module:: rss
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.plugin import Plugin
from luckybot.plugin.decorators import command
from luckybot.irc import Format
from rss.db import Feed
import urllib2 as urllib

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
			raise Exception, 'Could not parse XML'

		return tree.getroot()

	def read(self, max=5):
		"""
			Reads the RSS feed

			:Args:
				* max (int): Maximum number of items to read
		"""

		xml = self._get_xml(self.url)
		self.title = xml.find('channel').find('title').text

		self.items = []

		items = xml.find('channel').findall('item')

		i = 0
		while i < min(max, len(items)):
			try:
				description = items[i].find('description').text
			except:
				description = ''

			try:
				link = items[i].find('link').text
			except:
				link = ''

			if items[i].find('title').text.startswith('ADV:'):
				max += 1
				i += 1
				continue

			item = {
				'title': items[i].find('title').text,
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
		'version': '0.1'.
		'description': 'Reads RSS feed. and shows the latest entries in channel',
		'website': 'http://www.return1.net'
	}

	def initialize(self):
		"""
			Initializer, creates our database table if needed
		"""

		Feed.metadata.create_all()

		query = self.bot.db_session.query(Feed).filter_by(is_approved=True, register_as_command=True)
		for feed in query:
			self.read_rss.command.append(feed.name)


	def _validate_url(self, url):
		"""
			Checks if the given url is a valid url

			:Args:
				url (string): The url to check
		"""

		regexp = re.compile('([\w]+?://[\w\#$%&~/.\-;:=,?@\[\]+]*)$')
		return regexp.match(url) != None

	@command('rss', 'feed', 'last')
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
				event.channel.pm(self.language('rss_item', title=item.title, url=item.url)
		except RssException as error:
			event.channel.pm(error)




