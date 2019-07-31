# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: golem_task_api/proto/golem_task_api.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='golem_task_api/proto/golem_task_api.proto',
  package='golem_task_api',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n)golem_task_api/proto/golem_task_api.proto\x12\x0egolem_task_api\"Z\n\x11\x43reateTaskRequest\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\x1a\n\x12max_subtasks_count\x18\x02 \x01(\x05\x12\x18\n\x10task_params_json\x18\x03 \x01(\t\"\x11\n\x0f\x43reateTaskReply\"%\n\x12NextSubtaskRequest\x12\x0f\n\x07task_id\x18\x01 \x01(\t\"V\n\x10NextSubtaskReply\x12\x12\n\nsubtask_id\x18\x01 \x01(\t\x12\x1b\n\x13subtask_params_json\x18\x02 \x01(\t\x12\x11\n\tresources\x18\x03 \x03(\t\"R\n\x0e\x43omputeRequest\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\x12\n\nsubtask_id\x18\x02 \x01(\t\x12\x1b\n\x13subtask_params_json\x18\x03 \x01(\t\"\'\n\x0c\x43omputeReply\x12\x17\n\x0foutput_filepath\x18\x01 \x01(\t\"4\n\rVerifyRequest\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\x12\n\nsubtask_id\x18\x02 \x01(\t\"5\n\x0bVerifyReply\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x15\n\rreject_reason\x18\x02 \x01(\t\">\n\x16\x44iscardSubtasksRequest\x12\x0f\n\x07task_id\x18\x01 \x01(\t\x12\x13\n\x0bsubtask_ids\x18\x02 \x03(\t\"5\n\x14\x44iscardSubtasksReply\x12\x1d\n\x15\x64iscarded_subtask_ids\x18\x01 \x03(\t\"\x15\n\x13RunBenchmarkRequest\"\"\n\x11RunBenchmarkReply\x12\r\n\x05score\x18\x01 \x01(\x02\",\n\x19HasPendingSubtasksRequest\x12\x0f\n\x07task_id\x18\x01 \x01(\t\"7\n\x17HasPendingSubtasksReply\x12\x1c\n\x14has_pending_subtasks\x18\x01 \x01(\x08\"\x11\n\x0fShutdownRequest\"\x0f\n\rShutdownReply2\xf8\x04\n\x0cRequestorApp\x12R\n\nCreateTask\x12!.golem_task_api.CreateTaskRequest\x1a\x1f.golem_task_api.CreateTaskReply\"\x00\x12U\n\x0bNextSubtask\x12\".golem_task_api.NextSubtaskRequest\x1a .golem_task_api.NextSubtaskReply\"\x00\x12\x46\n\x06Verify\x12\x1d.golem_task_api.VerifyRequest\x1a\x1b.golem_task_api.VerifyReply\"\x00\x12\x61\n\x0f\x44iscardSubtasks\x12&.golem_task_api.DiscardSubtasksRequest\x1a$.golem_task_api.DiscardSubtasksReply\"\x00\x12X\n\x0cRunBenchmark\x12#.golem_task_api.RunBenchmarkRequest\x1a!.golem_task_api.RunBenchmarkReply\"\x00\x12j\n\x12HasPendingSubtasks\x12).golem_task_api.HasPendingSubtasksRequest\x1a\'.golem_task_api.HasPendingSubtasksReply\"\x00\x12L\n\x08Shutdown\x12\x1f.golem_task_api.ShutdownRequest\x1a\x1d.golem_task_api.ShutdownReply\"\x00\x32\x80\x02\n\x0bProviderApp\x12I\n\x07\x43ompute\x12\x1e.golem_task_api.ComputeRequest\x1a\x1c.golem_task_api.ComputeReply\"\x00\x12X\n\x0cRunBenchmark\x12#.golem_task_api.RunBenchmarkRequest\x1a!.golem_task_api.RunBenchmarkReply\"\x00\x12L\n\x08Shutdown\x12\x1f.golem_task_api.ShutdownRequest\x1a\x1d.golem_task_api.ShutdownReply\"\x00\x62\x06proto3')
)




_CREATETASKREQUEST = _descriptor.Descriptor(
  name='CreateTaskRequest',
  full_name='golem_task_api.CreateTaskRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='task_id', full_name='golem_task_api.CreateTaskRequest.task_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_subtasks_count', full_name='golem_task_api.CreateTaskRequest.max_subtasks_count', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='task_params_json', full_name='golem_task_api.CreateTaskRequest.task_params_json', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=61,
  serialized_end=151,
)


_CREATETASKREPLY = _descriptor.Descriptor(
  name='CreateTaskReply',
  full_name='golem_task_api.CreateTaskReply',
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
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=153,
  serialized_end=170,
)


