#
# LuckyBot5, a highly extendable IRC bot written in python
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

import socket
from luckybot.connections.glib import GlibConnection
import gobject

class Client(GlibConnection, gobject.GObject):
	"""
		IRC Client, parses incoming data into an Event object
	"""
	
	__gsignals__ = {
		'connected': (gobject.SIGNAL_RUN_LAST, None, ()),
		'data-received': (gobject.SIGNAL_RUN_LAST, None, (str,)),
		'data-sent': (gobject.SIGNAL_RUN_LAST, None, (str,)),
		'closed': (gobject.SIGNAL_RUN_LAST, None, ())
	}
	
	def __init__(self)
		"""
			Constructor, sets some members
		"""
		
		gobject.GObject.__init__(self)
		GlibConnection.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
	
	def send_pm(self, nick, message):
		"""
			Sends a message to a channel or nickname

			@type nick: string
			@param nick: The channel or nickname to send a message

			@type message: string
			@param message: The message to send
		"""

		return self.send("PRIVMSG %s :%s" % (nick, message))

	def send_notice(self, nick, message):
		"""
			Sends a notice to a given channel/nickname

			@type nick: string
			@param nick: The channel or nickname to send a notice

			@type message: string
			@param message: The message to send
		"""

		return self.send("NOTICE %s :%s" % (nick, message))

	def send_action(self, dest, message):
		"""
			Sends an 'action' message to a given destination
			Like you use the /me command on a normal IRC client

			@type dest: string
			@param dest: The nickname or channel you want to send to

			@type message: string
			@param message: The message
		"""

		self.send_pm(dest, "\001ACTION %s\001" % message)

	def join(self, channel):
		"""
			Joins a given channel

			@type channel: string
			@param channel: The channel to join
		"""

		if not channel.startswith('#'):
			channel = '#%s' % (channel)

		self.send("JOIN %s" % channel)

	def part(self, channel):
		"""
			Leaves a given channel

			@type channel: string
			@param channel: The channel to leave
		"""

		if not channel.startswith('#'):
			channel = '#%s' % channel

		self.send("PART %s" % channel)

	def set_nick(self, nickname):
		"""
			Changes the nickname

			@type nickname: string
			@param nickname: The new nickname
		"""

		self.send("NICK %s" % nickname)
		self.nickname = nickname

	def kick(self, channel, nickname, reason = ""):
		"""
			Kicks a specified user
		"""

		self.send("KICK %s %s :%s" % (channel, nickname, reason))
