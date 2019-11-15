import enum

from typing import Set, Type

import peewee


class EnumField(peewee.CharField):

    def __init__(
            self,
            enum_type: Type[enum.Enum],
            *args,
            **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._type: Type[enum.Enum] = enum_type
        self._values: Set[enum.Enum] = set([e.value for e in self._type])

    def db_value(self, value):
        if isinstance(value, self._type):
            return value.value

        value = self.coerce(value)
        if value not in self._values:
            raise TypeError(
                f"Expected {self._type.__name__} "
                f"type or one of {self._values}")
        return value

    def python_value(self, value):
        return self._type(value)