_NEXTSUBTASKREQUEST = _descriptor.Descriptor(
  name='NextSubtaskRequest',
  full_name='golem_task_api.NextSubtaskRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='task_id', full_name='golem_task_api.NextSubtaskRequest.task_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=172,
  serialized_end=209,
)


_NEXTSUBTASKREPLY = _descriptor.Descriptor(
  name='NextSubtaskReply',
  full_name='golem_task_api.NextSubtaskReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='subtask_id', full_name='golem_task_api.NextSubtaskReply.subtask_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='subtask_params_json', full_name='golem_task_api.NextSubtaskReply.subtask_params_json', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='resources', full_name='golem_task_api.NextSubtaskReply.resources', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=211,
  serialized_end=297,
)


_COMPUTEREQUEST = _descriptor.Descriptor(
  name='ComputeRequest',
  full_name='golem_task_api.ComputeRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='task_id', full_name='golem_task_api.ComputeRequest.task_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='subtask_id', full_name='golem_task_api.ComputeRequest.subtask_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='subtask_params_json', full_name='golem_task_api.ComputeRequest.subtask_params_json', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=299,
  serialized_end=381,
)


_COMPUTEREPLY = _descriptor.Descriptor(
  name='ComputeReply',
  full_name='golem_task_api.ComputeReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='output_filepath', full_name='golem_task_api.ComputeReply.output_filepath', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=383,
  serialized_end=422,
)


_VERIFYREQUEST = _descriptor.Descriptor(
  name='VerifyRequest',
  full_name='golem_task_api.VerifyRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='task_id', full_name='golem_task_api.VerifyRequest.task_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='subtask_id', full_name='golem_task_api.VerifyRequest.subtask_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=424,
  serialized_end=476,
)


_VERIFYREPLY = _descriptor.Descriptor(
  name='VerifyReply',
  full_name='golem_task_api.VerifyReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='success', full_name='golem_task_api.VerifyReply.success', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='reject_reason', full_name='golem_task_api.VerifyReply.reject_reason', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=478,
  serialized_end=531,
)


_DISCARDSUBTASKSREQUEST = _descriptor.Descriptor(
  name='DiscardSubtasksRequest',
  full_name='golem_task_api.DiscardSubtasksRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='task_id', full_name='golem_task_api.DiscardSubtasksRequest.task_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='subtask_ids', full_name='golem_task_api.DiscardSubtasksRequest.subtask_ids', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=533,
  serialized_end=595,
)


_DISCARDSUBTASKSREPLY = _descriptor.Descriptor(
  name='DiscardSubtasksReply',
  full_name='golem_task_api.DiscardSubtasksReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='discarded_subtask_ids', full_name='golem_task_api.DiscardSubtasksReply.discarded_subtask_ids', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=597,
  serialized_end=650,
)


_RUNBENCHMARKREQUEST = _descriptor.Descriptor(
  name='RunBenchmarkRequest',
  full_name='golem_task_api.RunBenchmarkRequest',
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
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=652,
  serialized_end=673,
)


_RUNBENCHMARKREPLY = _descriptor.Descriptor(
  name='RunBenchmarkReply',
  full_name='golem_task_api.RunBenchmarkReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='score', full_name='golem_task_api.RunBenchmarkReply.score', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=675,
  serialized_end=709,
)


_HASPENDINGSUBTASKSREQUEST = _descriptor.Descriptor(
  name='HasPendingSubtasksRequest',
  full_name='golem_task_api.HasPendingSubtasksRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='task_id', full_name='golem_task_api.HasPendingSubtasksRequest.task_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=711,
  serialized_end=755,
)


_HASPENDINGSUBTASKSREPLY = _descriptor.Descriptor(
  name='HasPendingSubtasksReply',
  full_name='golem_task_api.HasPendingSubtasksReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='has_pending_subtasks', full_name='golem_task_api.HasPendingSubtasksReply.has_pending_subtasks', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=757,
  serialized_end=812,
)


_SHUTDOWNREQUEST = _descriptor.Descriptor(
  name='ShutdownRequest',
  full_name='golem_task_api.ShutdownRequest',
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
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=814,
  serialized_end=831,
)


_SHUTDOWNREPLY = _descriptor.Descriptor(
  name='ShutdownReply',
  full_name='golem_task_api.ShutdownReply',
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
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=833,
  serialized_end=848,
)

