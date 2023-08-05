import collections
import json
import pprint
try:
    import configparser
    import io
except ImportError:
    import ConfigParser as configparser
    import StringIO as io

import marshmallow
from marshmallow import compat
from marshmallow import fields
try:
    import yaml
except ImportError:
    pass

# Checking Marshmallow version
MM2 = marshmallow.__version__.startswith('2')


@marshmallow.post_load
def __make_object__(self, data):
    obj = self.__model_class__(__post_load__=True, **data)
    obj.__schema__ = self
    return obj


class ModelMeta(type):
    def __new__(mcs, name, parents, dct):
        if '__schema_class__' not in dct:
            dct['__schema_class__'] = None
        cls = super(ModelMeta, mcs).__new__(mcs, name, parents, dct)

        schema_fields = {
            '__make_object__': __make_object__,
            '__model_class__': cls,
        }
        for key, value in dct.items():
            if isinstance(value, fields.Field):
                schema_fields[key] = value
                setattr(cls, key, None)
                if isinstance(value, fields.Method):
                    for method_name in (value.serialize_method_name,
                                        value.deserialize_method_name):
                        if method_name is not None:
                            schema_fields[method_name] = dct[method_name]

            elif hasattr(value, '__marshmallow_tags__'):
                schema_fields[key] = value

        parent_schema = cls.__schema_class__ or marshmallow.Schema
        if parents:
            for parent in parents:
                if issubclass(parent, Model):
                    parent_schema = parent.__schema_class__
                    break
        schema_class = type(name + 'Schema', (parent_schema, ), schema_fields)
        cls.__schema_class__ = schema_class

        return cls

    def __call__(cls, **kwargs):
        if kwargs.pop('__post_load__', False):
            obj = super(ModelMeta, cls).__call__(**kwargs)
            for name, value in kwargs.items():
                setattr(obj, name, value)
            obj.__init__(**kwargs)
        else:
            context = kwargs.pop('context', None)
            partial = kwargs.pop('partial', None)
            obj = cls.load(kwargs, context=context, partial=partial)
        return obj


class NestedModel(fields.Nested):
    def __init__(self, nested, **kwargs):
        super(NestedModel, self).__init__(nested.__schema_class__, **kwargs)

    def _deserialize(self, value, attr, data):
        if isinstance(value, Model):
            return value
        return super(NestedModel, self)._deserialize(value, attr, data)


class Model(compat.with_metaclass(ModelMeta)):
    __schema_class__ = marshmallow.Schema
    __schema__ = None

    @classmethod
    def __get_schema_class__(cls, **kwargs):
        if MM2:
            kwargs.setdefault('strict', True)
        return cls.__schema_class__(**kwargs)

    def __init__(self, context=None, partial=None, **kwargs):
        pass

    @property
    def context(self):
        return self.__schema__.context

    @context.setter
    def context(self, value):
        for name in self.__schema__.fields:
            attr = getattr(self, name)
            if isinstance(attr, Model):
                attr.context = value
        self.__schema__.context = value

    @classmethod
    def load(cls, data, context=None, many=None, partial=None):
        schema = cls.__get_schema_class__(context=context, partial=partial)
        loaded = schema.load(data, many=many)
        if MM2:
            return loaded[0]
        return loaded

    def dump(self):
        dump = self.__schema__.dump(self)
        if MM2:
            return dump.data
        return dump

    @classmethod
    def load_json(cls,
                  data,
                  context=None,
                  many=None,
                  partial=None,
                  *args,
                  **kwargs):
        schema = cls.__get_schema_class__(context=context)
        loaded = schema.loads(
            data, many=many, partial=partial, *args, **kwargs)
        if MM2:
            return loaded[0]
        return loaded

    def dump_json(self):
        dump = self.__schema__.dumps(self)
        if MM2:
            return dump.data
        return dump

    @classmethod
    def load_yaml(cls,
                  data,
                  context=None,
                  many=None,
                  partial=None,
                  *args,
                  **kwargs):
        loaded = yaml.load(data, *args, **kwargs)
        return cls.load(loaded, context=context, many=many, partial=partial)

    def dump_yaml(self, default_flow_style=False):
        return yaml.dump(self.dump(), default_flow_style=default_flow_style)

    @classmethod
    def load_ini(cls, data, context=None, partial=None, **kwargs):
        parser = configparser.ConfigParser(**kwargs)
        if compat.PY2:
            data = unicode(data)  # noqa
        parser.read_string(data)
        ddata = parser._sections
        ddata.update(parser.defaults())
        return cls.load(ddata, context=context, partial=partial)

    def dump_ini(self, **kwargs):
        data = {}
        default_data = {}
        for key, value in self.dump().items():
            if isinstance(value, dict):
                data[key] = value
            else:
                default_data[key] = value
        kwargs['defaults'] = default_data
        parser = configparser.ConfigParser(**kwargs)
        parser._sections = data
        fp = io.StringIO()
        parser.write(fp)
        return fp.getvalue().strip()

    @classmethod
    def validate(cls, data, context=None, many=None, partial=None):
        kwargs = {'context': context}
        if MM2:
            kwargs['strict'] = False
        schema = cls.__get_schema_class__(**kwargs)
        return schema.validate(data, many=many, partial=partial)

    def __copy__(self):
        return self.__class__.load(self.dump(), context=self.context)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for key in self.__schema__.fields.keys():
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    def __repr__(self):
        return "%s(**%s)" % (self.__class__.__name__, self.dump())

    def __str__(self):
        return pprint.pformat(self.dump())


def dump_many(data, context=None):
    ret = []
    for obj in data:
        if isinstance(obj, Model):
            if context is None:
                schema = obj.__schema__
            else:
                schema = obj.__get_schema_class__(context=context)
            obj_data = schema.dump(obj)
            if MM2:
                obj_data = obj_data[0]
            ret.append(obj_data)
        elif (isinstance(obj, collections.Sequence)
              and not isinstance(obj, str)):
            ret.append(dump_many(obj, context=context))
        else:
            raise marshmallow.ValidationError(
                "The object '%s' is not an instance of Model class" % obj,
                data=data)

    return ret


def dump_many_json(data, context=None, *args, **kwargs):
    ret = dump_many(data, context)
    return json.dumps(ret, *args, **kwargs)


def dump_many_yaml(data,
                   context=None,
                   default_flow_style=False,
                   *args,
                   **kwargs):
    ret = dump_many(data, context)
    return yaml.dump(
        ret, default_flow_style=default_flow_style, *args, **kwargs)
