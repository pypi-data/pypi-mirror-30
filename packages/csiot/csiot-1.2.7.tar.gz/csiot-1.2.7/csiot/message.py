import struct

##
## Simple Message object to use for organizing data
class Message:
  Error = 0
  Event = 1
  Method = 2
  Auth = 3
  Heartbeat = 4

  def __init__(self, message_type, data = str("{}")):
    self.message_type = message_type
    self.data = data

  def is_type(self, message_type):
    return self.message_type == message_type

  def is_error(self):
    return self.is_type(Message.Error)

  def is_event(self):
    return self.is_type(Message.Event)

  def is_method(self):
    return self.is_type(Message.Method)

  def is_auth(self):
    return self.is_type(Message.Auth)

  def is_heartbeat(self):
    return self.is_type(Message.Heartbeat)

  def serialize(self):
    if self.data:
      print("data_1: %s" % self.data)
      data = bytes()
      if not isinstance(self.data, bytes):
        data = self.data.encode("UTF-8")
      else:
        data = self.data
      print("data:", data)
      print("data_size:", len(data) + 4)
      return struct.pack("<Ii%ds" % len(data), len(data) + 4, self.message_type, data)
    else:
      return struct.pack("<Ii", 4, self.message_type)