DESCRIPTOR.message_types_by_name['CreateTaskRequest'] = _CREATETASKREQUEST
DESCRIPTOR.message_types_by_name['CreateTaskReply'] = _CREATETASKREPLY
DESCRIPTOR.message_types_by_name['NextSubtaskRequest'] = _NEXTSUBTASKREQUEST
DESCRIPTOR.message_types_by_name['NextSubtaskReply'] = _NEXTSUBTASKREPLY
DESCRIPTOR.message_types_by_name['ComputeRequest'] = _COMPUTEREQUEST
DESCRIPTOR.message_types_by_name['ComputeReply'] = _COMPUTEREPLY
DESCRIPTOR.message_types_by_name['VerifyRequest'] = _VERIFYREQUEST
DESCRIPTOR.message_types_by_name['VerifyReply'] = _VERIFYREPLY
DESCRIPTOR.message_types_by_name['DiscardSubtasksRequest'] = _DISCARDSUBTASKSREQUEST
DESCRIPTOR.message_types_by_name['DiscardSubtasksReply'] = _DISCARDSUBTASKSREPLY
DESCRIPTOR.message_types_by_name['RunBenchmarkRequest'] = _RUNBENCHMARKREQUEST
DESCRIPTOR.message_types_by_name['RunBenchmarkReply'] = _RUNBENCHMARKREPLY
DESCRIPTOR.message_types_by_name['HasPendingSubtasksRequest'] = _HASPENDINGSUBTASKSREQUEST
DESCRIPTOR.message_types_by_name['HasPendingSubtasksReply'] = _HASPENDINGSUBTASKSREPLY
DESCRIPTOR.message_types_by_name['ShutdownRequest'] = _SHUTDOWNREQUEST
DESCRIPTOR.message_types_by_name['ShutdownReply'] = _SHUTDOWNREPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

CreateTaskRequest = _reflection.GeneratedProtocolMessageType('CreateTaskRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATETASKREQUEST,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.CreateTaskRequest)
  })
_sym_db.RegisterMessage(CreateTaskRequest)

CreateTaskReply = _reflection.GeneratedProtocolMessageType('CreateTaskReply', (_message.Message,), {
  'DESCRIPTOR' : _CREATETASKREPLY,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.CreateTaskReply)
  })
_sym_db.RegisterMessage(CreateTaskReply)

NextSubtaskRequest = _reflection.GeneratedProtocolMessageType('NextSubtaskRequest', (_message.Message,), {
  'DESCRIPTOR' : _NEXTSUBTASKREQUEST,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.NextSubtaskRequest)
  })
_sym_db.RegisterMessage(NextSubtaskRequest)

NextSubtaskReply = _reflection.GeneratedProtocolMessageType('NextSubtaskReply', (_message.Message,), {
  'DESCRIPTOR' : _NEXTSUBTASKREPLY,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.NextSubtaskReply)
  })
_sym_db.RegisterMessage(NextSubtaskReply)

ComputeRequest = _reflection.GeneratedProtocolMessageType('ComputeRequest', (_message.Message,), {
  'DESCRIPTOR' : _COMPUTEREQUEST,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.ComputeRequest)
  })
_sym_db.RegisterMessage(ComputeRequest)

ComputeReply = _reflection.GeneratedProtocolMessageType('ComputeReply', (_message.Message,), {
  'DESCRIPTOR' : _COMPUTEREPLY,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.ComputeReply)
  })
_sym_db.RegisterMessage(ComputeReply)

VerifyRequest = _reflection.GeneratedProtocolMessageType('VerifyRequest', (_message.Message,), {
  'DESCRIPTOR' : _VERIFYREQUEST,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.VerifyRequest)
  })
_sym_db.RegisterMessage(VerifyRequest)

VerifyReply = _reflection.GeneratedProtocolMessageType('VerifyReply', (_message.Message,), {
  'DESCRIPTOR' : _VERIFYREPLY,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.VerifyReply)
  })
_sym_db.RegisterMessage(VerifyReply)

DiscardSubtasksRequest = _reflection.GeneratedProtocolMessageType('DiscardSubtasksRequest', (_message.Message,), {
  'DESCRIPTOR' : _DISCARDSUBTASKSREQUEST,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.DiscardSubtasksRequest)
  })
_sym_db.RegisterMessage(DiscardSubtasksRequest)

DiscardSubtasksReply = _reflection.GeneratedProtocolMessageType('DiscardSubtasksReply', (_message.Message,), {
  'DESCRIPTOR' : _DISCARDSUBTASKSREPLY,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.DiscardSubtasksReply)
  })
_sym_db.RegisterMessage(DiscardSubtasksReply)

RunBenchmarkRequest = _reflection.GeneratedProtocolMessageType('RunBenchmarkRequest', (_message.Message,), {
  'DESCRIPTOR' : _RUNBENCHMARKREQUEST,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.RunBenchmarkRequest)
  })
_sym_db.RegisterMessage(RunBenchmarkRequest)

RunBenchmarkReply = _reflection.GeneratedProtocolMessageType('RunBenchmarkReply', (_message.Message,), {
  'DESCRIPTOR' : _RUNBENCHMARKREPLY,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.RunBenchmarkReply)
  })
