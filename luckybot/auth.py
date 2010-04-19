"""
:mod:`luckybot.auth` - Authentication manager
=============================================

This module provides authentication functionality to our bot.
Authentication is based on the hostname of the user.

.. module:: luckybot.auth
   :synopsis: Authentication manager

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

class Authentication(object):
	"""
		This class provides functionality to authenticate a user
	"""

	def __init__(self, groups, users):
		"""
			Creates a new Authentication object

			:Args:
				* groups (dict): Dictionary of group names with their ranking as value
				* users (dict): Dictionary of hostnames and group as value
		"""

		self.groups = groups
		self.users = users

	def is_allowed(self, hostname, group):
		"""
			Checks if a certain user is in a group, or the group
			given is lower ranked than the group the user is in

			:Args:
				* hostname (string): The user hostname
				* group (string): Minium required group
		"""
		hostname = hostname.lower()
		group = group.lower()

		if not hostname in self.users:
			print 1
			return False

		if not group in self.groups:
			print 2
			return False

		if not self.users[hostname] in self.groups:
			print 3
			return False

		user_group = self.groups[self.users[hostname]]

		return self.groups[group] >= user_group
