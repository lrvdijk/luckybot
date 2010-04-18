"""
RSS Reader database tables
==========================

This module contains the database tables required for the RSS plugin

.. module:: rss.db
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Feed(Base):
	__tablename__ = 'rss_feeds'

	id = Column(Integer(unsigned=True), primary_key=True)
	name = Column(String(50))
	url = Column(String(255))
	is_approved = Column(Boolean)
	register_as_command = Column(Boolean)

	def __init__(self, name, url, is_approved=False, register_as_command=False):
		self.name = name
		self.url = url
		self.is_approved = is_approved
		self.register_as_command = register_as_command

	def __repr__(self):
		return "Feed({0.name}, {0.url}, {0.is_approved}, {0.register_as_command})".format(self)
