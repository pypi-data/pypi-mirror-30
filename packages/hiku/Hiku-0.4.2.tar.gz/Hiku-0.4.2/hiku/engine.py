import inspect

from functools import partial
from itertools import chain, repeat
from collections import defaultdict, Sequence

from . import query
from .graph import Link, Node, Maybe, One, Many, Nothing, Field
from .result import Result
from .executors.queue import Workflow, Queue


class SplitPattern(query.QueryVisitor):

    def __init__(self, node):
        self._node = node
        self._fields = []
        self._links = []
        self._nodes = []

    def split(self, pattern):
        for item in pattern.fields:
            self.visit(item)
        return self._fields, self._links, self._nodes

    def visit_node(self, obj):
        raise ValueError('Unexpected value: {!r}'.format(obj))

    def visit_field(self, obj):
        self._fields.append((self._node.fields_map[obj.name], obj))

    def visit_link(self, obj):
        graph_obj = self._node.fields_map[obj.name]
        if isinstance(graph_obj, Link):
            if graph_obj.requires:
                self._fields.append((self._node.fields_map[graph_obj.requires],
                                     query.Field(graph_obj.requires)))
            self._links.append((graph_obj, obj))
        elif isinstance(graph_obj, Node):
            self._nodes.append(obj)
        else:
            assert isinstance(graph_obj, Field), type(graph_obj)
            # `obj` here is a link, but this link is treated as a complex field
            self._fields.append((graph_obj, obj))


def _check_store_fields(node, fields, ids, result):
    if node.name is not None and ids is not None:
        if (
            isinstance(result, Sequence)
            and len(result) == len(ids)
            and all(isinstance(r, Sequence) and len(r) == len(fields)
                    for r in result)
        ):
            return
        else:
            expected = ('list (len: {}) of lists (len: {})'
                        .format(len(ids), len(fields)))
    else:
        if isinstance(result, Sequence) and len(result) == len(fields):
            return
        else:
            expected = 'list (len: {})'.format(len(fields))
    raise TypeError('Can\'t store field values, node: {!r}, fields: {!r}, '
                    'expected: {}, returned: {!r}'
                    .format(node.name or '__root__', [f.name for f in fields],
                            expected, result))


def store_fields(result, node, fields, ids, query_result):
    if inspect.isgenerator(query_result):
        query_result = list(query_result)

    _check_store_fields(node, fields, ids, query_result)

    names = [f.name for f in fields]
    if node.name is not None:
        if ids is not None:
            node_index = result.index.setdefault(node.name, {})
            for i, row in zip(ids, query_result):
                node_data = node_index.setdefault(i, {})
                node_data.update(zip(names, row))
        else:
            node_data = result.root.setdefault(node.name, {})
            node_data.update(zip(names, query_result))
    else:
        result.root.update(zip(names, query_result))


def link_reqs(result, node, link, ids):
    if node.name is not None:
        if ids is not None:
            return [result.index[node.name][i][link.requires] for i in ids]
        else:
            return result.root[node.name][link.requires]
    else:
        return result.root[link.requires]


def link_ref_maybe(result, link, ident):
    return None if ident is Nothing else result.ref(link.node, ident)


def link_ref_one(result, link, ident):
    assert ident is not Nothing
    return result.ref(link.node, ident)


def link_ref_many(result, link, idents):
    return [result.ref(link.node, i) for i in idents]


_LINK_REF_MAKER = {
    Maybe: link_ref_maybe,
    One: link_ref_one,
    Many: link_ref_many,
}


def _check_store_links(node, link, ids, result):
    if node.name is not None and ids is not None and link.requires is not None:
        if link.type_enum is Maybe or link.type_enum is One:
            if isinstance(result, Sequence) and len(result) == len(ids):
                return
            else:
                expected = 'list (len: {})'.format(len(ids))
        elif link.type_enum is Many:
            if (
                isinstance(result, Sequence)
                and len(result) == len(ids)
                and all(isinstance(r, Sequence) for r in result)
            ):
                return
            else:
                expected = 'list (len: {}) of lists'.format(len(ids))
        else:
            raise TypeError(link.type_enum)
    else:
        if link.type_enum is Maybe or link.type_enum is One:
            return
        elif link.type_enum is Many:
            if isinstance(result, Sequence):
                return
            else:
                expected = 'list'
        else:
            raise TypeError(link.type_enum)
    raise TypeError('Can\'t store link values, node: {!r}, link: {!r}, '
                    'expected: {}, returned: {!r}'
                    .format(node.name or '__root__', link.name,
                            expected, result))


def store_links(result, node, link, ids, query_result):
    _check_store_links(node, link, ids, query_result)

    field_val = partial(_LINK_REF_MAKER[link.type_enum], result, link)
    if node.name is not None:
        if ids is not None:
            if link.requires is None:
                query_result = repeat(query_result, len(ids))
            node_index = result.index.setdefault(node.name, {})
            for i, res in zip(ids, query_result):
                node_data = node_index.setdefault(i, {})
                node_data[link.name] = field_val(res)
        else:
            node_data = result.root.setdefault(node.name, {})
            node_data[link.name] = field_val(query_result)
    else:
        result.root[link.name] = field_val(query_result)


