"""
Gameserver Database Tables
==========================

This module contains the database tables required for the Gameserver plugin

.. module:: gameserver.db
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Server(Base):
	__tablename__ = 'gameserver_servers'

	id = Column(Integer(unsigned=True), primary_key=True)
	name = Column(String(50), unique=True)
	game = Column(String(30))
	ip = Column(String(50))
	port = Column(Integer)
	is_approved = Column(Boolean)

	def __init__(self, name, game, ip, port, is_approved=False):
		self.name = name
		self.game = game
		self.ip = ip
		self.port = port
		self.is_approved = is_approved

	def __repr__(self):
		return "Server({0.name}, {0.game}, {0.ip}:{0.port}, {0.is_approved})".format(self)
