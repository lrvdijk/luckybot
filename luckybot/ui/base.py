"""
:mod:`luckybot.ui.base` - LuckyBot UI Base Classes
==================================================

This module contains base classes for any UI. In this way it's possible
to use any GUI toolkit you want (if you write a specific GUI class for
your favoritie toolkit)

.. module:: luckybot.ui.base
   :synopsis: Provides the base UI classes

.. moduleauthor:: Lucas van Dijk <info@lucasvandijk.nl>
"""

from abc import ABCMeta, abstractmethod

class UI(object):
	"""
		The base class for any GUI
	"""

	__metaclass__ = ABCMeta

	def __init__(self, bot):
		pass

	@abstractmethod
	def start(self, bot):
		pass

	@abstractmethod
	def data_in(self, data):
		pass

	@abstractmethod
	def data_out(self, data):
		pass
