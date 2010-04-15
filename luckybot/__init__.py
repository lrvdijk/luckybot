"""
:mod:`luckybot` - FLexible IRC Bot
==================================

LuckyBot is a multipurpose IRC Bot, with a LOT of features. It runs each
socket in a seperate process for performance and stability. Beside that,
it also features a very flexible plugin sytem, which are easy to create.

Features
--------

* Multiserver and multichannel
* Easy and flexible plugin system
* Built-in, hostbased authentication system
* Multilanguage API for plugins
* A lot of builtin plugins

.. module:: luckybot.irc.protocol.handler
   :synopsis: IRC Protocol handler

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

__version__ = "5.0alpha"
from luckybot.path import user_path, base_path

