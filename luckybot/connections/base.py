"""
:mod:`luckybot.connections.base` - Base classes for connections
===============================================================

This module contains the base class which other types of connections
should subclass.

.. module:: luckybot.connections.base
   :synopsis: Base class for connections
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from abc import ABCMeta, abstractmethod
from luckybot.signals import SignalEmitter

class BaseConnection(SignalEmitter):
	"""
		Base class for any type of connection

		This also implements an simple event system, and the subclass
		is responsible for emitting the right signals.

		Minimum required available events:
		* connected
		* data_in
		* data_out
		* closed

		Emit them when it's the right time

		.. seealso
		    :mod:`luckybot.signals`
	"""

	available_events = ('connected', 'data_in', 'data_out', 'closed')

	def __init__(self, *args, **kwargs):
		SignalEmitter.__init__(self)
		self.info = kwargs

	@abstractmethod
	def connect(self):
		"""
			Connects to the server
		"""

	@abstractmethod
	def recv(self):
		"""
			Receive data from the server
		"""

	@abstractmethod
	def send(self, line):
		"""
			Send data to the server
		"""

	@abstractmethod
	def close(self):
		"""
			Close connection to the server
		"""



