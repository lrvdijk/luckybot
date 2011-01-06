"""
RSS Reader database tables
==========================

This module contains the database tables required for the RSS plugin

.. module:: rssreader.db
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Notification(Base):
	__tablename__ = 'twitter_notifications'

	id = Column(Integer(unsigned=True), primary_key=True)
	type = Column(String(10))
	name = Column(String(50))
	server = Column(String(100))
	channel = Column(String(50))
	last_check = Column(DateTime(timezone=True))
	is_approved = Column(Boolean)

	def __repr__(self):
		return "Notification({0.type}, {0.name}, {0.is_approved})".format(self)
