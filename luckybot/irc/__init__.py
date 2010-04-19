"""
:mod:`luckybot.irc` - IRC Helper classes
========================================

This module provides some helper classes for IRC specific things like
formatting.

.. module:: luckybot.irc
   :synopsis: IRC Helper classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""
import re

class Format(object):
	"""
		This class can be used to format messages sent to the IRC server
	"""

	black = 1
	darkblue = 2
	green = 3
	red = 4
	darkred = 5
	purple = 6
	orange = 7
	yellow = 8
	lightgreen = 9
	aqua = 10
	lightblue = 11
	blue = 12
	violet = 13
	grey = 14
	lightgrey = 15
	white = 16

	@classmethod
	def color(self, color):
		"""
			Add a color to a message

			:Args:
				* color (string): The name of the color
		"""
		try:
			code = getattr(self, color)
		except:
			code = 1

		return "\x03%02.f" % (code)

	@classmethod
	def normal(self):
		"""
			Reset to the default color
		"""
		return "\x0F"

	@classmethod
	def bold(self):
		"""
			Make the text bold
		"""
		return "\x02"

	@classmethod
	def reverse(self):
		"""
			Make the text italic (doet not work for all clients)
		"""
		return "\x16"

	@classmethod
	def underline(self):
		"""
			Underline the text
		"""
		return "\x1F"

	@classmethod
	def remove(self, string):
		"""
			Remove all format in the given string

			:Args:
				* string (string): The string to cleanup
		"""

		regexp = re.compile('(?:(?:\x03[0-9]+)|(?:\x0F|\x02|\x16|\x1F))', re.I)

		return regexp.sub('', string)
