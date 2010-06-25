"""
:mod:`luckybot.connections` - Socket helper classes
===================================================

This module contains some basic socket abstaction classes, to make
sockets more flexible.

.. module:: luckybot.connections
   :synopsis: Socket helper classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from abc import ABCMeta, abstractmethod, abstractproperty
import socket
import traceback

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
	 ENOTCONN, ESHUTDOWN, EINTR, EISCONN, errorcode

class BaseConnection(object):
	"""
		Represents a connection to some host
	"""

	__metaclass__ = ABCMeta

	def __init__(self, type):
		self.type = type

	@abstractmethod
	def open(self, addr):
		pass

	@abstractmethod
	def close(self):
		pass

	@abstractmethod
	def send(self, data):
		pass

	@abstractmethod
	def recv(self, length):
		pass

	@abstractproperty
	def is_alive(self):
		"""
			Checks if the connection is still alive

			:Returns:
				A bool, True when still connected, else False
		"""
		pass

class Connection(BaseConnection):
	"""
		A simple synchronous connection to some host
	"""

	def open(self, addr):
		"""
			Opens and creates a new socket object, connecting to the given address

			:Args:
				* addr (tuple): A tuple containing the address and port
		"""

		for res in socket.getaddrinfo(addr[0], addr[1], socket.AF_UNSPEC, self.type):
			af, socktype, proto, canonname, sa = res
			try:
				self._socket = socket.socket(af, socktype, proto)
			except socket.error, msg:
				self._socket = None
				traceback.print_exc()
				continue
			try:
				self._socket.connect(sa)
			except socket.error, msg:
				self._socket.close()
				self._socket = None
				traceback.print_exc()
				continue
			break

		if self._socket == None:
			raise socket.error((-1, "Could not open socket"))

		self.connected = True
		self._fileno = self._socket.fileno()

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

			:Args:
				* length (int): The number of bytes to read

			:Returns: The data read
		"""

		data = self._socket.recv(length)

		if data == "":
			raise socket.error((-1, 'Not connected to host'))

		return data

	def send(self, data):
		"""
			Sends data to the socket

			:Args:
				* data (string): The data to send
		"""

		return self._socket.send(data)

	@property
	def socket(self):
		return self._socket

	@property
	def fileno(self):
		return self._fileno

	@property
	def is_alive(self):
		"""
			Checks if the connection is still alive

			:Returns:
				A bool, True when still connected, else False
		"""
		return self.connected

	def __getattr__(self, name):
		"""
			Redirect calls to our socket object
		"""

		if hasattr(self, '_socket') and hasattr(self._socket, name):
			return getattr(self._socket, name)
		else:
			raise AttributeError, 'Undefined attribute %s' % name







