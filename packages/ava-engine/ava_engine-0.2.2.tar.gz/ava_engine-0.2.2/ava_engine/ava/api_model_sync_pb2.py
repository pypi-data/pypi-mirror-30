# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ava_engine/ava/api_model_sync.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='ava_engine/ava/api_model_sync.proto',
  package='ava_engine',
  syntax='proto3',
  serialized_pb=_b('\n#ava_engine/ava/api_model_sync.proto\x12\nava_engine\"C\n\x05Model\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04path\x18\x03 \x01(\t\x12\x12\n\ncreated_at\x18\x04 \x01(\x05\"\x12\n\x10ModelSyncRequest\"6\n\x11ModelSyncResponse\x12!\n\x06models\x18\x01 \x03(\x0b\x32\x11.ava_engine.Modelb\x06proto3')
)




_MODEL = _descriptor.Descriptor(
  name='Model',
  full_name='ava_engine.Model',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='ava_engine.Model.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='name', full_name='ava_engine.Model.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='path', full_name='ava_engine.Model.path', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='created_at', full_name='ava_engine.Model.created_at', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=51,
  serialized_end=118,
)


_MODELSYNCREQUEST = _descriptor.Descriptor(
  name='ModelSyncRequest',
  full_name='ava_engine.ModelSyncRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=120,
  serialized_end=138,
)


_MODELSYNCRESPONSE = _descriptor.Descriptor(
  name='ModelSyncResponse',
  full_name='ava_engine.ModelSyncResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='models', full_name='ava_engine.ModelSyncResponse.models', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=140,
  serialized_end=194,
)

_MODELSYNCRESPONSE.fields_by_name['models'].message_type = _MODEL
DESCRIPTOR.message_types_by_name['Model'] = _MODEL
DESCRIPTOR.message_types_by_name['ModelSyncRequest'] = _MODELSYNCREQUEST
DESCRIPTOR.message_types_by_name['ModelSyncResponse'] = _MODELSYNCRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Model = _reflection.GeneratedProtocolMessageType('Model', (_message.Message,), dict(
  DESCRIPTOR = _MODEL,
  __module__ = 'ava_engine.ava.api_model_sync_pb2'
  # @@protoc_insertion_point(class_scope:ava_engine.Model)
  ))
_sym_db.RegisterMessage(Model)

ModelSyncRequest = _reflection.GeneratedProtocolMessageType('ModelSyncRequest', (_message.Message,), dict(
  DESCRIPTOR = _MODELSYNCREQUEST,
  __module__ = 'ava_engine.ava.api_model_sync_pb2'
  # @@protoc_insertion_point(class_scope:ava_engine.ModelSyncRequest)
  ))
_sym_db.RegisterMessage(ModelSyncRequest)

ModelSyncResponse = _reflection.GeneratedProtocolMessageType('ModelSyncResponse', (_message.Message,), dict(
  DESCRIPTOR = _MODELSYNCRESPONSE,
  __module__ = 'ava_engine.ava.api_model_sync_pb2'
  # @@protoc_insertion_point(class_scope:ava_engine.ModelSyncResponse)
  ))
_sym_db.RegisterMessage(ModelSyncResponse)


# @@protoc_insertion_point(module_scope)
