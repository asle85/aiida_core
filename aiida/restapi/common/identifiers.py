# -*- coding: utf-8 -*-
"""Utility functions to work with node "full types" which are unique node identifiers."""
from __future__ import absolute_import

import collections
import six

FULL_TYPE_CONCATENATOR = '|'
LIKE_OPERATOR_CHARACTER = '%'


def validate_full_type(full_type):
    """Validate that the `full_type` is a valid full type unique node identifier.

    :param full_type: a `Node` full type
    :raises ValueError: if the `full_type` is invalid
    :raises TypeError: if the `full_type` is not a string type
    """
    from aiida.common.lang import type_check

    type_check(full_type, six.string_types)

    if FULL_TYPE_CONCATENATOR not in full_type:
        raise ValueError(
            'full type `{}` does not include the required concatenator symbol `{}`.'.format(
                full_type, FULL_TYPE_CONCATENATOR
            )
        )


def construct_full_type(node_type, process_type):
    """Return the full type, which uniquely identifies any `Node` with the given `node_type` and `process_type`.

    :param node_type: the `node_type` of the `Node`
    :param process_type: the `process_type` of the `Node`
    :return: the full type, which is a unique identifier
    """
    if node_type is None:
        process_type = ''

    if process_type is None:
        process_type = ''

    return '{}{}{}'.format(node_type, FULL_TYPE_CONCATENATOR, process_type)


def get_full_type_filters(full_type):
    """Return the `QueryBuilder` filters that will return all `Nodes` identified by the given `full_type`.

    :param full_type: the `full_type` unique node identifier
    :return: dictionary of filters to be passed for the `filters` keyword in `QueryBuilder.append`
    :raises ValueError: if the `full_type` is invalid
    :raises TypeError: if the `full_type` is not a string type
    """
    validate_full_type(full_type)

    filters = {}
    node_type, process_type = full_type.split(FULL_TYPE_CONCATENATOR)

    for entry in (node_type, process_type):
        if entry.count(LIKE_OPERATOR_CHARACTER) > 1:
            raise ValueError('full type component `{}` contained more than one like-operator character'.format(entry))

        if LIKE_OPERATOR_CHARACTER in entry and entry[-1] != LIKE_OPERATOR_CHARACTER:
            raise ValueError('like-operator character in full type component `{}` is not at the end'.format(entry))

    if LIKE_OPERATOR_CHARACTER in node_type:
        filters['node_type'] = {'like': node_type}
    else:
        filters['node_type'] = node_type

    if LIKE_OPERATOR_CHARACTER in process_type:
        filters['process_type'] = {'like': process_type}
    else:
        if process_type:
            filters['process_type'] = process_type

    return filters


def load_entry_point_from_full_type(full_type):
    """Return the loaded entry point for the given `full_type` unique node identifier.

    :param full_type: the `full_type` unique node identifier
    :raises ValueError: if the `full_type` is invalid
    :raises TypeError: if the `full_type` is not a string type
    :raises :class:`~aiida.common.exceptions.EntryPointError`
    """
    from aiida.common import EntryPointError
    from aiida.common.utils import strip_prefix
    from aiida.plugins.entry_point import is_valid_entry_point_string, load_entry_point, load_entry_point_from_string

    prefix = 'data.'

    validate_full_type(full_type)

    node_type, process_type = full_type.split(FULL_TYPE_CONCATENATOR)

    if is_valid_entry_point_string(process_type):

        try:
            return load_entry_point_from_string(process_type)
        except EntryPointError:
            raise EntryPointError('could not load entry point `{}`'.format(process_type))

    elif node_type.startswith(prefix):

        base_name = strip_prefix(node_type, prefix)
        entry_point_name = base_name.rsplit('.', 2)[0]

        try:
            return load_entry_point('aiida.data', entry_point_name)
        except EntryPointError:
            raise EntryPointError('could not load entry point `{}`'.format(process_type))

    # Here we are dealing with a `ProcessNode` with a `process_type` that is not an entry point string.
    # Which means it is most likely a full module path (the fallback option) and we cannot necessarily load the
    # class from this. We could try with `importlib` but not sure that we should
    raise EntryPointError('entry point of the given full type cannot be loaded')


