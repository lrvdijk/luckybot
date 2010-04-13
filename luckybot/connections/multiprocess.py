"""
:mod:`luckybot.connections.multiprocess` - Multiprocess sockets
---------------------------------------------------------------

This module contains some classes for handling with sockets, with each
socket running in its own process.

.. module:: luckybot.connections.multiprocess
   :synopsis: Multiprocess socket helper classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from multiprocessing import Process, Queue, Value
from Queue import Empty
from luckybot.connections import BaseConnection

class ConnectionProcess(Process):
	"""
		This is the worker process for a specific connection
	"""

	def __init__(self, family, type, addr, recv_queue, send_queue):
		"""
			Initializes the worker

			:Args:
				* family (int): Socket Family, for example socket.AF_INET
				* type (int): Socket type, for example socket.SOCK_STREAM
				* connection_data (tuple): A tuple containing all information
					which is needed for a connection.
					(family, type, addr)
				* recv_queue (:class:`multiprocessing.Queue`): The queue
					where received data is put in
				* send_queue (:class:`multiprocessing.Queue`): The queue
					which contains the data to be sent

			.. seealso::
				Python mod:`socket` module
		"""
		Process.__init__(self)

		self.recv_queue = recv_queue
		self.send_queue = send_queue
		self.family = family
		self.type = type
		self.addr = addr
		self.check_for_send_queue = Value('b', False)
		self.buffer = ""

	def run(self):
		"""
			Runs the process, opens up a connection, and starts sending
			/receiving
		"""

		connection = Connection(self.family, self.type)
		connection.open(self.addr)

		while connection.is_alive:
			if self.check_for_send_queue.value:
				while True:
					try:
						data = self.send_queue.get(False)
						connection.send(data)

						if data.startswith("QUIT"):
							break 2
					except Empty:
						break

				self.check_for_send_queue.value = False

			try:
				data = connection.recv(1024)
			except socket.error:
				# Connection closed
				break

			if data == "":
				# Connection closed
				break

			self.buffer += data
			self.check_buffer()

		try:
			connection.close()
		except:
			pass

	def check_buffer(self):
		"""
			Checks if a newline is in the buffer (which means end of
			command), and appends it to the recv queue if so
		"""

		pos = self.buffer.find("\n")

		if pos != -1:
			data = self.buffer[0:pos+1]
			self.recv_queue.append(data)

			self.buffer = self.buffer[pos+1:]

			if self.buffer.find("\n") != -1:
				self.check_buffer()

class MultiProcessConnection(BaseConnection):
	"""
		This connection will be run in a seperate subprocess
	"""

	def __init__(self, family, type):
		BaseConnection.__init__(self, family, type)

		self.recv_queue = Queue()
		self.send_queue = Queue()
		self.process = None

	def open(self, addr):
		"""
			Creates a new subprocess for this connection

			:Args:
				* addr (tuple): Where to connect to (address, port)
		"""
		self.addr = addr

		self.process = ConnectionProcess(self.family, self.type, addr,
			self.recv_queue, self.send_queue)

		self.process.start()

	def send(self, data):
		"""
			Puts data in the send queue
		"""
		self.send_queue.append(data)
		self.process.check_for_send_queue.value = True

	def recv(self):
		"""
			Returns the first item from the queue
		"""

		try:
			return self.recv_queue.get()
		except Empty:
			return None

	def close(self):
		"""
			Sends QUIT command to subprocess
		"""

		self.send("QUIT :")

	@property
	def is_alive(self):
		"""
			Checks if the connection is still alive

			:Returns:
				A bool, True when still connected, else False
		"""
		return self.process and self.process.is_alive()
