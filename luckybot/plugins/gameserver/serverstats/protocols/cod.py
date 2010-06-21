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
# $Id: cod.py 76 2009-05-19 14:06:14Z luckyluke56 $
#

from .. import Protocol
from ..protocol import Packet

class Cod4Protocol(Protocol):
	"""
		Protocol for Call of duty 4 and 5 servers
	"""

	QUERY_STATUS = "\xFF\xFF\xFF\xFFgetstatus\x00"

	def get_query(self, type):
		"""
			Gets the query string for certain info
		"""

		if type in ['info', 'players']:
			self.type = type
		else:
			self.type = 'info'

		return Cod4Protocol.QUERY_STATUS

	def parse(self, packet):
		"""
			Parses the received data from the server
		"""

		if self.type == 'info':
			pass
