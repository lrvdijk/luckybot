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

from abc import ABCMeta, abstractmethod
import socket

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
	 ENOTCONN, ESHUTDOWN, EINTR, EISCONN, errorcode

class BaseConnection(object):
	"""
		Represents a connection to some host
	"""
	
	__metaclass__ = ABCMeta

	def __init__(self, family, type):
		self._family = family
		self._type = type
	
	@abstractmethod
	def open(self, addr):
		pass
	
	@abstractmethod	
	def close(self):
		pass
	
	@abstractmethod
	def send(self, data):
		pass
	
	@absractmethod
	def recv(self, length):
		pass

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

		return self._socket.send(data)

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

