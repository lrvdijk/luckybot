"""
mod:`luckybot.processes` - Processes manager
============================================

This class manages all processes used for each connection to the IRC server.
When one fails, it automatically restarts it.

.. module:: luckybot.processes
   :synopsis: Handles processes for connections to the irc servers

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

class ProcessManager(object):
	"""
		This class manages each subprocess for any socket
	"""

	def __init__(self, servers, keep_alive=True):
		"""
			Constructor, initializes the manager

			:Args:
				* servers (list): List of server connections to watch
				* keep_alive (bool): Keep processes alive?

			.. seealso
			   :mod:`luckybot.connections`
		"""

		self.servers = servers
		self.keep_alive = keep_alive

	def check_processes(self):
		"""
			Checks each process if they're still alive, or any data is
			waiting to be read.

			If the process is dead, it optionally restarts it again.
		"""

		num_alive = 0
		for server in self.servers:
			alive = server.connection.is_alive

			if alive:
				data = server.recv()

				if data.startswith("QUIT"):
					alive = False
				else:
					num_alive += 1

			if not alive:
				if (hasattr(server, 'started') and self.keep_alive) or not hasattr(server, 'started'):
					# Make sure its really closed, and respawn the process again
					server.connect()
					server.started = True

					# Asume connection is successfull
					num_alive += 1

		return num_alive
