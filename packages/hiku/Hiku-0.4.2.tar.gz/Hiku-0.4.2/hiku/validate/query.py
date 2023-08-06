import collections

from itertools import repeat
from contextlib import contextmanager

from ..types import AbstractTypeVisitor
from ..query import QueryVisitor
from ..graph import GraphVisitor, Node, Field, Link, Nothing
from ..compat import text_type

from .errors import Errors


_undefined = object()


class _AssumeRecord(AbstractTypeVisitor):

    def __init__(self, _nested=False):
        self._nested = _nested

    def visit(self, obj):
        if obj is not None:
            return obj.accept(self)

    def _false(self, obj):
        pass

    visit_any, visit_boolean, visit_string, visit_integer, visit_float, \
        visit_mapping, visit_callable, visit_typeref = repeat(_false, 8)

    def visit_optional(self, obj):
        if not self._nested:
            return _AssumeRecord(_nested=True).visit(obj.__type__)

    def visit_sequence(self, obj):
        if not self._nested:
            return _AssumeRecord(_nested=True).visit(obj.__item_type__)

    def visit_record(self, obj):
        # return fields alongside type definitions
        return obj.__field_types__


class _AssumeField(GraphVisitor):

    def __init__(self, node, errors):
        self.node = node
        self.errors = errors

    def visit_field(self, obj):
        return True

    def visit_link(self, obj):
        self.errors.report('Trying to query "{}.{}" link as it was a field'
                           .format(self.node.name or 'root', obj.name))
        return False

    def visit_node(self, obj):
        assert self.node.name is None,\
            'Nested node can be only in the root node'
        self.errors.report('Trying to query "{}" node as it was a field'
                           .format(obj.name))
        return False

    def visit_root(self, obj):
        raise AssertionError('Root node is not expected here')


class _OptionError(TypeError):

    def __init__(self, description):
        self.description = description
        super(_OptionError, self).__init__(description)


class _OptionTypeError(_OptionError):

    def __init__(self, value, expected):
        description = '"{}" instead of {!r}'.format(type(value).__name__,
                                                    expected)
        super(_OptionTypeError, self).__init__(description)


class _OptionTypeValidator(object):

    def __init__(self, value):
        self._value = [value]

    @property
    def value(self):
        return self._value[-1]

    @contextmanager
    def push(self, value):
        self._value.append(value)
        try:
            yield
        finally:
            self._value.pop()

    def visit(self, type_):
        type_.accept(self)

    def visit_boolean(self, type_):
        if not isinstance(self.value, bool):
            raise _OptionTypeError(self.value, type_)

    def visit_string(self, type_):
        if not isinstance(self.value, text_type):
            raise _OptionTypeError(self.value, type_)

    def visit_integer(self, type_):
        if not isinstance(self.value, int):
            raise _OptionTypeError(self.value, type_)

    def visit_float(self, type_):
        if not isinstance(self.value, float):
            raise _OptionTypeError(self.value, type_)

    def visit_optional(self, type_):
        if self.value is not None:
            self.visit(type_.__type__)

    def visit_sequence(self, type_):
        if not isinstance(self.value, collections.Sequence):
            raise _OptionTypeError(self.value, type_)
        for item in self.value:
            with self.push(item):
                self.visit(type_.__item_type__)

    def visit_mapping(self, type_):
        if not isinstance(self.value, collections.Mapping):
            raise _OptionTypeError(self.value, type_)
        for key, value in self.value.items():
            with self.push(key):
                self.visit(type_.__key_type__)
            with self.push(value):
                self.visit(type_.__value_type__)

    def visit_record(self, type_):
        if not isinstance(self.value, collections.Mapping):
            raise _OptionTypeError(self.value, type_)

        unknown = set(self.value).difference(type_.__field_types__)
        if unknown:
            fields = ', '.join(sorted(map(repr, unknown)))
            raise _OptionError('unknown fields: {}'.format(fields))

        missing = set(type_.__field_types__).difference(self.value)
        if missing:
            fields = ', '.join(sorted(missing))
            raise _OptionError('missing fields: {}'.format(fields))

        for key, value_type in type_.__field_types__.items():
            with self.push(self.value[key]):
                self.visit(value_type)


