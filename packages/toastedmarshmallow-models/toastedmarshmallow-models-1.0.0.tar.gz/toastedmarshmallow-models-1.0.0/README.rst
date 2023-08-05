***********************************************************************
:fire:toastedmarshmallow-models:fire:: Create Serializable Class Models
***********************************************************************

Inspired by `Marshmallow Models <https://github.com/douglas-treadwell/marshmallow-models>`_ and by ORM libraries.

The Toasted Marshmallow Models package makes it easy to define serializable classes based on the ultra fast
serialization that `Toasted Marshmallow <https://github.com/lyft/toasted-marshmallow>`_ provides.


Installing toastedmarshmallow-models
------------------------------------

.. code-block:: bash

  pip install toastedmarshmallow-models


Using Toasted Marshmallow Models
--------------------------------

Using Toasted Marshmallow Models in an existing class requires your class to inherit
the ``Model`` class and specify the relevant ``Marshmallow fields``. For example:

.. code-block:: python

    from marshmallow import fields
    from toastedmarshmallow_models import Model

    class Entity(Model):  # Inherit Model
        # Define Marshmallow fields
        id = fields.Integer()
        name = fields.String()

        def __init__(self, id, name):
            self.id = id
            self.name = name


How it works
------------

The Toasted Marshmallow Models package makes it easy to ``dump`` and ``load`` models.


``Dump methods:``

.. code-block:: python

    entity = Entity(id=1, name='John Doe')

    print(entity.to_dict())
    # {"id": 1, "name": "John"}

    print(entity.to_json())
    # '{"id": 1, "name": "John"}'


``Load Methods:``

.. code-block:: python

    entity = Entity.from_dict({"id": 1, "name": "John"}) # creates an Entity instance

    entity = Entity.from_json('{"id": 1, "name": "John"}') # creates an Entity instance


Features
--------

``Validation:``

.. code-block:: python

    entity = Entity(id='i-am-not-a-valid-int', name='John Doe')

    entity.validate()  # throws marshmallow.ValidationError if not valid


``Get validation errors:``

.. code-block:: python

    entity = Entity(id='i-am-not-a-valid-int', name='John Doe')

    entity.get_validation_errors()  # returns dict(id=['Not a valid integer.'])


``Nested Models:``

.. code-block:: python

    class ChildEntity(Model):
        name = fields.String()

        def __init__(self, name: str):
            self.name = name


    class ParentEntity(Model):
        name = fields.String()
        # Use NestedModel to define parent-child relationships
        children = fields.Nested(NestedModel(ChildEntity), many=True)

        def __init__(self, name: str, children: List[ChildEntity]):
            self.children = children
            self.name = name


``Self Referencing Model:``

.. code-block:: python

    class Employee(Model):
        name = fields.String()
        # Use SelfReferencingModel to define self-referencing relationships
        subordinates = fields.Nested(SelfReferencingModel('Employee'), many=True, allow_none=True)

        def __init__(self, name: str, subordinates: List['Employee'] = None):
            self.subordinates = subordinates
            self.name = name