_sym_db.RegisterMessage(RunBenchmarkReply)

HasPendingSubtasksRequest = _reflection.GeneratedProtocolMessageType('HasPendingSubtasksRequest', (_message.Message,), {
  'DESCRIPTOR' : _HASPENDINGSUBTASKSREQUEST,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.HasPendingSubtasksRequest)
  })
_sym_db.RegisterMessage(HasPendingSubtasksRequest)

HasPendingSubtasksReply = _reflection.GeneratedProtocolMessageType('HasPendingSubtasksReply', (_message.Message,), {
  'DESCRIPTOR' : _HASPENDINGSUBTASKSREPLY,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.HasPendingSubtasksReply)
  })
_sym_db.RegisterMessage(HasPendingSubtasksReply)

ShutdownRequest = _reflection.GeneratedProtocolMessageType('ShutdownRequest', (_message.Message,), {
  'DESCRIPTOR' : _SHUTDOWNREQUEST,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.ShutdownRequest)
  })
_sym_db.RegisterMessage(ShutdownRequest)

ShutdownReply = _reflection.GeneratedProtocolMessageType('ShutdownReply', (_message.Message,), {
  'DESCRIPTOR' : _SHUTDOWNREPLY,
  '__module__' : 'golem_task_api.proto.golem_task_api_pb2'
  # @@protoc_insertion_point(class_scope:golem_task_api.ShutdownReply)
  })
_sym_db.RegisterMessage(ShutdownReply)



_REQUESTORAPP = _descriptor.ServiceDescriptor(
  name='RequestorApp',
  full_name='golem_task_api.RequestorApp',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=851,
  serialized_end=1483,
  methods=[
  _descriptor.MethodDescriptor(
    name='CreateTask',
    full_name='golem_task_api.RequestorApp.CreateTask',
    index=0,
    containing_service=None,
    input_type=_CREATETASKREQUEST,
    output_type=_CREATETASKREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='NextSubtask',
    full_name='golem_task_api.RequestorApp.NextSubtask',
    index=1,
    containing_service=None,
    input_type=_NEXTSUBTASKREQUEST,
    output_type=_NEXTSUBTASKREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Verify',
    full_name='golem_task_api.RequestorApp.Verify',
    index=2,
    containing_service=None,
    input_type=_VERIFYREQUEST,
    output_type=_VERIFYREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='DiscardSubtasks',
    full_name='golem_task_api.RequestorApp.DiscardSubtasks',
    index=3,
    containing_service=None,
    input_type=_DISCARDSUBTASKSREQUEST,
    output_type=_DISCARDSUBTASKSREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='RunBenchmark',
    full_name='golem_task_api.RequestorApp.RunBenchmark',
    index=4,
    containing_service=None,
    input_type=_RUNBENCHMARKREQUEST,
    output_type=_RUNBENCHMARKREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='HasPendingSubtasks',
    full_name='golem_task_api.RequestorApp.HasPendingSubtasks',
    index=5,
    containing_service=None,
    input_type=_HASPENDINGSUBTASKSREQUEST,
    output_type=_HASPENDINGSUBTASKSREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Shutdown',
    full_name='golem_task_api.RequestorApp.Shutdown',
    index=6,
    containing_service=None,
    input_type=_SHUTDOWNREQUEST,
    output_type=_SHUTDOWNREPLY,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_REQUESTORAPP)

DESCRIPTOR.services_by_name['RequestorApp'] = _REQUESTORAPP


_PROVIDERAPP = _descriptor.ServiceDescriptor(
  name='ProviderApp',
  full_name='golem_task_api.ProviderApp',
  file=DESCRIPTOR,
  index=1,
  serialized_options=None,
  serialized_start=1486,
  serialized_end=1742,
  methods=[
  _descriptor.MethodDescriptor(
    name='Compute',
    full_name='golem_task_api.ProviderApp.Compute',
    index=0,
    containing_service=None,
    input_type=_COMPUTEREQUEST,
    output_type=_COMPUTEREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='RunBenchmark',
    full_name='golem_task_api.ProviderApp.RunBenchmark',
    index=1,
    containing_service=None,
    input_type=_RUNBENCHMARKREQUEST,
    output_type=_RUNBENCHMARKREPLY,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='Shutdown',
    full_name='golem_task_api.ProviderApp.Shutdown',
    index=2,
    containing_service=None,
    input_type=_SHUTDOWNREQUEST,
    output_type=_SHUTDOWNREPLY,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_PROVIDERAPP)

DESCRIPTOR.services_by_name['ProviderApp'] = _PROVIDERAPP

# @@protoc_insertion_point(module_scope)
