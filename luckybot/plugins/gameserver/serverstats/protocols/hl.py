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
# $Id: hl.py 76 2009-05-19 14:06:14Z luckyluke56 $
#

from .. import Protocol
from ..protocols import Packet
import struct
import bz2

def sort_dict(adict):
	keys = adict.keys()
	keys.sort()
	return map(adict.get, keys)

class SourceProtocol(Protocol):
	"""
		Represents the protocol for source servers
	"""

	QUERY_CHALLENGE = "\xFF\xFF\xFF\xFF\x57"
	QUERY_INFO = "\xFF\xFF\xFF\xFF\x54Source Engine Query"
	QUERY_PLAYERS = "\xFF\xFF\xFF\xFF\x55"
	QUERY_RULES = "\xFF\xFF\xFF\xFF\x56"

	def start_protocol(self):
		self.challenge = struct.pack('i', -1)

	def get_query(self, type):
		"""
			Gets the query for the given type
			Available types are:
			  * challenge - The get the challenge
			  * info - To get the basic server info
			  * players - To get player data
			  * rules - To get all server rules

			@type type: string
			@param type: The query type
		"""

		if type == 'challenge':
			return SourceProtocol.QUERY_CHALLENGE
		elif type == 'info':
			return SourceProtocol.QUERY_INFO
		elif type == 'players':
			return SourceProtocol.QUERY_PLAYERS + self.challenge
		elif type == 'rules':
			return SourceProtocol.QUERY_RULES + self.challenge
		else:
			return SourceProtocol.QUERY_INFO

	def parse(self, packet):
		"""
			Called when a packet arrives
		"""

		# Check for multipacket
		header = packet.read_int()

		if header == -2:
			# Multipacket response
			request_id = packet.read_int()

			# check if the packet is compressed
			compressed = request_id < 0

			packets = {}
			packet_no = packet.read_short()
			num_packets = packet_no & 0x0F

			for i in range(num_packets):
				# Receive rest of the packages
				if i != 0:
					packet = Packet(self.connection.recv(1024 * 4))

				packet_no = packet.read_short(8)
				packet_num = packet_no & 0xF0

				# if compressed, 2 extra fields are added
				if compressed:
					uncompressed_length = packet.read_int()
					crc = packet.read_int()

				# add it to the packet list
				packets[packet_num] = str(packet)[packet.offset:]

			packets = sort_dict(packets)
			data = ''.join(packets)

			if compressed:
				data = bz2.decompress(data)

			self.parse(Packet(data))
		else:
			# Check what type of packet we have
			query = packet.read_byte()

			if query == 'A':
				# Challenge response
				self.challenge = struct.pack('i', packet.read_int())

				if not self.last_query or self.last_query != SourceProtocol.QUERY_CHALLENGE:
					# We received this response while we didn't request it
					# Send previous query again with new challenge

					self.query("\xFF\xFF\xFF\xFF" + self.last_query[4] + self.challenge)
			elif query == 'I':
				# Info response
				info = {}

				info['version'] = packet.read_ord()
				info['server_name'] = packet.read_string()
				info['map'] = packet.read_string()
				info['game_directory'] = packet.read_string()
				info['game_description'] = packet.read_string()
				info['appid'] = packet.read_short()
				info['num_players'] = packet.read_ord()
				info['max_players'] = packet.read_ord()
				info['bot_players'] = packet.read_ord()
				info['dedicated'] = packet.read_byte()
				info['os'] = packet.read_byte()
				info['password'] = packet.read_ord()
				info['secure'] = packet.read_ord()
				info['gameversion'] = packet.read_string()

				self.server.info = info
			elif query == 'D':
				# Players response

				num_players = packet.read_ord()
				players = {}

				if num_players > 0:
					while packet.get_remaining_length():
						index = packet.read_ord()
						player = {
							'name': packet.read_string(),
							'kills': packet.read_int(),
							'time_connected': packet.read_float()
						}

						players[index] = player

				self.server.players = sort_dict(players)
			elif query == 'E':
				packet.skip(2)

				rules = {}
				rule = packet.read_string()
				while rule:
					rules[rule] = packet.read_string()

					rule = packet.read_string()

				self.server.rules = rules
			else:
				raise GameserverException, "Unsupported packet received, sure it's a source server?"




