__version__ = '1.0.0'

import collections
import toastedmarshmallow
from marshmallow import Schema, ValidationError, post_load
from marshmallow.base import FieldABC


class ModelMeta(type):
    @staticmethod
    def is_schema_attribute(attr):
        return isinstance(attr, FieldABC)

    @classmethod
    def __prepare__(metacls, name, bases):
        return collections.OrderedDict()

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)

        def make_object(self, data):
            return self._model_class(**data)

        def handle_error(self, error, data):
            if isinstance(error, ValidationError):
                error.kwargs['klass'] = self._model_class.__name__
                raise error
            else:
                e = ValidationError(error, klass=self._model_class.__name__)
                raise e

        schema_methods = dict(
            make_object=post_load(make_object),
            handle_error=handle_error
        )

        schema_class_attrs = {attr_name: attr
                              for attr_name, attr in cls.__dict__.items()
                              if ModelMeta.is_schema_attribute(attr)}

        meta_class = type('Meta', (object,), {'jit': toastedmarshmallow.Jit})
        schema_class_members = dict()
        schema_class_members.update(schema_methods)
        schema_class_members.update(schema_class_attrs)
        schema_class_members.update({'Meta': meta_class})

        schema_class_name = f'{cls.__name__}Schema'
        schema_class = type(schema_class_name, (Schema,), schema_class_members)
        schema_class._model_class = cls
        cls.SCHEMA = schema_class
        cls._schema_instance = schema_class()


class Model(metaclass=ModelMeta):
    SCHEMA = None
    _schema_instance = None

    @classmethod
    def from_dict(cls, data):
        result = cls._schema_instance.load(data)
        return result.data

    @classmethod
    def from_json(cls, data):
        result = cls._schema_instance.loads(data)
        return result.data

    def to_dict(self):
        result = self._schema_instance.dump(self)
        return result.data

    def to_json(self):
        result = self._schema_instance.dumps(self)
        return result.data

    def validate(self):
        self._schema_instance.dump(self)

    def get_validation_errors(self):
        errors_by_attr = dict()

        try:
            self._schema_instance.dump(self)
        except ValidationError as e:
            errors_by_attr = e.messages

        return errors_by_attr


class NestedModel:
    def __init__(self, nested_model: Model):
        self.nested_model = nested_model

    def __call__(self, *args, **kwargs):
        return self.nested_model.SCHEMA


class SelfReferencingModel:
    def __new__(cls, model_name: str):
        return f'{model_name}Schema'



