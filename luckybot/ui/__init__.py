"""
:mod:`luckybot.ui` - LuckyBot UI Classes
==========================================

This module contains base classes for any UI. In this way it's possible
to use any GUI toolkit you want (if you write a specific GUI class for
your favoritie toolkit)

.. module:: luckybot.ui
   :synopsis: Provides the base UI classes

.. moduleauthor:: Lucas van Dijk <info@lucasvandijk.nl>
"""

from abc import ABCMeta, abstractmethod

class UI(object):
	"""
		The base class for any GUI
	"""

	__metaclass__ = ABCMeta

	@classmethod
	def get(cls, type):
		"""
			Searches for a sub UI class, which matches the given type

			:Args:
				* type (string): The UI type
		"""

		subclasses = UI.__subclasses__()
		for sub in subclasses:
			if sub.__name__.lower == ("%sui" % type).lower():
				return sub

		return None

	@abstractmethod
	def data_in(self, data):
		pass

	@abstractmethod
	def data_out(self, data):
		pass