def link_result_to_ids(from_list, link_type, result):
    if from_list:
        if link_type is Maybe:
            return [i for i in result if i is not Nothing]
        elif link_type is One:
            if any(i is Nothing for i in result):
                raise TypeError('Non-optional link should not return Nothing: '
                                '{!r}'.format(result))
            return result
        elif link_type is Many:
            return list(chain.from_iterable(result))
    else:
        if link_type is Maybe:
            return [] if result is Nothing else [result]
        elif link_type is One:
            if result is Nothing:
                raise TypeError('Non-optional link should not return Nothing')
            return [result]
        elif link_type is Many:
            return result
    raise TypeError(repr([from_list, link_type]))


def _yield_options(graph_obj, query_obj):
    options = query_obj.options or {}
    for option in graph_obj.options:
        value = options.get(option.name, option.default)
        if value is Nothing:
            raise TypeError('Required option "{}" for {!r} was not provided'
                            .format(option.name, graph_obj))
        else:
            yield option.name, value


def get_options(graph_obj, query_obj):
    return dict(_yield_options(graph_obj, query_obj))


class Query(Workflow):

    def __init__(self, queue, task_set, graph, ctx):
        self._queue = queue
        self._task_set = task_set
        self.graph = graph
        self._ctx = ctx
        self._result = Result()

    def _submit(self, func, *args, **kwargs):
        if _do_pass_context(func):
            return self._task_set.submit(func, self._ctx, *args, **kwargs)
        else:
            return self._task_set.submit(func, *args, **kwargs)

    def result(self):
        return self._result

    def process_node(self, node, pattern, ids):
        fields, links, nodes = SplitPattern(node).split(pattern)

        assert not (node.name and nodes), 'Nested nodes are not supported yet'
        for link in nodes:
            self.process_node(node.fields_map[link.name], link.node, None)

        to_func = {}
        from_func = defaultdict(list)
        from_sq = defaultdict(list)
        for graph_field, query_field in fields:
            sq = getattr(graph_field.func, '__subquery__', None)
            if sq is None:
                to_func[graph_field.name] = graph_field.func
                from_func[graph_field.func].append((graph_field, query_field))
            else:
                to_func[graph_field.name] = sq
                from_sq[sq].append((graph_field, query_field))

        # schedule fields resolve
        to_fut = {}
        for func, func_fields in from_func.items():
            query_fields = [query.Field(qf.name, options=get_options(gf, qf))
                            if gf.options else qf for gf, qf in func_fields]

            if ids is not None:
                fut = self._submit(func, query_fields, ids)
            else:
                fut = self._submit(func, query_fields)

            to_fut[func] = fut
            self._queue.add_callback(fut, (
                lambda _query_fields=query_fields, _result_proc=fut.result:
                store_fields(self._result, node, _query_fields, ids,
                             _result_proc())
            ))

        for func, func_fields in from_sq.items():
            assert ids is not None, 'Sub-queries without ids not supported yet'
            graph_fields, query_fields = zip(*func_fields) \
                if func_fields else ([], [])

            options = [[v for _, v in _yield_options(gf, qf)]
                       for gf, qf in func_fields]

            task_set = self._queue.fork(self._task_set)
            result_proc = func(graph_fields, query_fields, options, ids,
                               self._queue, self._ctx, task_set)

            to_fut[func] = task_set
            self._queue.add_callback(task_set, (
                lambda _query_fields=query_fields, _result_proc=result_proc:
                store_fields(self._result, node, _query_fields, ids,
                             _result_proc())
            ))

        # schedule link resolve
        for graph_link, query_link in links:
            if graph_link.requires:
                fut = to_fut[to_func[graph_link.requires]]
                self._queue.add_callback(fut, (
                    lambda _gl=graph_link, _ql=query_link:
                    self._process_node_link(node, _gl, _ql, ids)
                ))
            else:
                if graph_link.options:
                    options = get_options(graph_link, query_link)
                    fut = self._submit(graph_link.func, options)
                else:
                    fut = self._submit(graph_link.func)
                self._queue.add_callback(fut, (
                    lambda _fut=fut, _gl=graph_link, _qe=query_link.node:
                    self.process_link(node, _gl, _qe, ids, _fut.result())
                ))

    def _process_node_link(self, node, graph_link, query_link, ids):
        reqs = link_reqs(self._result, node, graph_link, ids)
        if graph_link.options:
            options = get_options(graph_link, query_link)
            fut = self._submit(graph_link.func, reqs, options)
        else:
            fut = self._submit(graph_link.func, reqs)
        self._queue.add_callback(fut, (
            lambda:
            self.process_link(node, graph_link, query_link.node, ids,
                              fut.result())
        ))

    def process_link(self, node, graph_link, query_node, ids, result):
        if inspect.isgenerator(result):
            result = list(result)
        store_links(self._result, node, graph_link, ids, result)
        from_list = ids is not None and graph_link.requires is not None
        to_ids = link_result_to_ids(from_list, graph_link.type_enum, result)
        if to_ids:
            self.process_node(self.graph.nodes_map[graph_link.node], query_node,
                              to_ids)


def pass_context(func):
    func.__pass_context__ = True
    return func


def _do_pass_context(func):
    return getattr(func, '__pass_context__', False)


class Context(object):

    def __init__(self, mapping):
        self.__mapping = mapping

    def __getitem__(self, item):
        try:
            return self.__mapping[item]
        except KeyError:
            raise KeyError('Context variable {!r} is not specified '
                           'in the query context'.format(item))


class Engine(object):

    def __init__(self, executor):
        self.executor = executor

    def execute(self, graph, pattern, ctx=None):
        queue = Queue(self.executor)
        task_set = queue.fork(None)
        q = Query(queue, task_set, graph, Context(ctx or {}))
        q.process_node(q.graph.root, pattern, None)
        return self.executor.process(queue, q)
