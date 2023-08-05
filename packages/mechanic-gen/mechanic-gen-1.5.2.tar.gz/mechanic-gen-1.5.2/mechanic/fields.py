# python native
import copy

# third party
from marshmallow import fields
from marshmallow import class_registry
from marshmallow.exceptions import ValidationError
from marshmallow_sqlalchemy.fields import Related
from sqlalchemy.orm.exc import NoResultFound


def _is_linkable(val):
    """
    Determines if the value passed in is a legitimate value to link to another object.
    :param val: string to link to another resource. Ex: "/api/dogs/1234"
    :return: True or False
    """
    return isinstance(val, str)


class OneOf(fields.Field):
    def __init__(self, field_types=[], **kwargs):
        super(OneOf, self).__init__(**kwargs)
        self.field_types = field_types

    def _serialize(self, value, attr, obj):
        vals = []
        for item in self.field_types:
            # add serialized values to array
            vals.append(item._serialize(value, attr, obj))

        # return the first value that is not None, [], {}, etc.
        for val in vals:
            if val:
                return val
        return None

    def _deserialize(self, value, attr, data):
        for item in self.field_types:
            try:
                item._validate(value)
                return item._deserialize(value, attr, data)
            except ValidationError:
                pass
        raise ValidationError(attr + ": does not match any of the possible field types.")


class MechanicEmbeddable(Related):
    """
    Field type that allows an object to be 'embeddable'.
    """
    def __init__(self, schema, deserialize_key=None, *args, **kwargs):
        self.schema = schema
        self.deserialize_key = deserialize_key
        super(MechanicEmbeddable, self).__init__(*args, **kwargs)

    @property
    def related_keys(self):
        if self.columns:
            mapper = self.related_model.__mapper__
            ret = []
            for column in self.columns:
                if column in mapper.columns.keys():
                    ret.append(mapper.get_property_by_column(mapper.columns[column]))
                elif column in mapper.attrs.keys():
                    ret.append(mapper.get_property(mapper.attrs[column].key))
            return ret

    def _serialize(self, value, attr, obj):
        if isinstance(self.schema, str):
            schema = class_registry.get_class(self.schema)
            self.schema = schema

        embed = self.context.get("embed", [])

        # Serialize with embedded objects
        if any(e.startswith(attr) for e in embed):
            return self._serialize_embed(attr, embed, value)

        # Serialize with links to objects
        return self._serialize_without_embed(attr, obj, value)

    def _serialize_without_embed(self, attr, obj, value):
        if isinstance(value, list):
            ret = []
            for item in value:
                ret.append(self._serialize(item, attr, obj))
        else:
            ret = {}
            for prop in self.related_keys:
                key_val = getattr(value, prop.key, None)
                if key_val:
                    ret[prop.key] = key_val

        if isinstance(ret, list) or len(ret) > 1:
            ret_val = ret
        else:
            if ret:
                ret_val = list(ret.values())[0]
            else:
                ret_val = [] if isinstance(ret, list) else None
        return ret_val

    def _serialize_embed(self, attr, embed, value):
        new_embed = []
        for embedded_item in embed:
            val = embedded_item
            if embedded_item.startswith(attr):
                val = ".".join(embedded_item.split(".")[1:])
            new_embed.append(val)
        nested_context = copy.deepcopy(self.context)
        nested_context["embed"] = new_embed
        if isinstance(value, list):
            s = self.schema(context=nested_context, many=True)
        else:
            s = self.schema(context=nested_context)
        return s.dump(value).data

    def _deserialize_by_link(self, value, attr):
        keys = {self.deserialize_key: value}
        query = self.session.query(self.related_model)
        try:
            if self.deserialize_key:
                result = query.filter_by(**{
                    self.deserialize_key: keys.get(self.deserialize_key)
                }).one()
            else:
                if not isinstance(value, dict):
                    if len(self.related_keys) != 1:
                        self.fail('invalid', value=value, keys=[prop.key for prop in self.related_keys])
                    value = {self.related_keys[0].key: value}

                # Use a faster path if the related key is the primary key.
                result = query.get([
                    keys.get(prop.key) for prop in self.related_keys
                ])
                if result is None:
                    raise NoResultFound
        except NoResultFound:
            raise ValidationError("Resource with '%s' %s not found" % (self.deserialize_key, value), field_names=[attr])
        return result

    def _deserialize(self, value, *args, **kwargs):
        if isinstance(self.schema, str):
            schema = class_registry.get_class(self.schema)
            self.schema = schema

        attr = args[0]
        val = args[1]

        # Handling linking by URI
        if isinstance(val.get(attr), str):
            return self._deserialize_by_link(value, attr)
        elif isinstance(val.get(attr), list) and all(isinstance(x, str) for x in val.get(attr)):
            result = []
            for item in val.get(attr):
                result.append(self._deserialize_by_link(item, attr))
            return result

        # Handle deserializing by embedded objects
        embed = self.context.get("embed", [])
        if not any(e.startswith(attr) for e in embed):
            # There is no embed option for the specified attribute.
            if not _is_linkable(val):
                raise ValidationError("Cannot create/update nested object without embed option.", field_names=[attr])
        else:
            # Handles nesting objects
            return self._deserialize_nested_object(attr, embed, val)

    def _deserialize_nested_object(self, attr, embed, val):
        new_embed = []
        for embedded_item in embed:
            ei = embedded_item
            if embedded_item.startswith(attr):
                ei = ".".join(embedded_item.split(".")[1:])
            new_embed.append(ei)
        nested_context = copy.deepcopy(self.context)
        nested_context["embed"] = new_embed
        many = False
        if isinstance(val.get(attr), list):
            many = True
        return self.schema(context=nested_context, many=many).load(val.get(attr), session=self.session).data
