**********************************************************
:fire:toastedmarshmallow-enum:fire:: Dumps and Loads Enums
**********************************************************

Inspired by `Marshmallow Enum <https://github.com/justanr/marshmallow_enum>`_ and by ORM libraries.

The Toasted Marshmallow Enum package makes it possible to dump and load Enum values based on the ultra fast
serialization that `Toasted Marshmallow <https://github.com/lyft/toasted-marshmallow>`_ provides.


Installing toastedmarshmallow-enum
------------------------------------

.. code-block:: bash

  pip install toastedmarshmallow-enum


Using Toasted Marshmallow Enum
--------------------------------

Using Toasted Marshmallow Enum in an existing ``Marshmallow Schema`` is as easy as defining the enum class attribute
as an ``EnumField``. For example:

.. code-block:: python

    from enum import Enum

    import toastedmarshmallow
    from marshmallow import fields, Schema

    from toastedmarshmallow_enum import EnumField

    class Level(Enum):
        LOW = '0'
        MEDIUM = '1'
        HIGH = '2'

    class UserSchema(Schema):
        class Meta:
            jit = toastedmarshmallow.Jit

        name = fields.String()
        level = EnumField(Level)


How it works
------------

``Dump methods:``

.. code-block:: python

    class User:
        def __init(name, level):
            self.name = name
            self.level = level

    schema = DummyUserSchema()

    user = User(name='John Doe', level=Level.HIGH)
    print(schema.dump(user).data)
    # {'name': 'John Doe', 'level': 2}

    print(schema.load({'name': 'John Doe', 'level: 2}).data)
    # {'name': 'John Doe', 'level': 'HIGH'}
