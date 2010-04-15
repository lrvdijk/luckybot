"""
:mod:`luckybot.plugin.decorators` - Plugin Decorators
=====================================================

This module provides some decorators used to tag functions as a callback
for a specifick IRC event

.. module:: luckybot.plugin.decorators
   :synopsis: Plugin Decorators

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.plugin import TYPE_COMMAND, TYPE_USER_EVENT, TYPE_SERVER_EVENT, \
	TYPE_REGEXP_RAW, TYPE_REGEXP_MESSAGE

def command(command):
	"""
		Decorator which makes a given function act as a command
		callback when registered to the pluginhandler

		:Args:
			* command (string|list|tuple): The command(s) to where it should respond to
	"""

	def function_modifier(func):
		func.handler_type = TYPE_COMMAND
		func.command = [command] if type(command) is str else command

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
		func.handler_type = TYPE_USER_EVENT
		func.event = [event] if type(event) is str else event

		return func

	return function_modifier

def serverevent(code):
	"""
		Decorator which makes a given function act as a callback
		for a server reply code.

		.. seealso::
			http://irchelp.org/irchelp/rfc/chapter6.html

		:Args:
			* event (int|list|tuple): Reply codes of the IRC replies to watch for
	"""

	def function_modifier(func):
		func.handler_type = TYPE_SERVER_EVENT
		func.event = [code] if type(code) is int else code

		return func

	return function_modifier

def regexpraw(pattern, modifiers=0):
	"""
		Decorator which makes sure when the given regexp matches
		an incoming message from the server. The regexp will be matched
		against the raw line from the server

		.. seealso::
			Decorator :function:`regexpmessage`

		:Args:
			* pattern (string): The regexp pattern
			* modifiers (int): Pattern modifiers, default 0
	"""

	def function_modifier(func):
		func.handler_type = TYPE_REGEXP_RAW
		func.pattern = pattern
		func.modifiers = modifiers

		return func

	return function_modifier

def regexpmessage(pattern, modifiers=0):
	"""
		Decorator which makes sure when the given regexp matches
		an incoming message from a certain user. The regexp will be matched
		against the message sent by the user.

		.. seealso::
			Decorator :function:`regexpmessage`

		:Args:
			* pattern (string): The regexp pattern
			* modifiers (int): Pattern modifiers, default 0
	"""

	def function_modifier(func):
		func.handler_type = TYPE_REGEXP_MESSAGE
		func.pattern = pattern
		func.modifiers = modifiers

		return func

	return function_modifier
