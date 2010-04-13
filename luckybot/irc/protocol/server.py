"""
:mod:`luckybot.irc.protocol.server` - IRC Server handling
-----------------------------------------------------------

This module provides a class from, which you can access all server
data, and, if it's connected, the connection it self.

.. module:: luckybot.irc.protocol.server
   :synopsis: IRC Server handling

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.irc.handler import ProtocolHandler

class Server(object):
	"""
		Represents an IRC server
	"""

	def __init__(self, *args, **kwargs):
		"""
			Constructor, sets the server info.

			:Args:
				* Argument names should be
				  the same as in the directives for the [Server] section in
				  the ini file
		"""

		self.info = kwargs
		self.connection = None

	def connect(self):
		pass
