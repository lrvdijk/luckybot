"""
:mod:`luckybot.language` - Multi language API
=============================================

This is our main bot controller, manages plugins, servers and more

.. module:: luckybot.bot
   :synopsis: Main controller class

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from ConfigParser import SafeConfigParser
from luckybot.irc import Format

class Language(object):
	"""
		Multi language class, reads a given ini file containing language
		entries.

		It also adds support for IRC Formatting, use {c} for the given
		color, {b} for bold, {u} for underline and {n} to clear
		all formatting
	"""

	def __init__(self, language, color=None, default_formatting={}):
		"""
			Initializes our language object

			:Args:
				* language (string): Which language to use
				* color (string): IRC Color to use for the {c} variable
				* default_formatting (dict): Dictionary which will
				  be added to the format function when retreiving
				  a language entry

			.. seealso::
				IRC Formatting: :class:`luckybot.irc.Format`
		"""

		self.language = language
		self.color = color if color else 'darkblue'
		self.parser = SafeConfigParser()
		self.languages_available = []
		self.format_vars = default_formatting

	def load_language(self, file):
		"""
			Loads the language entries in a given file for a given
			language

			:Args:
				* file (string): The ini file to load
				* language (string): Which language to load
		"""

		self.parser.read(file)
		self.languages_available = self.parser.sections()

	def __call__(self, key, *args, **kwargs):
		"""
			Gets a certain entry, and returns the formatted string

			:Args:
				* key (string): The language entry key
				* Further arguments or keyword arguments are passed to
				  the format function
		"""

		formatting = {
			'c': Format.color(self.color),
			'b': Format.bold(),
			'u': Format.underline(),
			'n': Format.normal()
		}

		format_vars = self.format_vars
		format_vars.update(kwargs)
		format_vars.update(formatting)

		if self.parser.has_section(self.language):
			if self.parser.has_option(self.language, key):
				return self.parser.get(self.language, key).format(*args, **format_vars).strip()
		elif self.parser.has_section('english'):
			if self.parser.has_option('english', key):
				return self.parser.get('english', key).format(*args, **format_vars).strip()
		else:
			if self.parser.has_option(self.languages_available[0], key):
				return self.parser.get(self.languages_available[0], key).format(*args, **format_vars).strip()

		return key


