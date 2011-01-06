"""
:mod:`stats.db` - SQLAlchemy database schemas
=============================================

This module contains table definitions for the statistics plugin, using
sqlalchemy

.. module:: stats.db
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.types import Integer, Unicode, String, UnicodeText, Boolean, DateTime
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

import datetime

class Server(Base):
	"""
		Represents an IRC Server
	"""

	__tablename__ = 'stats_servers'

	id = Column(Integer(unsigned=True), primary_key=True)
	hostname = Column(String(100), nullable=False, unique=True)

class Channel(Base):
	"""
		Represents a channel on an IRC server
	"""

	__tablename__ = 'stats_channels'

	id = Column(Integer(unsigned=True), primary_key=True)
	server_id = Column(Integer(unsigned=True), ForeignKey('stats_servers.id'))
	name = Column(String(100), nullable=False, unique=True)

	server = relationship(Server, backref='channels')

class User(Base):
	"""
		Represents a user on a channel
	"""

	__tablename__ = 'stats_users'

	id = Column(Integer(unsigned=True), primary_key=True)
	channel_id = Column(Integer(unsigned=True), ForeignKey('stats_channels.id'))
	nick_id = Column(Integer(unsigned=True), ForeignKey('stats_nicks.id'))
	is_bot = Column(Boolean, default=False)

	channel = relationship(Channel, backref='users')

class Hostname(Base):
	"""
		Represents a user with a specific hostname
	"""

	__tablename__ = 'stats_hostnames'

	id = Column(Integer(unsigned=True), primary_key=True)
	user_id = Column(Integer(unsigned=True), ForeignKey('stats_users.id'))
	lines = Column(Integer(unsigned=True), default=0)
	lines_morning = Column(Integer(unsigned=True), default=0)
	lines_noon = Column(Integer(unsigned=True), default=0)
	lines_evening = Column(Integer(unsigned=True, default=0)
	lines_night = Column(Integer(unsigned=True, default=0)
	words = Column(Integer(unsigned=True, default=0)
	characters = Column(Integer(unsigned=True, default=0)
	joins = Column(Integer(unsigned=True, default=1)
	actions = Column(Integer(unsigned=True, default=0)

	user = relationship(User, backref='hostnames')

class Nickname(Base):
	"""
		Represents a nickname
	"""

	__tablename__ = 'stats_nicks'

	id = Column(Integer(unsigned=True), primary_key=True)
	user_id = Column(Integer(unsigned=True), ForeignKey('stats_users.id'))
	nickname = Column(String(50), nullable=False)
	is_bot = Column(Boolean, default=False)

	user = relationship(User, backref='nicks')

class LastMessage(Base):
	"""
		Last message of a user
	"""

	__tablename__ = 'stats_last_messages'

	id = Column(Integer(unsigned=True), primary_key=True)
	user_id = Column(Integer(unsigned=True), ForeignKey('stats_users.id'))
	message = Column(UnicodeText, nullable=False)
	date = Column(DateTime, nullable=False)

	user = relationship(User, backref='last_message')

class Activity(Base):
	__tablename__ = 'stats_activity'

	channel_id = Column(Integer(unsigned=True), ForeignKey('stats_channels.id'))
	lines = Column(Integer(unsigned=True), default=0)
	date = column(DateTime, nullable=False)

	channel = relationship(Channel, backref='activity')
