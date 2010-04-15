"""
:mod:`luckybot.ui.console` - Console logger UI
==============================================

UI which consists of a simple console logger

.. module:: luckybot.ui.console
   :synopsis: Console logger UI

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.ui import UI
from luckybot.ui.termcolor import colored

class ConsoleUI(UI):
	"""
		Represents the console UI, which simpels writes any data to
		stdout
	"""

	def data_in(self, data):
		print colored("<<< %s" % data, 'yellow')

	def data_out(self, data):
		print colored(">>> %s" % data, 'blue')
