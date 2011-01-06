"""
:mod:`luckybot.plugin` - Plugin related classes
===============================================

You can find all plugin related classes in this module

.. module:: luckybot.plugin
   :synopsis: Plugin related classes
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.plugin.managment import Plugin, PluginManager, PluginException, TYPE_COMMAND,\
    TYPE_USER_EVENT, TYPE_SERVER_EVENT, TYPE_REGEXP_RAW, TYPE_REGEXP_MESSAGE, TYPE_TIMER
from luckybot.plugin.proxy import PluginProxy
