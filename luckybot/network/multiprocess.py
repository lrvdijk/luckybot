"""
:mod:`luckybot.network.multiprocess` - Multiprocess sockets
===========================================================

This module contains some classes for handling with sockets, with each
socket running in its own process.

.. module:: luckybot.network.multiprocess
   :synopsis: Multiprocess socket helper classes

.. moduleauthor:: Lucas van Dijk <info@return1.net>
"""

from multiprocessing import Process, Queue, Value
from Queue import Empty
import socket
import select

from luckybot.network.base import BaseSocket, Socket

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, \
	 ENOTCONN, ESHUTDOWN, EINTR, EISCONN, errorcode

class SocketProcess(Process):
	"""
		This is the worker process for a specific connection
	"""

	def __init__(self, type, addr, recv_queue, send_queue):
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
				Python mod:`multiprocessing` module
		"""
		Process.__init__(self)

		self.recv_queue = recv_queue
		self.send_queue = send_queue
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

		read_success = True
		write_success = True

		if readables:
			read_success = self.read_data()

		if writeables:
			write_success = self.check_queue()

		return read_success and write_success and not errors


	def read_data(self):
		"""
			Reads data if there's anything available
		"""

		try:
			data = self.connection.recv(4096)
		except socket.error as e:
			# Connection closed
			print "No data, print exception"
			import traceback
			traceback.print_exc()

			return False

		if data == "":
			# Connection closed
			return False

		self.recv_queue.put(data)
		return True

	def check_queue(self):
		"""
			Checks the send queue, and sends all data in it
		"""

		while True:
			try:
				data = self.send_queue.get(timeout=2)
				self.connection.send(data)

				if data.startswith("QUIT"):
					return False
			except Empty:
				self.check_for_send_queue.value = False
				break

		return True

	def run(self):
		"""
			Runs the process, opens up a connection, and starts sending
			/receiving
		"""

		self.connection = Socket(self.type)
		self.connection.open(self.addr)
		self.connection.setblocking(0)

		result = True

		while result:
			try:
				result = self.poll(self.check_for_send_queue.value, 0.1)
			except KeyboardInterrupt:
				break

		self.recv_queue.put("QUIT\n")

		try:
			self.connection.close()
			self.terminate()
		except:
			pass

		print "End of Process"

		return 0

class MultiProcessSocket(BaseSocket):
	"""
		This connection will be run in a seperate subprocess
	"""

	def __init__(self, type):
		BaseSocket.__init__(self, type)

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

		self.process = SocketProcess(self.type, addr,
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
			return self.recv_queue.get(timeout=0.3)
		except Empty:
			return ""

	def close(self):
		"""
			Sends QUIT command to subprocess
		"""

		self.send("QUIT")

	@property
	def is_alive(self):
		"""
			Checks if the connection is still alive

			:Returns:
				A bool, True when still connected, else False
		"""
		return self.process and self.process.is_alive()
