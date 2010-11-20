#
# LuckyBot4, a python IRC bot
# (c) Copyright 2008 by Lucas van Dijk
# http://www.return1.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA
#
# $Id$
#

try:
	from xml.etree import ElementTree
except ImportError:
	try:
		from elementtree import ElementTree
	except ImportError:
		raise

import urllib2 as urllib
import re

from luckybot.plugin import Plugin
from luckybot.plugin.decorators import command
from luckybot.protocols.irc import Format

class BaseRadio(object):
	@classmethod
	def get_radio(self, name):
		classes = self.__subclasses__()
		for subclass in classes:
			if subclass.__name__.lower() == ('radio_%s' % name).lower():
				return subclass()

		return False

	def now_playing(self):
		raise NotImplementedError

	def get_stream_url(self):
		raise NotImplementedError

	def get_xml(self, url):
		data = urllib.urlopen(url)
		contents = data.read()

		contents = contents.replace('&', '&amp;')
		tree = ElementTree.fromstring(contents)

		return tree

class Radio_538(BaseRadio):
	def now_playing(self):
		root = self.get_xml('http://stream.radio538.nl/538play/nowplaying.xml')

		artist = root.find('now').find('artist').text

		if not artist or len(artist) == 0:
			artist = root.find('previous').find('artist').text
			title = root.find('previous').find('title').text
			previous = True
		else:
			title = root.find('now').find('title').text
			previous = False

		return (artist.lower().title(), title.lower().title())

	def get_stream_url(self):
		return 'http://82.201.100.9:8000/radio538.m3u'

class Radio_SlamFM(BaseRadio):
	def now_playing(self):
		root = self.get_xml('http://www.slamfm.nl/slamfm/nowonair/Onair.XML')

		artist = root.find('Current').find('artistName').text
		title = root.find('Current').find('titleName').text

		return (artist, title)

	def get_stream_url(self):
		return 'http://nl.sitestat.com/slamfm/slam/s?slam.luister.itunes_winamp&ns_type=clickin'

class Radio_3fm(BaseRadio):
	def now_playing(self):
		root = self.get_xml('http://www.3fm.nl/page/xml_daletfeed')

		artist = root.find('artist').text
		title = root.find('title').text

		artist = artist or ""
		title = title or ""

		return (artist.lower().title(), title.lower().title())

	def get_stream_url(self):
		return 'http://cgi.omroep.nl/cgi-bin/shoutcastlive.pls?radio3live'

class Radio_FreshFM(BaseRadio):
	def now_playing(self):
		http = urllib.urlopen('http://www.freshfm.nl')
		contents = http.read()

		regexp = r"<br/><p>(.*?)</p>\s+</div>"

		regexp = re.compile(regexp, re.I | re.M | re.S)
		match = regexp.search(contents)

		song = match.group(1)
		artist, title = song.split(' - ')
		artist = artist.strip()
		title = title.strip()

		return (artist.lower().title(), title.lower().title())

	def get_stream_url(self):
		return 'http://www.fresh.fm/media/audio/ListenHigh.pls'


class RadioPlugin(Plugin):
	"""
		Radio plugin, displays what's playing at several radio stations
	"""

	PLUGIN_INFO = {
		'name': 'Radio',
		'description': "Geeft wat er nu speelt op bepaalde radio stations",
		'authors': ['Lucas van Dijk'],
		'version': '1.0',
		'website': 'http://www.return1.net'
	}
	
	@command('radio')
	def get_radio_np(self, event):
		"""
			Shows what's playing on a specific radio station
			
			For all available radio stations use !radiolist
		"""
		
		radio = BaseRadio.get_radio(event.message.bot_args)

		if radio:
			try:
				np = radio.now_playing()
			except urllib.HTTPError as e:
				event.channel.pm(str(e))
				return
			
			vars = {
				'radio': event.message.bot_args.lower().title(),
				'artist': np[0] or self.language('unknown'),
				'title': np[1] or self.language('unknown')
			}
			
			tpl = 'now_playing'
			
			if len(np) == 3:
				vars.update(program=np[2])
				tpl = 'now_playing_program'
			
			event.channel.pm(self.language(tpl, **vars))
		else:
			event.channel.pm(self.language('radio_does_not_exists'))

	def get_radio_stream(self, event):
		"""
			Get radio stream for a specific radio
		"""
		
		radio = BaseRadio.get_radio(event.message.bot_args)

		if radio:
			event.channel.pm(self.language('stream_tpl', radio=event.message.bot_args.lower().title(), stream=radio.get_stream_url()))
		else:
			event.channel.pm(self.language('radio_does_not_exists'))

	def show_radio_list(self, event):
		"""
			Shows the list of available radios
		"""
		
		classes = BaseRadio.__subclasses__()

		event.user.pm(self.language('available_radios'))
		for subclass in classes:
			buffer += subclass.__name__.lower().replace('radio_', '').title() + ", "

			if len(buffer) > 255:
				event.channel.pm(buffer[0:-2])
				buffer = ""

		if buffer:
			event.channel.pm(buffer[0:-2])

