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

import gobject
from luckybot.connections.async import OutgoingPacket, AsyncConnection

class GlibConnection(AsyncConnection):
	"""
		This class represents a connection
		using gobject IOChannel to integrate with the main glib loop
	"""

	def __init__(self, family, type):
		"""
			Constructor initializes some vars
		"""

		super(GlibConnection, self).__init__(family, type)

		self._io_condition = 0
		self._watch_id = 0

	def open(self, addr):
		"""
			Opens and creates a new socket object plus an IOChannel
			object, connecting to the given address

			@type addr: tuple
			@param addr: A tuple containing the address and port
		"""

		super(GlibConnection, self).open(addr)

		self.iochannel = gobject.IOChannel(self._socket.fileno())
		self.iochannel.set_encoding(None)
		self.iochannel.set_buffered(False)
		self.iochannel.set_flags(self.iochannel.get_flags() | gobject.IO_FLAG_NONBLOCK)

		self._set_watch(gobject.IO_IN | gobject.IO_PRI | gobject.IO_ERR | gobject.IO_HUP)
		self.handle_connect_event()

	def close(self):
		"""
			Closes the socket
		"""

		self.iochannel.close()

		super(GlibConnection, self).close()

	def recv(self, length):
		"""
			Reads data from the socket

			@type length: int
			@param length: Number of bytes to read
		"""

		data = self.iochannel.read(length)

		if data == "":
			self.handle_close_event()
			return ''

		return data

	def send(self, data):
		"""
			Send data and add IO_OUT watch
		"""
		
		super(GlibConnection, self).send(data)
		self._add_condition(gobject.IO_OUT)

	def _remove_watch(self):
		"""
			Remove the IOChannel event handler
		"""

		gobject.source_remove(self._watch_id)
		self._watch_id = 0
		self._io_condition = 0

	def _set_watch(self, condition):
		"""
			Set the IOChannel event handler with a given condition

			@type condition: int
			@param condition: The conditions
		"""

		if self._watch_id != 0:
			self._remove_watch()

		self._io_condition = condition
		self._watch_id = self.iochannel.add_watch(condition, self._io_handler)

	def _add_condition(self, condition):
		"""
			Add an additional condition to the current handler

			@type condition: int
			@param condition: The condition to add
		"""

		if self._io_condition & condition == condition:
			return

		self._io_condition |= condition
		self._set_watch(self._io_condition)

	def _remove_condition(self, condition):
		if self._io_condition & condition == 0:
			return

		self._io_condition ^= condition
		self._set_watch(self._io_condition)

	def _io_handler(self, channel, condition):
		"""
			Our IO handler, this function will be called when we can perform
			i/o operations without blocking the GUI

			@type channel: gobject.IOChannel
			@param channel: The channel we're on

			@type condition: int
			@param condition: The condition(s) which apply for this call
		"""

		if (condition & (gobject.IO_IN | gobject.IO_PRI)) != 0:
			self.handle_read_event()

		if (condition & (gobject.IO_ERR | gobject.IO_HUP)) != 0:
			self.close()
			self.handle_close_event()

		if (condition & gobject.IO_OUT) != 0:
			self.handle_write_event()

			if not self.writeable():
				self._remove_condition(gobject.IO_OUT)

		return True
		
	def handle_write_event(self):
		"""
			Sends data through IO channel
		"""
		
		if self.send_queue:
			item = self.send_queue[0]
			item.sent(self.iochannel.write(item.read()))

			if item.is_complete():
				del self.send_queue[0]
				del item
