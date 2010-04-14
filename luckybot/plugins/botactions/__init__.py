"""
Bot actions plugin
------------------

This plugin provides some basic actions for the bot like joining,
leaving changing nick etc.

.. module:: botactions
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.plugin import Plugin
from luckybot.plugin.decorators import command

class BotActions(Plugin):
	PLUGIN_INFO = {
		'author': 'Lucas van Dijk',
		'version': '0.1',
		'description': 'Some basic bot actions like join, part etc'
	}

	@command(['help', 'info'])
	def help(self, event):
		"""
			Displays some bot information
		"""

		event.channel.pm("LuckyBot v5 - Created by Lucas van Dijk")