class _ValidateOptions(GraphVisitor):

    def __init__(self, options, for_, errors):
        self.options = options
        self.for_ = for_
        self.errors = errors
        self._options = options or {}

    def visit_link(self, obj):
        super(_ValidateOptions, self).visit_link(obj)
        unknown = set(self._options).difference(obj.options_map)
        if unknown:
            node, field = self.for_
            self.errors.report('Unknown options for "{}.{}": {}'.
                               format(node, field, ', '.join(unknown)))

    visit_field = visit_link

    def visit_option(self, obj):
        value = self._options.get(obj.name, obj.default)
        if value is Nothing:
            node, field = self.for_
            self.errors.report('Required option "{}.{}:{}" is not specified'
                               .format(node, field, obj.name))
        elif obj.type is not None:
            try:
                _OptionTypeValidator(value).visit(obj.type)
            except _OptionError as err:
                node, field = self.for_
                self.errors.report('Invalid value for option "{}.{}:{}", {}'
                                   .format(node, field, obj.name,
                                           err.description))

    def visit_node(self, obj):
        assert self.options is None, 'Node can not have options'

    def visit_root(self, obj):
        raise AssertionError('Root node is not expected here')


class _RecordFieldsValidator(QueryVisitor):

    def __init__(self, field_types, errors):
        self._field_types = field_types
        self._errors = errors

    def visit_field(self, obj):
        if obj.name not in self._field_types:
            self._errors.report('Unknown field name')
        elif obj.options is not None:
            self._errors.report('Options are not expected')
        elif _AssumeRecord().visit(self._field_types[obj.name]):
            self._errors.report('Trying to query "{}" link as it was a field'
                                .format(obj.name))

    def visit_link(self, obj):
        field_types = _AssumeRecord().visit(self._field_types[obj.name])
        if field_types is not None:
            fields_validator = _RecordFieldsValidator(field_types,
                                                      self._errors)
            for field in obj.node.fields:
                fields_validator.visit(field)
        else:
            self._errors.report('"{}" is not a link'.format(obj.name))

    def visit_node(self, obj):
        raise AssertionError('Node is not expected here')


class QueryValidator(QueryVisitor):

    def __init__(self, graph):
        self.map = graph.nodes_map
        self.path = [graph.root]
        self.errors = Errors()

    def visit_field(self, obj):
        node = self.path[-1]
        field = node.fields_map.get(obj.name)
        if field is not None:
            is_field = _AssumeField(node, self.errors).visit(field)
            if is_field:
                for_ = (node.name or 'root', obj.name)
                _ValidateOptions(obj.options, for_, self.errors).visit(field)
        else:
            self.errors.report('Field "{}" is not implemented in the "{}" node'
                               .format(obj.name, node.name or 'root'))

    def visit_link(self, obj):
        node = self.path[-1]
        graph_obj = node.fields_map.get(obj.name, _undefined)
        if isinstance(graph_obj, Field):
            for_ = (node.name or 'root', obj.name)
            _ValidateOptions(obj.options, for_, self.errors).visit(graph_obj)

            field_types = _AssumeRecord().visit(graph_obj.type)
            if field_types is not None:
                fields_validator = _RecordFieldsValidator(field_types,
                                                          self.errors)
                for field in obj.node.fields:
                    fields_validator.visit(field)
            else:
                self.errors.report('Trying to query "{}.{}" simple field '
                                   'as node'
                                   .format(node.name or 'root', obj.name))

        elif isinstance(graph_obj, Link):
            linked_node = self.map[graph_obj.node]
            for_ = (node.name or 'root', obj.name)
            _ValidateOptions(obj.options, for_, self.errors).visit(graph_obj)

            self.path.append(linked_node)
            try:
                self.visit(obj.node)
            finally:
                self.path.pop()

        elif isinstance(graph_obj, Node):
            linked_node = graph_obj
            if obj.options is not None:
                self.errors.report('Options are not possible here')
            self.path.append(linked_node)
            try:
                self.visit(obj.node)
            finally:
                self.path.pop()

        elif graph_obj is _undefined:
            self.errors.report('Link "{}" is not implemented in the "{}" node'
                               .format(obj.name, node.name or 'root'))
        else:
            raise TypeError(repr(graph_obj))


def validate(graph, query):
    query_validator = QueryValidator(graph)
    query_validator.visit(query)
    return query_validator.errors.list
