"""
Last.FM Information
===================

This plugin retreives information from last.fm for a specific user,
like last played, weekly top tracks or overal top tracks.

.. module:: lastfm
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

try:
	from xml.etree import ElementTree
except ImportError:
	try:
		from elementtree import ElementTree
	except ImportError:
		raise

import urllib2 as urllib

from luckybot.plugin import Plugin
from luckybot.plugin.decorators import command
from luckybot.protocols.irc import Format

class LastFMInfo(object):
	"""
		This class can be used to get Last.FM profile data
	"""

	def __init__(self, username):
		"""
			Initializes the class

			@type username: string
			@param username: The username of the profile you want to get data from
		"""

		self.username = username

	def _get_xml(self, url):
		"""
			Gets an Element object for the given URL

			@type url: string
			@param url: The url to fetch data from

			@rtype: elementtree.Element
			@return: An Element object
		"""

		data = urllib.urlopen(url)

		try:
			tree = ElementTree.ElementTree(file=data)
		finally:
			data.close()

		if not tree or tree == None:
			raise Exception, 'Could not parse XML'

		return tree.getroot()

	def now_playing(self):
		"""
			Gets the current listening track of this user

			@rtype: string
			@return: A string containing the artist an title, or False when there're no tracks
		"""
		elem = self._get_xml('http://ws.audioscrobbler.com/1.0/user/%s/recenttracks.xml' % self.username)

		track = elem.find('track')

		if not track:
			return False

		return {'artist': track.find('artist').text, 'title': track.find('name').text}

	def get_top_tracks(self):
		tree = self._get_xml('http://ws.audioscrobbler.com/1.0/user/%s/toptracks.xml' % self.username)

		tracks = tree.findall('track')

		to_return = []
		i = 0
		while i < 5:
			track = {
				'artist': tracks[i].find('artist').text,
				'title': tracks[i].find('name').text,
				'playcount': tracks[i].find('playcount').text
			}

			to_return.append(track)

			i += 1

		return to_return

	def get_top_artists(self):
		tree = self._get_xml('http://ws.audioscrobbler.com/1.0/user/%s/topartists.xml' % self.username)

		artists = tree.findall('artist')

		to_return = []
		i = 0
		while i < 5:
			track = {
				'artist': artists[i].find('name').text,
				'playcount': artists[i].find('playcount').text
			}

			to_return.append(track)

			i += 1

		return to_return

	def get_weekly_tracks(self):
		tree = self._get_xml('http://ws.audioscrobbler.com/1.0/user/%s/weeklytrackchart.xml' % self.username)

		tracks = tree.findall('track')

		to_return = []
		i = 0
		while i < 5:
			track = {
				'artist': tracks[i].find('artist').text,
				'title': tracks[i].find('title').text,
				'playcount': tracks[i].find('playcount').text
			}

			to_return.append(track)

			i += 1

		return to_return

class LastFMPlugin(Plugin):
	"""
		Last FM information plugin
	"""

	PLUGIN_INFO = {
		'name': 'Last.FM',
		'author': ['Lucas van Dijk'],
		'version': '0.1',
		'description': 'Retreives last.fm information',
		'website': 'http://www.return1.net'
	}

	@command('lastfm')
	def lastfm(self, event):
		# Check which mode
		args = event.message.bot_args.split()

		if len(args) > 1:
			if args[1] == 'tracks':
				self.send_top_tracks(args[0], event)
			elif args[1] == 'artists':
				self.send_top_artists(args[0], event)
			elif args[1] == 'weekly':
				self.send_weekly_top(args[0], event)
			else:
				event.user.notice(self.language('lastfm_usage'))
		elif len(args) == 1:
			self.send_now_playing(args[0], event)
		else:
			event.user.send_notice(self.language('no_user_given'))

	def send_now_playing(self, user, event):
		lastfm = LastFMInfo(user)
		try:
			track = lastfm.now_playing()
		except:
			import traceback
			traceback.print_exc()
			event.channel.pm(self.language('user_not_found'))
		else:
			if not track:
				event.channel.pm(self.language('no_track_playing'))
			else:
				track.update(user=user)
				event.channel.pm(self.language('now_playing', **track))


		del lastfm

	def send_top_tracks(self, user, event):
		lastfm = LastFMInfo(user)

		try:
			tracks = lastfm.get_top_tracks()
		except:
			import traceback
			traceback.print_exc()
			event.channel.pm(self.language('user_not_found'))
		else:
			if len(tracks) == 0:
				event.channel.pm(self.language('no_top_tracks'))
			else:
				event.channel.pm(self.language('top_tracks_from', user=user))

				i = 1
				for track in tracks:
					track.update(num=i)
					event.channel.pm(self.language('top_tracks_tpl', **track))
					i += 1

	def send_top_artists(self, user, event):
		lastfm = LastFMInfo(user)

		try:
			artists = lastfm.get_top_artists()
		except:
			import traceback
			traceback.print_exc()
			event.channel.pm(self.language('user_not_found'))
		else:
			if len(artists) == 0:
				event.channel.pm(self.language('no_top_artists'))
			else:
				event.channel.pm(self.language('top_artists_from', user=user))

				i = 1
				for artist in artists:
					artist.update(num=i)
					event.channel.pm(self.language('top_artists_tpl', **artist))
					i += 1

	def send_weekly_top(self, user, event):
		lastfm = LastFMInfo(user)

		try:
			tracks = lastfm.get_weekly_tracks()
		except:
			import traceback
			traceback.print_exc()
			event.channel.pm(self.language('user_not_found'))
		else:
			if len(tracks) == 0:
				event.channel.pm(self.language('no_top_tracks'))
			else:
				event.channel.pm(self.language('weekly_top_tracks_from', user=user))

				i = 1
				for track in tracks:
					track.update(num=i)
					event.channel.pm(self.language('top_tracks_tpl', **track))
					i += 1
