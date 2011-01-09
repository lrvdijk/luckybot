"""
Twitter Plugin
==============

This plugin provides some twitter functionality to the bot, like last
tweets, and notifications for given searches

.. module:: twitter
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.plugin import Plugin, TYPE_COMMAND
from luckybot.plugin.decorators import command, timer
from luckybot.protocols.irc import Format

from urllib import urlencode, unquote_plus
import urllib2
import json
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.tz import gettz

from twitter.db import Notification

from abc import ABCMeta, abstractmethod

class TwitterException(Exception):
	pass

class TweetsReader(object):
	__metaclass__ = ABCMeta

	@abstractmethod
	def get_tweets(self, param):
		pass

class TwitterSearch(TweetsReader):
	"""
		Wrapper for twitter search API
	"""

	def __init__(self, query, refresh_url=None):
		"""
			Initializes a new twitter search
		"""

		self.query = query
		self.refresh_url = refresh_url

	def search(self, query_string):
		"""
			Makes the request to the API, and returns results
		"""

		print query_string
		page = urllib2.urlopen('http://search.twitter.com/search.json' + query_string)
		data = json.loads(page.read())

		if 'refresh_url' in data:
			self.refresh_url = data['refresh_url']

		if 'results' in data:
			return data['results']
		else:
			return []

	def refresh(self):
		"""
			Retreives new tweets sinds last search
		"""

		if not self.refresh_url:
			return None

		return self.search(self.refresh_url)

	def get_tweets(self):
		"""
			Searches for a specific query
		"""

		return self.search('?q=' + self.query)

class TwitterUser(TweetsReader):
	"""
		Wrapper for user timeline API
	"""

	def __init__(self, user):
		self.user = user
		self.last_id = None

	def refresh(self):
		if last_id:
			page = urllib2.urlopen('http://api.twitter.com/1/statuses/user_timeline.json?trim_user=1&screen_name=' + self.user + '&since_id=' + self.last_id)
			data = json.loads(page.read())

			if data:
				self.last_id = data[0]['id']

				return data

		return None

	def get_tweets(self):
		"""
			Get tweets from given user
		"""

		page = urllib2.urlopen('http://api.twitter.com/1/statuses/user_timeline.json?trim_user=1&screen_name=' + self.user)
		data = json.loads(page.read())

		if data:
			self.last_id = data[0]['id']

		return data

class TwitterPlugin(Plugin):
	PLUGIN_INFO = {
		'name': 'Bot Information',
		'author': ['Lucas van Dijk'],
		'version': '0.1',
		'description': 'Adds some twitter functionality to the bot',
		'webiste': 'http://return1.net'
	}

	def initialize(self):
		Notification.metadata.bind = self.bot.db_engine
		Notification.metadata.create_all()

	@command(['twitter', 'twit'])
	def show_last_tweets(self, event):
		"""
			Displays last tweets to current channel
		"""

		if not event.message.bot_args:
			event.channel.pm(self.language('twit_syntax'))
			return

		user = TwitterUser(event.message.bot_args)
		try:
			tweets = user.get_tweets()
		except urllib2.HTTPError as e:
			if e.code == 401:
				event.channel.pm(self.language('tweets_private', user=event.message.bot_args))
			elif e.code == 404:
				event.channel.pm(self.language('user_not_found', user=event.message.bot_args))
			else:
				raise
		else:
			if tweets:
				event.channel.pm(self.language('tweets_from', user=event.message.bot_args))

				for i in range(2):
					tweet = tweets[i]
					# Parse date
					timestamp = parse(tweet['created_at']).replace(tzinfo=gettz('Europe/London')).astimezone(gettz())
					print timestamp
					event.channel.pm(self.language('tweet', text=tweet['text'], date=timestamp.strftime('%a, %d %B %Y %H:%M:%S')))
			else:
				event.channel.pm(self.language('no_tweets_found'))

	@command('twitnotify')
	def add_notification(self, event):
		"""
			Adds a notification for a search or user
		"""

		try:
			args = event.message.bot_args.split(' ', 1)

			# Check for enough arguments
			if len(args) == 1:
				raise TwitterException, self.language('twitnotify_syntax')

			name = urlencode({'x': Format.remove(args[1])})[2:]
			notify_type = Format.remove(args[0])

			if not notify_type in ['search', 'user']:
				raise TwitterException, self.language('twitnotify_syntax')

			# Check search query/user
			try:
				if notify_type == 'search':
					tweets = TwitterSearch(name)
				else:
					tweets = TwitterUser(name)

				results = tweets.get_tweets()
			except:
				import traceback
				traceback.print_exc()
				results = None

			if not results:
				raise TwitterException, self.language('no_tweets_found')

			# Check if the name is already in use
			if self.bot.db_session.query(Notification).filter_by(name=name, type=notify_type).count() > 0:
				raise TwitterException, self.language('name_in_use')

			notification = Notification()
			notification.name = name
			notification.type = notify_type
			notification.server = event.server.info['hostname']
			notification.channel = str(event.channel)
			notification.is_approved = event.user.is_allowed('moderator')
			self.bot.db_session.add(notification)
			self.bot.db_session.commit()

			event.user.notice(self.language('twitnotify_added'))
		except TwitterException as error:
			event.channel.pm(error)
		except Exception as error:
			event.channel.pm(str(type(error)) + ', ' + str(error))
			import traceback
			traceback.print_exc()

	@command('reviewnotify')
	def review_notify(self, event):
		"""
			Review submitted twitter notifications
		"""

		if not event.user.is_allowed('moderator'):
			event.user.notice(self.language('permission_denied'))
			return

		args = event.message.bot_args.split()

		if len(args) == 0:
			# Display a list of unapproved notifications
			query = self.bot.db_session.query(Notification).filter_by(is_approved=False)

			event.user.notice(self.language('unapproved_notifications'))
			for notification in query:
				event.user.notice(self.language('review_notification_template', notification=notification))
		elif len(args) == 2:
			notification = self.bot.db_session.query(Notification).filter_by(id=Format.remove(args[0])).first()

			if not notification:
				event.user.notice(self.language('not_found'))
			else:
				if args[1] in ['yes', 'ok', 'good', 'as_command']:
					notification.is_approved = True

					self.bot.db_session.commit()
					event.user.notice(self.language('notification_approved'))
				elif args[1] in ['no', 'wrong', 'delete']:
					self.bot.db_session.delete(notification)
					self.bot.db_session.commit()

					event.user.notice(self.language('notification_deleted'))
				else:
					event.user.notice(self.language('review_syntax'))
		else:
			event.user.notice(self.language('review_syntax'))

	@timer(30)
	def notification_poller(self):
		"""
			Polls every 30 seconds to check for new twitter messages
		"""

		try:
			# Query DB
			notifications = self.bot.db_session.query(Notification).filter_by(is_approved=True)

			for notification in notifications:
				if notification.type == 'search':
					retreiver = TwitterSearch(notification.name)
				else:
					retreiver = TwitterUser(notification.name)

				tweets = retreiver.get_tweets()
				if tweets:
					# Only send latest tweet
					# parse date
					timestamp = parse(tweets[0]['created_at']).replace(tzinfo=gettz('Europe/London'))

					if notification.last_check:
						last_check = notification.last_check.replace(tzinfo=gettz('Europe/London'))
					else:
						last_check = datetime.now(gettz('Europe/London')) - timedelta(minutes=10)

					if timestamp > last_check:
						server = self.bot.get_server(notification.server)
						timestamp = timestamp.astimezone(gettz())

						if server and server.connection.is_alive:
							if notification.type == 'search':
								server.send(server.protocol.pm(notification.channel, self.language('new_tweet_search',
									text=tweets[0]['text'],
									date=timestamp.strftime('%a, %d %b %Y %H:%M:%S'),
									query=unquote_plus(notification.name)
								)))
							else:
								server.send(server.protocol.pm(notification.channel, self.language('new_tweet_user',
									text=tweets[0]['text'],
									date=timestamp.strftime('%a, %d %b %Y %H:%M:%S'),
									user=unquote_plus(notification.name)
								)))

							notification.last_check = datetime.now()
							self.bot.db_session.commit()
		except Exception as e:
			import traceback
			traceback.print_exc()






