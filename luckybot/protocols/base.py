"""
:mod:`luckybot.protocols.base` - Protocol base classes
======================================================

Some required classes for handling protocols.

.. module:: luckybot.protocols.base
   :synopsis: Protocol base classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

class Message(object):
	"""
		This class represents a line from the server
	"""

	RAW_MESSAGE = 0
	USER_MESSAGE = 1
	SERVER_MESSAGE = 2

	def __init__(self, type, raw, *args, **kwargs):
		self.data = kwargs
		self.data['type'] = type
		self.data['raw'] = raw

	def __getattr__(self, name):
		if name in self.data:
			return self.data[name]
		else:
			raise AttributeError, "No attribute named %s" % name

	def __str__(self):
		return self.raw
