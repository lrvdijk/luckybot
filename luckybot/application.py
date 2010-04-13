"""
:mod:`luckybot.application` - Application entry point
-----------------------------------------------------

Application entry class, from here everything is set in motion

.. module:: luckybot.application
   :synopsis: Application entry point

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

import optparse
import sys
from luckybot import base_path, user_path, __version__, bot
from luckybot.ui import UI

class Application(object):
	"""
		Main luckybot application class
	"""

	def __init__(self):
		"""
			Constructor, initializes our option parser
		"""
		self.parser = optparse.OptionParser(usage="%prog [options]",
			version="LuckyBot v%s" % __version__)
		self.parser.add_option('-u', '--ui', dest="ui",
			help="GUI type: currently only console supported",
			default="console")

		self.ui = None

	def run(self):
		"""
			Run the application, loads the GUI
		"""

		options, args = self.parser.parse_args(sys.argv)

		self.ui = UI.get(options.ui)
		bot.start()

app = Application()
