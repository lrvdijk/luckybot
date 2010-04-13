"""
:mod:`luckybot.application` - Application entry point
-----------------------------------------------------

Application entry class, from here everything is set in motion

.. module:: luckybot.application
   :synopsis: Application entry point

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

import optparse
from luckybot import base_path, user_path, __version__
from gettext import gettext as _
from luckybot.ui import UI

class Application(object):
	"""
		Main luckybot application class
	"""

	def __init__(self):
		"""
			Constructor, initializes our option parser
		"""
		self.parser = optparser.OptionParser(usage="%prog [options]",
			version="LuckyBot v%s" % __version__)
		self.parser.add_option('-d', '--deamon', dest="deamon", action="store_true",
			help=_("Create a daemon, instead of running in terminal"),
			default=False)
		self.parser.add_option('-u', '--ui', dest="ui",
			help=_("GUI type: currently only console supported"),
			default="console")

	def run(self, argv):
		"""
			Run the application, loads the GUI
		"""

		options, args = self.parser.parse_args(sys.argv)

		UI.get(options.ui)

app = Application()
