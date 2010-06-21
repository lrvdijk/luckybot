#
# RCON Anywhere - http://www.rcon-anywhere.net
# Desktop tool
#
# Created by Lucas van Dijk (www.return1.net)
#
# Package serverstats
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA
#
# $Id: __init__.py 76 2009-05-19 14:06:14Z luckyluke56 $
#

import struct

class Packet(object):
	"""
		Represents a packet received from the server
	"""

	def __init__(self, data):
		"""
			Sets the data

			@type data: string
			@param data: The data received
		"""

		self.data = data
		self.length = len(data)
		self.offset = 0

	def get_remaining_length(self):
		return max(self.length - self.offset, 0)

	def set_offset(self, offset):
		"""
			Sets the offset if valid
		"""

		if offset >= 0 and offset < self.length:
			self.offset = offset

	def read_string(self, offset = -1):
		"""
			Reads a string from the given packet
			It loops through the data untill he finds a \x00 byte
		"""

		if offset != -1:
			self.set_offset(offset)

		the_string = ""

		while self.offset < self.length:
			if self.data[self.offset] == "\x00":
				self.offset += 1
				break

			the_string += self.data[self.offset]
			self.offset += 1

		return the_string

	def read_int(self, offset = -1):
		"""
			Reads a 4 byte signed int from the packet
		"""

		if offset != -1:
			self.set_offset(offset)

		data = struct.unpack_from('i', self.data, self.offset)[0]
		self.offset += struct.calcsize('i')

		return data

	def read_short(self, offset = -1):
		"""
			Reads a 2 byte unsigned short from the packet
		"""

		if offset != -1:
			self.set_offset(offset)

		data = struct.unpack_from('H', self.data, self.offset)[0]
		self.offset += struct.calcsize('H')

		return data

	def read_float(self, offset = -1):
		"""
			Reads a float from the packet
		"""

		if offset != -1:
			self.set_offset(offset)

		data = struct.unpack_from('f', self.data, self.offset)[0]
		self.offset += struct.calcsize('f')

		return data

	def read_byte(self, offset = -1, use_ord = False):
		"""
			Reads a single byte
		"""

		if offset != -1:
			self.set_offset(offset)

		data = ord(self.data[self.offset]) if use_ord else self.data[self.offset]
		self.offset += 1

		return data

	def read_ord(self, amount = 1, offset = -1):
		"""
			Reads a given amount of bytes and calls ord on it
		"""

		if offset != -1:
			self.set_offset(offset)

		the_string = ""
		while amount > 0:
			the_string += str(self.read_byte(use_ord=True))
			amount -= 1

		return the_string

	def unpack(self, format, offset = -1):
		"""
			unpacks the data according the given format
			See python docs for struct module
		"""

		if offset != -1:
			self.set_offset(offset)

		data = struct.unpack(format, self.data, self.offset)
		self.offset += struct.calcsize(format)

		return data

	def skip(self, amount):
		"""
			Skip a given amount of bytes
		"""

		self.offset = min(self.length - 1, self.offset + amount)

	def __str__(self):
		return self.data



