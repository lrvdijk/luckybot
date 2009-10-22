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
import select

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
	 ENOTCONN, ESHUTDOWN, EINTR, EISCONN, errorcode

class OutgoingPacket(object):
	"""
		This class represents data to be asyncrhously sent

		This class is used to track how many of the packet is sent, so we
		can track if we need to sent more of this packet
	"""

	def __init__(self, data):
		self.data = data
		self.length = len(data)
		self._sent = 0

	def read(self, length = 2048):
		if length != None:
			return self.data[self._sent:][0:length]

		return self.data[self._sent:]

	def sent(self, bytes):
		self._sent += bytes

	def is_complete(self):
		return self._sent >= self.length

	def __str__(self):
		return self.data.encode('utf-8')

	def __repr__(self):
		return 'OutgoingPacket object with data: %s' % self.data

class AsyncConnection(Connection):
	"""
		Class for multiple asynchrous connections
		Inspired by asyncore

		Haven't really tested this class yet
	"""
	
	def __init__(self, af, type):
		"""
			Calls super constructor, and inits the send queue
		"""
		Connection.__init__(self, af, type)
		
		self.send_queue = []

	def open(self, addr):
		super(AsyncConnection, self).open(addr)

		self.register_socket()

	def close(self):
		self.remove_socket()

		super(AsyncConnection, self).close()
		
	def send(self, data):
		"""
			Adds the data to the send queue, and will be sent to the 
			server when the socket is ready for it
		"""
		
		self.send_queue.append(OutgoingPacket(data))

	def register_socket(self):
		"""
			Adds this socket to the socket_map
		"""

		if not hasattr(AsyncConnection, 'socket_map') or not AsyncConnection.socket_map:
			AsyncConnection.socket_map = {}

		AsyncConnection.socket_map[self._fileno] = self

	def remove_socket(self):
		"""
			Removes socket from the socket map
		"""

		if not hasattr(AsyncConnection, 'socket_map') or not AsyncConnection.socket_map:
			AsyncConnection.socket_map = {}

		try:
			del AsyncConnection.socket_map[self._fileno]
		except:
			pass
	
	def readable(self):
		"""
			We assume if a socket is connected, it's readable
		"""
		
		return self.connected
	
	def writeable(self):
		"""
			If there's anything in the send queue, wer're ready
			for writing
		"""
		
		return self.connected and self.send_queue

	@classmethod
	def poll(cls, timeout=0.0):
		"""
			Checks all sockets in socket_map and calls the event handlers
			if there's one
		"""

		if timeout is not None:
			# timeout is in milliseconds
			timeout = int(timeout*1000)

		pollster = select.poll()
		if hasattr(cls, 'socket_map') and cls.socket_map:
			for fd, obj in cls.socket_map.items():
				flags = 0
				if obj.readable():
					flags |= select.POLLIN | select.POLLPRI
				if obj.writable():
					flags |= select.POLLOUT
				if flags:
					# Only check for exceptions if object was either readable
					# or writable.
					flags |= select.POLLERR | select.POLLHUP | select.POLLNVAL
					pollster.register(fd, flags)
			try:
				r = pollster.poll(timeout)
			except select.error, err:
				if err[0] != EINTR:
					raise
				r = []
			for fd, flags in r:
				obj = cls.socket_map.get(fd)
				if obj is None:
					continue
				
				if not obj.connected:
					obj.handle_connect_event()
				if flags & (select.POLLIN | select.POLLPRI):
					obj.handle_read_event()
				if flags & select.POLLOUT:
					obj.handle_write_event()

	def handle_read_event(self):
		"""
			This checks if the current instance has an event handler
			for a read event and calls it if it exists
		"""

	def handle_write_event(self):
		"""
			This checks if the current instance has an event handler
			for a write/out event and calls it if it exists
		"""
		
		if self.send_queue:
			item = self.send_queue[0]
			item.sent(self._socket.send(item.read()))

			if item.is_complete():
				del self.send_queue[0]
				del item

	def handle_connect_event(self):
		"""
			This checks if the current instance has an event handler
			for a connect event and calls it if it exists
		"""

	def handle_close_event(self):
		"""
			This checks if the current instance has an event handler
			for a close event and calls it if it exists
		"""
		
		self.close()

	def handle_error(self, type, value, traceback):
		"""
			Called when an error occurs
		"""
		
		print 'Socket Error'

		print 'Type:', type
		print 'Value:', value
		print 'Traceback:'
		print traceback
