"""
:mod:`luckybot.signals` - Signal emitting and listening system
==============================================================

This module contains some classes used for setting up an event system.

.. module:: luckybot.signals
   :synopsis: Event related classes
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from abc import ABCMeta

class SignalException(Exception):
	pass

class SignalEmitter(object):
	__metaclass__ = ABCMeta

	available_events = ()

	def __init__(self):
		self.listeners = {}

	def add_listener(self, name, callback, userdata=None):
		"""
			Adds a listener function for a specific event, or multiple.

			:Args:
				* name (string): Name of the event
				* callback (function): The callback function
				* userdata (mixed): Any optional userdata
		"""

		if name in self.available_events:
			if not name in self.listeners:
				self.listeners[name] = []

			self.listeners[name].append((callback, userdata))
		else:
			raise SignalException, "Signal name does not exists"

	def emit_signal(self, name, *args, **kwargs):
		"""
			Calls all listeners for a specific signal

			:Args:
				* name (string): Signal name
		"""

		if name in self.listeners:
			for callback, userdata in self.listeners[name]:
				if userdata:
					kwargs['userdata'] = userdata

				callback(self, *args, **kwargs)

