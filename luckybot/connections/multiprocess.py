"""
:mod:`luckybot.connections.multiprocess` - Multiprocess sockets
===============================================================

This module contains some classes for handling with sockets, with each
socket running in its own process.

.. module:: luckybot.connections.multiprocess
   :synopsis: Multiprocess socket helper classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from multiprocessing import Process, Queue, Value
from Queue import Empty
from luckybot.connections import BaseConnection, Connection
import socket
import select

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
	 ENOTCONN, ESHUTDOWN, EINTR, EISCONN, errorcode

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
		self.check_for_send_queue = Value('b', True)
		self.buffer = ""

	def poll(self, writeable, timeout=1.0):
		"""
			Checks if our connection is readable or writeable, and if so
			calls the desired function
		"""

		readables = []
		writeables = []
		errors = []
		readables.append(self.connection._socket)

		if self.check_for_send_queue.value or writeable:
			writeables.append(self.connection._socket)

		errors.append(self.connection._socket)

		try:
			readables, writables, errors = select.select(readables, writeables, errors, timeout)
		except socket.error as e:
			if e.args[0] == EINTR:
				return

			raise

		if readables:
			self.read_data()

		if writeables:
			self.check_queue()

		if errors:
			raise EOFError


	def read_data(self):
		"""
			Reads data if there's anything available
		"""

		try:
			data = self.connection.recv(1024)
		except socket.error as e:
			# Connection closed
			print e
			raise EOFError

		if data == "":
			# Connection closed
			raise EOFError

		self.buffer += data
		self.check_buffer()

	def check_queue(self):
		"""
			Checks the send queue, and sends all data in it
		"""

		while True:
			try:
				data = self.send_queue.get(False)
				self.connection.send(data)

				if data.startswith("QUIT"):
					raise EOFError
			except Empty:
				self.check_for_send_queue.value = False
				break

	def run(self):
		"""
			Runs the process, opens up a connection, and starts sending
			/receiving
		"""

		self.connection = Connection(self.family, self.type)
		self.connection.open(self.addr)
		self.connection.setblocking(0)

		while True:
			try:
				self.poll(self.check_for_send_queue.value, 0.05)
			except KeyboardInterrupt:
				self.connection.send("QUIT LuckyBot v5 - http://luckybot.return1.org")
				break
			except EOFError:
				break

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
			self.recv_queue.put(data)

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
		self.send_queue.put(data)
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

		self.send("QUIT LuckyBot5 - http://luckybot.return1.net")

	@property
	def is_alive(self):
		"""
			Checks if the connection is still alive

			:Returns:
				A bool, True when still connected, else False
		"""
		return self.process and self.process.is_alive()
