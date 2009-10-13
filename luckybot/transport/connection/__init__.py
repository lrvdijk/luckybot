#
# LuckyBot5, a multiprotocol, extendable python IM bot.
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

class BaseConnection(object):
	"""
		Represents a connection to some host
	"""

	def __init__(self, family, type, protocol = None):
		self._family = family
		self._type = type

		if protocol != None:
			self.set_protocol(protocol)
		else:
			self.protocol = None

	def set_protocol(self, protocol):
		self.protocol = protocol
		self.protocol.set_connection(self)

	def open(self, addr):
		raise NotImplementedError

	def close(self):
		raise NotImplementedError

	def send(self, data):
		raise NotImplementedError

	def recv(self, length):
		raise NotImplementedError

class Connection(BaseConnection):
	"""
		A simple synchronous connection to some host
	"""

	def open(self, addr):
		"""
			Opens and creates a new socket object plus an IOChannel
			object, connecting to the given address

			@type addr: tuple
			@param addr: A tuple containing the address and port
		"""

		try:
			self._socket = socket.socket(self._family, self._type)
			self._socket.connect(addr)

			self.addr = addr
			self._fileno = self._socket.fileno()
		except socket.error, e:
			if e[0] in [EINPROGRESS, EALREADY, EWOULDBLOCK]:
				return
			else:
				raise socket.error, e

		self.connected = True

	def close(self):
		"""
			Closes the socket
		"""

		try:
			self._socket.close()
			del self._socket
			self._fileno = -1
			self.connected = False
		except socket.error, e:
			if e[0] in [ECONNRESET, ENOTCONN]:
				pass
			else:
				raise
		except AttributeError:
			pass

	def recv(self, length):
		"""
			Reads the number of bytes from the socket given by length

			@type length: int
			@param length: The number of bytes to read

			@rtype: string
			@return: The data received
		"""

		data = self._socket.recv(length)
		
		if data == "":
			raise socket.error((-1, 'Not connected to host'))

		return data

	def send(self, data):
		"""
			Sends data to the socket

			@type data: string
			@param data: The data to send
		"""

		self._socket.send(data)

	@property
	def socket(self):
		return self._socket

	@property
	def fileno(self):
		return self._fileno

	def __getattr__(self, name):
		"""
			Redirect calls to our socket object

			@type name: string
			@param name: Attribute name
		"""

		if hasattr(self, '_socket') and hasattr(self._socket, name):
			return getattr(self._socket, name)
		else:
			raise AttributeError, 'Undefined attribute %s' % name


class AsyncConnection(Connection):
	"""
		Class for multiple asynchrous connections
		Inspired by asyncore

		Haven't really tested this class yet
	"""

	def open(self, addr):
		super(AsyncConnection, self).open(addr)

		self.register_socket()

	def close(self):
		self.remove_socket()

		super(AsyncConnection, self).close()

	def register_socket(self):
		"""
			Adds this socket to the socket_map
		"""

		if not hasattr(AsyncConnection, 'socket_map') or AsyncConnection.socket_map == None:
			AsyncConnection.socket_map = {}

		AsyncConnection.socket_map[self._fileno] = self

	def remove_socket(self):
		"""
			Removes socket from the socket map
		"""

		if not hasattr(AsyncConnection, 'socket_map') or AsyncConnection.socket_map == None:
			AsyncConnection.socket_map = {}

		try:
			del AsyncConnection.socket_map[self._fileno]
		except:
			pass

	@classmethod
	def poll(self, timeout=0.0):
		"""
			Checks all sockets in socket_map and calls the event handlers
			if there's one
		"""

		if timeout is not None:
			# timeout is in milliseconds
			timeout = int(timeout*1000)

		pollster = select.poll()
		if hasattr(AsyncConnection, 'socket_map') and AsyncConnection.socket_map:
			for fd, obj in AsyncConnection.socket_map.items():
				flags = 0
				if obj.readable():
					flags |= select.POLLIN | select.POLLPRI
				if obj.protocol.writable():
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
				obj = AsyncConnection.socket_map.get(fd)
				if obj is None:
					continue

				if flags & (select.POLLIN | select.POLLPRI):
					obj.handle_read_event()
				if flags & select.POLLOUT:
					obj.handle_write_event()

	def handle_read_event(self):
		"""
			This checks if the current instance has an event handler
			for a read event and calls it if it exists
		"""

		if not self.connected:
			self.connected = True
			self.handle_connect_event()

		if hasattr(self.protocol, 'handle_read'):
			self.protocol.handle_read()

	def handle_write_event(self):
		"""
			This checks if the current instance has an event handler
			for a write/out event and calls it if it exists
		"""

		if not self.connected:
			self.connected = True
			self.handle_connect_event()

		if hasattr(self.protocol, 'handle_write'):
			self.protocol.handle_write()

	def handle_connect_event(self):
		"""
			This checks if the current instance has an event handler
			for a connect event and calls it if it exists
		"""

		if hasattr(self.protocol, 'handle_connect'):
			self.protocol.handle_connect()

	def handle_close_event(self):
		"""
			This checks if the current instance has an event handler
			for a close event and calls it if it exists
		"""

		try:
			if self.connected:
				self.iochannel.close()
		except:
			pass

		self.connected = False

		if hasattr(self.protocol, 'handle_close'):
			self.protocol.handle_close()

	def handle_error(self, type, value, traceback):
		"""
			Called when an error occurs
		"""

		if hasattr(self.protocol, 'handle_error'):
			self.protocol.handle_error(type, value, traceback)
		else:
			print 'Socket Error'

			print 'Type:', type
			print 'Value:', value
			print 'Traceback:'
			print traceback

