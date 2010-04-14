"""
:mod:`luckybot.plugin.decorators` - Plugin Decorators
-----------------------------------------------------

This module provides some decorators used to tag functions as a callback
for a specifick IRC event

.. module:: luckybot.plugin.decorators
   :synopsis: Plugin Decorators

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

TYPE_COMMAND = 1
TYPE_USER_EVENT = 2
TYPE_SERVER_EVENT = 3
TYPE_REGEXP_RAW = 4
TYPE_REGEXP_MESSAGE = 5

def command(command):
	"""
		Decorator which makes a given function act as a command
		callback when registered to the pluginhandler

		:Args:
			* command (string|list|tuple): The command(s) to where it should respond to
	"""

	def function_modifier(func):
		func.type = TYPE_COMMAND
		func.command = [command] if type(command) is str else command
		func.im_class.has_commands = True

		return func

	return function_modifier

def userevent(event):
	"""
		Decorator which makes a given function act as a callback
		for a given user event on IRC, like JOIN, NICK, or QUIT, which
		means new user joined, nickchange, and a user quit

		:Args:
			* event (string|list|tuple): Name of the IRC event(s) to watch for
	"""

	def function_modifier(func):
		func.type = TYPE_USER_EVENT
		func.event = [event] if type(event) is str else event
		func.im_class.has_event = True

		return func

	return function_modifier

def serverreply(code):
	"""
		Decorator which makes a given function act as a callback
		for a server reply code.

		.. seealso::
			http://irchelp.org/irchelp/rfc/chapter6.html

		:Args:
			* event (int|list|tuple): Reply codes of the IRC replies to watch for
	"""

	def function_modifier(func):
		func.type = TYPE_SERVER_EVENT
		func.event = [code] if type(code) is int else code
		func.im_class.has_event = True

		return func

	return function_modifier
