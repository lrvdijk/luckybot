"""
:mod:`luckybot.path` - Path helper functions
============================================

This module provides some helper functions to get a specific path

.. module:: luckybot.path
   :synopsis: Provides some path helper functions

.. moduleauthor:: Lucas van Dijk <info@lucasvandijk.nl>
"""

import os

__settingsdir = os.path.expanduser('~/.luckybot')

try:
	root = __file__

	if os.path.islink(root):
		root = os.path.realpath(root)

	root = os.path.dirname(os.path.abspath(root))
except:
	print "Could not determine path!"
	sys.exit(1)

__basedir = root

if not os.path.exists(__settingsdir):
	os.mkdir(__settingsdir)

def user_path(*elems):
	return os.path.join(__settingsdir, *elems)

def base_path(*elems):
	return os.path.join(__basedir, *elems)
