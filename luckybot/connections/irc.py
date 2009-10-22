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
	
	def __init__(self, username, password, invisible=True)
		"""
			Constructor, sets some members
		"""
		
		gobject.GObject.__init__(self)
		GlibConnection.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
		
		self.username = username
		self.password = password
		self.invisible = invisible

