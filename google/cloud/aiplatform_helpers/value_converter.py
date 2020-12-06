from __future__ import absolute_import
from google.protobuf.struct_pb2 import Value
from proto.marshal.collections.maps import MapComposite
from proto.marshal import Marshal
from google.protobuf import json_format
import ipdb


def to_value(self):
  """Converts a message type to a :class:`~google.protobuf.struct_pb2.Value` object.
   
  Args:
    message: the message to convert
  
  Returns:
    the message as a :class:`~google.protobuf.struct_pb2.Value` object
  """
  def is_prop(prop):
      if prop[0].isupper():
          return False
      if prop.startswith('_'):
          return False
      return True

  props = list(filter(is_prop, dir(self._pb)))
  
  props_dict = {}
  for prop in props:
      props_dict[prop] = getattr(self._pb, prop)
      
  return json_format.ParseDict(props_dict, Value())


def from_value(cls, value):
  """Creates instance of class from a :class:`~google.protobuf.struct_pb2.Value` object.

  Args:
    value: a :class:`~google.protobuf.struct_pb2.Value` object

  Returns:
    Instance of class
  """
  value_dict = json_format.MessageToDict(value)          
  return json_format.ParseDict(value_dict, cls()._pb)


def from_map(cls, map_):
  """Creates instance of class from a :class:`~proto.marshal.collections.maps.MapComposite` object.

  Args:
    map_: a :class:`~proto.marshal.collections.maps.MapComposite` object

  Returns:
    Instance of class
  """
  map_dict = dict(map_)
  marshal = Marshal(name='marshal')
  pb = marshal.to_proto(Value, map_)
  return from_value(cls, pb)
