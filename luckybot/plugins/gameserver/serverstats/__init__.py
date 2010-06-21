#
# RCON Anywhere - http://www.rcon-anywhere.net
# Desktop tool
#
# Created by Lucas van Dijk (www.return1.net)
#
# Package serverstats
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
# $Id: __init__.py 76 2009-05-19 14:06:14Z luckyluke56 $
#

import re
import socket
from luckybot.connections import Connection
from .protocols import Packet

class GameserverException(Exception):
	pass

class Gameserver(object):
	"""
		Represents a gameserver
	"""

	def __init__(self, protocol, addr):
		"""
			Sets the game type
		"""

		self.addr = addr
		self.protocol = protocol(self)
		self.protocol.server = self

	def query(self, type):
		"""
			Queries the current gameserver

			@type query_string: string
			@param query_string: The query type to send
		"""

		self.protocol.query(self.protocol.get_query(type))

class Protocol(object):
	"""
		The base protocol all other game protocols should derive from
	"""

	connection_class = Connection

	def __init__(self, server):
		"""
			Sets the gameserver object as a member
		"""

		self.server = server

		# Setup connection
		self.connection = self.connection_class(socket.SOCK_DGRAM)
		self.connection.open(server.addr)

		self.last_query = ""
		self.start_protocol()

	def start_protocol(self):
		raise NotImplementedError

	def query(self, query_string):
		"""
			sends a query to the server
		"""

		self.output = None

		self.connection.send(query_string)
		data = Packet(self.connection.recv(1024 * 4))

		self.last_query = query_string
		self.parse(data)

	def get_query(self, type):
		"""
			Gets the query string for the given type
		"""

		raise NotImplementedError

	def get_output(self):
		return self.output




