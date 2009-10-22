#
# LuckyBot5, a highly extendable IRC bot written in python
# (c) Copyright 2008 by Lucas van Dijk
# http://www.return1.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA
#
# $Id$ 
#

import glib
from ConfigParser import SafeConfigParser
import re
from luckybot import path

class LuckyBot(object):
	"""
		Main application controller
	"""
	
	def __init__(self):
		"""
			Constructor, initializes some basic bot functionality
		"""
		
		# Load settings
		self.settings = SafeConfigParser()
		if os.path.exists(path.get_personal_file('settings.ini')):
			self.settings.read([path.get_personal_file('settings.ini')])
		else:
			self.settings.read(path.get_base_path('data', 'settings.ini'))
			
		# Create a glib main loop
		self.loop = glib.MainLoop()
	
	def get_servers(self):
		"""
			Reads the configuration file, and checks which servers
			to connect to
		"""

		servers = []
		sections = self.settings.sections()
		regexp = re.compile(r'^Server(\d+)$', re.I)

		for section in sections:
			match = regexp.match(section)
			if match:
				config = {}
				for option in self.settings.options(section):
					config[option] = self.settings.get(section, option)
				servers.append(config)

		return servers
	
	def start(self):
		"""
			Starts the Glib mainloop, opens the connections to the servers
			and connects to the connection events.
		"""
		
		
	

bot = LuckyBot()