class Namespace(collections.MutableMapping):
    """Namespace that can be used to map the node class hierarchy."""

    NAMESPACE_SEPARATOR = '.'

    def __str__(self):
        import json
        return json.dumps(self.get_description(), sort_keys=True, indent=4)

    def __init__(self, namespace, path=None, label=None, full_type=None):
        """Construct a new node class namespace."""
        # pylint: disable=super-init-not-called
        self._namespace = namespace
        self._label = label
        self._path = path if path else namespace
        self._full_type = self._infer_full_type(full_type)
        self._subspaces = {}

    def _infer_full_type(self, full_type):
        """Infer the full type based on the current namespace path and the given full type of the leaf."""
        from aiida.common.utils import strip_prefix

        if full_type or self._path is None:
            return full_type

        full_type = strip_prefix(self._path, 'node.')

        return full_type + '.{query_character}{concatenator}{query_character}'.format(
            query_character=LIKE_OPERATOR_CHARACTER, concatenator=FULL_TYPE_CONCATENATOR
        )

    def __iter__(self):
        return self._subspaces.__iter__()

    def __len__(self):
        return len(self._subspaces)

    def __delitem__(self, key):
        del self._subspaces[key]

    def __getitem__(self, key):
        return self._subspaces[key]

    def __setitem__(self, key, port):
        self._subspaces[key] = port

    def get_description(self):
        """Return a dictionary with a description of the ports this namespace contains.

        Nested PortNamespaces will be properly recursed and Ports will print their properties in a list

        :returns: a dictionary of descriptions of the Ports contained within this PortNamespace
        """
        result = {
            'namespace': self._namespace,
            'full_type': self._full_type,
            'label': self._label,
            'path': self._path,
            'subspaces': []
        }
        for _, port in self._subspaces.items():
            result['subspaces'].append(port.get_description())

        return result

    def create_namespace(self, name, **kwargs):
        """Create and return a new `Namespace` in this `Namespace`.

        If the name is namespaced, the sub `Namespaces` will be created recursively, except if one of the namespaces is
        already occupied at any level by a Port in which case a ValueError will be thrown

        :param name: name (potentially namespaced) of the port to create and return
        :param kwargs: constructor arguments that will be used *only* for the construction of the terminal Namespace
        :returns: Namespace
        :raises: ValueError if any sub namespace is occupied by a non-Namespace port
        """
        if not isinstance(name, six.string_types):
            raise ValueError('name has to be a string type, not {}'.format(type(name)))

        if not name:
            raise ValueError('name cannot be an empty string')

        namespace = name.split(self.NAMESPACE_SEPARATOR)
        port_name = namespace.pop(0)

        if port_name in self and not isinstance(self[port_name], Namespace):
            raise ValueError("the name '{}' in '{}' already contains a namespace".format(port_name, name))

        path = '{}{}{}'.format(self._path, self.NAMESPACE_SEPARATOR, port_name)

        # If this is True, the (sub) port namespace does not yet exist, so we create it
        if port_name not in self:

            # If there still is a `namespace`, we create a sub namespace, *without* the constructor arguments
            if namespace:
                self[port_name] = self.__class__(port_name, path=path)

            # Otherwise it is the terminal port and we construct *with* the keyword arugments
            else:
                self[port_name] = self.__class__(port_name, path=path, **kwargs)

        if namespace:
            return self[port_name].create_namespace(self.NAMESPACE_SEPARATOR.join(namespace), **kwargs)

        return self[port_name]


def get_node_namespace():
    """Return the full namespace of all available nodes in the current database.

    :return: complete node `Namespace`
    """
    from aiida import orm
    from aiida.common import EntryPointError
    from aiida.plugins.entry_point import (
        is_valid_entry_point_string, load_entry_point_from_string, parse_entry_point_string
    )

    builder = orm.QueryBuilder().append(orm.Node, project=['node_type', 'process_type'])
    unique_types = {(node_type, process_type if process_type else '') for node_type, process_type in builder.all()}

    # First we create a flat list of all "leaf" node types.
    namespaces = []

    for node_type, process_type in unique_types:

        label = None
        namespace = None

        if process_type:
            # Process nodes
            if is_valid_entry_point_string(process_type):
                try:
                    cls = load_entry_point_from_string(process_type)
                    label = cls.__name__
                except EntryPointError:
                    _, label = parse_entry_point_string(process_type)
            else:
                label = process_type.rsplit('.', 1)[-1]

            parts = node_type.rsplit('.', 2)
            namespace = '.'.join(parts[:-2] + [label])
        else:
            # Data nodes
            parts = node_type.rsplit('.', 2)
            try:
                label = parts[-2]
                namespace = '.'.join(parts[:-2])
            except IndexError:
                continue

        full_type = construct_full_type(node_type, process_type)
        namespaces.append((namespace, label, full_type))

    node_namespace = Namespace('node')

    for namespace, label, full_type in namespaces:
        node_namespace.create_namespace(namespace, label=label, full_type=full_type)

    return node_namespace
