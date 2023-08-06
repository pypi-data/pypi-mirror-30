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
import time
from csiot.message import Message
from csiot.config import Config

if sys.version_info.major == 2:
  from Queue import Queue
else:
  from queue import Queue

class ServiceSocket:
  def __init__(self):
    self.host = None
    self.port = None
    self.socket = None

    self.write_queue = Queue()

    self.m_on_open = lambda svc: print("%s connected" % str(svc))
    self.m_on_read = lambda msg: print("on_read: { type: %d, data: '%s' }" % (msg.message_type, msg.data))
    self.m_on_close = lambda svc: print("%s closed" % str(svc))

    self.authenticated = False

    self.is_running = False

  def on_open(self, f):
    self.m_on_open = f

  def on_read(self, f):
    self.m_on_read = f

  def on_close(self, f):
    self.m_on_close = f

  def run_forever(self):
    self.is_running = True

    while self.is_running:
      wfds = []
      if not self.write_queue.empty():
        wfds = [self.socket]
      r, w, e = select.select([self.socket], wfds, [], 1.0)
      if r == [self.socket]:
        self.socket.setblocking(1)
        size = self.socket.recv(4)
        if size is None or len(size) != 4:
          self.socket.setblocking(0)
          return False

        # Unpack unsigned size header
        size, = struct.unpack("<I", size)
        data = self.socket.recv(size)
        self.socket.setblocking(0)

        # Unpack signed message type
        message_type, = struct.unpack("<i", data[:4])
        data = data[4:]

        if not data:
          return False

        if len(data) > 0:
          self.m_on_read(Message(message_type, data.decode("UTF-8")))
        else:
          self.m_on_read(Message(message_type))

      if w == [self.socket]:
        item = self.write_queue.get()
        self.send(item)

  def stop(self):
    self.is_running = False

  def send(self, message):
    data = message.serialize()
    print("send:", data)
    print("send_size:", len(data))
    self.socket.send(data)

  def enqueue(self, message):
    print("Enqueued: { type: %d, message: %s }" % (message.message_type, message.data))
    self.write_queue.put(message)

  def connect(self, key, host, port):
    self.host = host
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    self.socket.connect((host, port))

    ## Go SSL
    self.socket = ssl.wrap_socket(self.socket, cert_reqs=ssl.CERT_NONE)

    self.authenticated = self.auth_exchange(key)
    if self.authenticated:
      print("successfully authenticated with cluster server")
      self.m_on_open(self)
      return True

    return False

  def auth_exchange(self, key):
    out_data = json.dumps({
      "auth": "service",
      "key": key
    })

    print("Using key: %s" % key)
    print("Using out_data: %s" % str(out_data))

    out_struct = struct.pack("<Ii%ds" % len(out_data),
        len(out_data) + 4, Message.Auth, out_data.encode("UTF-8"))

    self.socket.send(out_struct)

    size, = struct.unpack("<I", self.socket.recv(4))
    response = self.socket.recv(size)
    message_type, = struct.unpack("<i", response[:4])

    if message_type != Message.Auth:
      print("auth_exchange response wasn't of type Message.Auth")
      return False

    response = response[4:]

    in_data = json.loads(response.decode("UTF-8"))
    print(in_data)
    return in_data["response"] == "auth" and in_data["status"] == True

class Service:
  def __init__(self):
    self.service_socket = ServiceSocket()
    self.event_callbacks = dict()
    self.method_callbacks = dict()

  def provide_method(self, method, callback):
    out_data = json.dumps({
      "action": "subscribe",
      "method": method
    })

    message = Message(Message.Method, out_data)
    self.service_socket.send(message)
    self.method_callbacks[method] = callback

  def register_event(self, event, callback):
    out_data = json.dumps({
      "action": "subscribe",
      "event": event
    })
    self.event_callbacks[event] = callback

    message = Message(Message.Event, out_data)
    self.service_socket.send(message)

  def on_event(self, json_data):
    data = json_data

    cfg = Config()
    if "key" in data:
      if data["key"] != cfg["service_key"]:
        print("%s event registration was given an invalid key" % data["event"])
        return None

      if data["action"] == "subscribe":
        if data["status"] == False:
          event = data["event"]
          del self.event_callbacks[event]
        else:
          print("%s event registered with server" % data["event"])
    else:
      if data["event"] in self.event_callbacks:
        self.event_callbacks[data["event"]](data)

  def on_method(self, json_data):
    data = json_data

    cfg = Config()
    if "action" in data and data["action"] == "subscribe":
      ## We expect data["status"] here
      method = data["method"]
      if data["key"] != cfg["service_key"]:
        print("%s method registration was given an invalid key" % method)
        return None

      if method in self.method_callbacks:
        print("%s method registered with server" % data["method"])

      print("%s method was successfully subscribed to" % data["method"])
      return True

    print("attached request: %s" % str(data))
    # Unattach ids, user doesnt need them
    socket_id = data["socket_id"]
    del data["socket_id"]

    message_id = data["id"]
    del data["id"]

    node_id = data["node_id"]
    del data["node_id"]
    print("unattached request: %s" % str(data))

    if data["method"] in self.method_callbacks:
      method = data["method"]
      ret = self.method_callbacks[method](data)
      print("method reply: %s" % str(ret))
      # Reattach ids
      ret["id"] = message_id
      ret["node_id"] = node_id
      ret["socket_id"] = socket_id
      print("reattached reply: %s" % str(ret))

      # Add our responded to method data to outgoing queue
      message = Message(Message.Method, json.dumps(ret))
      self.service_socket.enqueue(message)
    else:
      print("%s method called but no method provided" % data["method"])

  def on_read(self, message):
    print("got data: %s" % message.data)
    data = json.loads(message.data)
    if message.is_type(Message.Heartbeat):
      print("got heartbeat")
      # Reply with a heartbeat
      self.service_socket.enqueue(message)
    elif message.is_event():
      self.on_event(data)
    elif message.is_method():
      self.on_method(data)
    else:
      print("unsupported message type: %d" % message.message_type)

  def on_ping(self, data):
    print("on_ping: called")

  def on_sum(self, data):
    c = 0
    for i in data["data"]:
      c += i
    data["data"] = c
    return data

  # key: node service-key
  def connect(self, key, host="localhost", port=6667):
    self.service_socket.on_read(self.on_read)
    self.service_socket.connect(key, host, port)

  # key: node service-key
  def run_forever(self):
    self.service_socket.run_forever()

if __name__ == "__main__":
  port = 6667
  if len(sys.argv) > 1:
    port = int(sys.argv[1])

  cfg = Config()

  service = Service()
  key = cfg["service_key"]
  if not key:
    print("missing service key, you need to configure ~/.csiot.conf")
    exit(1)

  service.connect(cfg["service_key"], port=port)

  service.provide_method("sum", service.on_sum)

  try:
    service.run_forever()
  except KeyboardInterrupt:
    pass

