##
## This module should be compatible across Python 2 and 3
##
## Copyright (C) 2018 Codestruct
## All Rights Reserved.
##
from __future__ import print_function
import socket
import os
import json
import struct
import sys
import select
import errno
import ssl
import random
import time
from csiot.message import Message
from csiot.config import Config

if sys.version_info.major == 2:
	from Queue import Queue
else:
	from queue import Queue

""" In the API connector, we force the user to supply the API key
def get_api_key():
	path = "%s/.config/cse-node/service-key" % os.environ["HOME"]
	if not os.path.exists(path):
		raise OSError("no service key found at %s" % path)
	data = str()
	with open(path) as f:
		data = f.read().rstrip().replace('\0', '')
	return data
"""

class APISocket:
	def __init__(self):
		self.host = None
		self.port = None
		self.socket = None

		self.write_queue = Queue()

		self.m_on_open = lambda svc: print("%s connected" % str(svc))
		self.m_on_read = lambda x: print("%s" % x.data)
		self.m_on_close = lambda svc: print("%s closed" % str(svc))

		self.authenticated = False

		self.is_running = False

		self.cb_queue = Queue()
		self.callbacks = dict()

	def on_open(self, f):
		self.m_on_open = f

	def on_read(self, f):
		self.m_on_read = f

	def on_close(self, f):
		self.m_on_close = f

	def run_forever(self):
		self.is_running = True

		while self.is_running:
			r, w, e = select.select([self.socket], [self.socket], [], 1.0)
			for fd in r:
				message = self.recv()
				data = message.data
				if data:
					data = json.loads(data)
					# If this is json is a method, it has a status, and status is True
					if message.is_method() and "status" in data and data["status"]:
						# Then add our latest callback to the table
						json_id = data["id"]
						cb = self.cb_queue.get()
						self.callbacks[json_id] = cb
					elif "id" in data and data["id"] in self.callbacks:
						self.callbacks[data["id"]](data)
						del self.callbacks[data["id"]]
					else:
						self.m_on_read(data)

			for fd in w:
				if not self.write_queue.empty():
					item = self.write_queue.get()
					self.send(item)

			# Help the CPU out a bit..
			time.sleep(0.02)

	def recv(self):
			head = self.socket.recv(8)
			if not head:
				return None
			if len(head) != 8:
				print("bugged head size: %d" % len(size))
			size, m_type, = struct.unpack('<Ii', head)
			data = self.socket.recv(size - 4)

			return Message(m_type, data)

	def send(self, message):
		self.socket.send(struct.pack("<Ii%ds" % len(message.data),
			len(message.data) + 4, message.message_type, message.data.encode("UTF-8")))

	def send_event(self, event):
		data = json.dumps({
			"event": event
		})
		self.send(Message(Message.Event, data))

	def send_method(self, method, data, callback=None):
		out_data = json.dumps({
			"method": method,
			"data": data
		})

		if callback:
			self.cb_queue.put(callback)

		self.send(Message(Message.Method, out_data))

	def connect(self, key, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		self.socket = ssl.wrap_socket(self.socket)
		self.socket.context.load_default_certs()
		self.socket.connect((host, port))

		self.authenticated = self.auth_exchange(key)
		if self.authenticated:
			print("successfully authenticated with cluster server")
			self.m_on_open(self)
			return True
		return False

	def auth_exchange(self, api_key):
		out_data = json.dumps({
			"auth": "api",
			"key": api_key
		})

		out_struct = struct.pack("<Ii%ds" % len(out_data),
				len(out_data) + 4, Message.Auth, out_data.encode("UTF-8"))

		self.socket.send(out_struct)

		size, = struct.unpack("<I", self.socket.recv(4))
		response = self.socket.recv(size)
		json_type, = struct.unpack("<i", response[:4])
		response = response[4:]

		in_data = json.loads(response)
		return in_data["response"] == "auth" and in_data["status"]

class API:
	def __init__(self, key, host, port=6666):
		self.api_key = key
		self.api_host = host
		self.api_port = port
		self.api_socket = APISocket()
		self.method_callbacks = dict()

	def send_event(self, event):
		self.api_socket.send_event(event)

	# params should be a list of parameters to supply to the given method
	def send_method(self, method, data, callback):
		return self.api_socket.send_method(method, data, callback)

	# NOTE: You may not use call_method when run_forever has been invoked
	def call_method(self, method, data=None):
		self.api_socket.send_method(method, data)
		message = self.api_socket.recv()
		data = json.loads(message.data)

		print("Sent message id: %s" % data["id"])
		print("Received json confirmation: %s" % (not "error" in data))

		if "error" in data:
			return data

		message = self.api_socket.recv()
		data = json.loads(message.data)

		return data

	def on_read(self, data):
		data = json.loads(data)
		sys.stdout.write(" %d" % data["data"])
		sys.stdout.flush()

	def connect(self):
		self.api_socket.on_read(self.on_read)
		self.api_socket.connect(self.api_key, self.api_host, self.api_port)

	def run_forever(self):
		self.api_socket.run_forever()

if __name__ == "__main__":
	args = sys.argv[1:]
	key = str()

	if len(args) == 0:
		cfg = Config()
		if cfg["api_key"] == "":
			print("usage: %s <api-key>" % sys.argv[0])
			print("Alternatively, you can store `api_key' in the config file")
			exit(1)
		else:
			key = cfg["api_key"]
	else:
		key = args[0]

	api = API(key, "localhost", 6666)
	api.connect()
	print("result: %s" % api.call_method("sum", [1, 1]))

	def react(data):
		print("reacted: %s" % data)

	api.send_method("sum", [1, 2], react)
	api.run_forever()
	#api.send_method("sum", [1, 1], lambda x: print(x["data"] * 2))

