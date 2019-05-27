import sys

from .proto import constants_pb2

for field, value in constants_pb2.DESCRIPTOR.GetOptions().ListFields():
    setattr(sys.modules[__name__], field.name, value)
