"""
System Information
==================

This plugin retreives some information about the system the bot
is running on.

.. module:: sysinfo
.. moduleauthor:: Wiebe Verweij <info@wiebelt.nl>
.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from luckybot.plugin import Plugin
from luckybot.plugin.decorators import command
from luckybot.protocols.irc import Format

import os
from ConfigParser import NoSectionError

class SysinfoPlugin(Plugin):
	"""
		Plugin which retreives sys info
	"""

	PLUGIN_INFO = {
		'name': 'System Information',
		'description': 'Displays some system information',
		'authors': ['Wiebe Verweij', 'Lucas van Dijk'],
		'version': '1.0',
		'website': 'http://www.wiebelt.nl'
	}

	@command('server_load')
	def load(self, event):
		"""
			Displays information from the uptime linux command
		"""

		load = os.popen('uptime')
		load = load.read().splitlines()

		event.channel.pm(self.language('load_tmpl', output=load[0]))

	@command('os')
	def get_os(self, event):
		"""
			Sends operating system of the bot
		"""

		# Get kernel version
		kernel	= os.popen('uname -r')
		kernel	= kernel.read().splitlines()
		kernel	= kernel[0]

		# Get release version
		data	= os.popen('lsb_release -a 2> /dev/null').read()
		data	= data.strip()
		data	= data.splitlines()

		distro = "Unknown"
		for line in data:
			split = line.split(':')
			if split[0] == 'Description':
				distro = split[1].strip()
				break

		send = self.language('os_tmpl', kernel=kernel, distro=distro)

		event.channel.pm(send)

	@command('usage')
	def get_usage(self, event):
		"""
			Check how much memory and CPU time the bot uses
		"""

		# Get process information
		pid		= os.getpid()
		usage	= os.popen('ps -eo%cpu,%mem,rss,pid | grep ' + str(pid))
		pieces 	= usage.read().split()

		# Strip all the data that we dont need..
		print pieces

		# Now calculate and define the data
		cpu		= pieces[0]
		memory 	= int(pieces[2]) / 1024

		send = self.language('usage_tmpl', cpu=cpu, memory=memory)
		event.channel.pm(send)

	@command('cpu')
	def get_cpu(self, event):
		"""
			Spits out some CPU information
		"""

		# Get proccessor information
		cpu_info = os.popen('cat /proc/cpuinfo')
		cpu_info = cpu_info.read().splitlines()

		# Now get the specific information we want to display.
		for info in cpu_info:
			info = info.split(':')
			info[0] = info[0].strip()
			if info[0] == 'model name':
				cpu_model 	= info[1]
			elif info[0] == 'cpu MHz':
				cpu_mhz		= info[1]
			elif info[0] == 'cache size':
				cpu_cache	= info[1]

		# Get temperature information
		cpu_temp = None
		try:
			show_temp = self.bot.settings.get('SysInfo', 'sensors')
			if (show_temp == 'true'):
				sensors = os.popen('sensors')
				sensors = sensors.read().splitlines()

				for sensor in sensors:
					type = sensor.split(':')
					if type[0] == 'CPU Temp':
						cpu_temp = type[1].split('(')
						pieces = cpu_temp[0].split(' ')
						for piece in pieces:
							if piece != '':
								cpu_temp = piece
								break
		except NoSectionError:
			pass

		if cpu_temp:
			tmpl = 'cpu_with_temp_tmpl'
		else:
			tmpl = 'cpu_tmpl'

		# Now, lets format the message and send the message!
		send = self.language(tmpl, model=cpu_model, freq=cpu_mhz, cache=cpu_cache, temp=cpu_temp)
		event.channel.pm(send)

	@command('memory')
	def get_memory(self, event):
		# Get memory usage information
		memory_info = os.popen('free -m')
		memory_info = memory_info.read().splitlines()

		# Get RAM specific information
		pieces	= memory_info[1].split(' ')
		ram_info	= []
		for piece in pieces:
			if piece != '':
				ram_info.append(piece)

		ram_total	= ram_info[1]
		ram_used	= ram_info[2]
		ram_free	= ram_info[3]

		# Get Swap specific information
		pieces	= memory_info[3].split(' ')
		swap_info	= []
		for piece in pieces:
			if piece != '':
				swap_info.append(piece)

		swap_total	= swap_info[1]
		swap_used	= swap_info[2]
		swap_free	= swap_info[3]

		# Format and send it! :)
		send = self.language('memory_tmpl', ram_used=ram_used, ram_total=ram_total, swap_used=swap_used, swap_total=swap_total)
		event.channel.pm(send)

