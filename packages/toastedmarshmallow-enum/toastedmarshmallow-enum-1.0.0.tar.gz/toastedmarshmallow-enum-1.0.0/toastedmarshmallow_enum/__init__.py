__version__ = '1.0.0'

from enum import Enum

import marshmallow
from marshmallow import fields


class EnumField(fields.Field):
    def __init__(self, enum_class, default=marshmallow.missing, attribute=None, load_from=None, dump_to=None,
                 error=None, validate=None, required=False, allow_none=None, load_only=False,
                 dump_only=False, missing=marshmallow.missing, error_messages=None, **metadata):
        if not issubclass(enum_class, Enum):
            raise TypeError(f"{repr(enum_class)} must be an Enum")

        if default is not marshmallow.missing:
            if default and not isinstance(default, Enum):
                raise ValueError(f"Field {enum_class.__name__}: 'default' parameter should be an enum")

        if missing is not marshmallow.missing:
            if missing and not isinstance(missing, Enum):
                raise ValueError(f"Field {enum_class.__name__}: 'missing' parameter should be an enum")

        super().__init__(default=default, attribute=attribute, load_from=load_from, dump_to=dump_to,
                 error=error, validate=validate, required=required, allow_none=allow_none, load_only=load_only,
                 dump_only=dump_only, missing=missing, error_messages=error_messages, **metadata)
        self._enum_class = enum_class

    def _serialize(self, value, attr, obj):
        value_to_serialize = value.value if value else None
        if not value_to_serialize and self.default is not marshmallow.missing:
            value_to_serialize = self.default.value
        return super()._serialize(value_to_serialize, attr, obj)

    def _deserialize(self, value, attr, data):
        value_to_deserialize = self._enum_class(value) if value else None
        return super()._deserialize(value_to_deserialize, attr, data)