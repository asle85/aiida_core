# -*- coding: utf-8 -*-
"""Utility functions to work with node "full types" which are unique node identifiers."""
from __future__ import absolute_import
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
        filters['process_type'] = process_type

    return filters


def load_entry_point_from_full_type(full_type):
    """Return the loaded entry point for the given `full_type` unique node identifier.

    :param full_type: the `full_type` unique node identifier
    :raises ValueError: if the `full_type` is invalid
    :raises TypeError: if the `full_type` is not a string type
    :raises EntryPointError:
    """
    from aiida.common import EntryPointError
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

        base_name = node_type.lstrip(prefix)
        entry_point_name = base_name.rsplit('.', 2)[0]

        try:
            return load_entry_point('aiida.data', entry_point_name)
        except EntryPointError:
            raise EntryPointError('could not load entry point `{}`'.format(process_type))

    # Here we are dealing with a `ProcessNode` with a `process_type` that is not an entry point string.
    # Which means it is most likely a full module path (the fallback option) and we cannot necessarily load the
    # class from this. We could try with `importlib` but not sure that we should
    raise EntryPointError('entry point of the given full type cannot be loaded')


def get_existing_full_types():
    """Return a dictionary of the set of node type identifiers present in the database.

    A type identifier is the `Node.node_type` and `Node.process_type` concatenated by a special character. Each type
    identifier returned in the result will be mapped onto a dictionary of metadata, with for example a short human
    readable label.

    :return: mapping of unique node type identifier onto its metadata
    """
    from aiida import orm
    from aiida.common import EntryPointError
    from aiida.plugins.entry_point import is_valid_entry_point_string, load_entry_point_from_string

    result = [{'namespace': 'data', 'subspaces': []}, {'namespace': 'process', 'subspaces': []}]

    builder = orm.QueryBuilder().append(orm.Node, project=['node_type', 'process_type'])
    unique = {(node_type, process_type if process_type else '') for node_type, process_type in builder.all()}

    for node_type, process_type in unique:

        full_type = construct_full_type(node_type, process_type)
        label = None

        if not node_type and not process_type:
            continue

        if not process_type:
            label = node_type.rsplit('.', 2)[-2]

        elif process_type and is_valid_entry_point_string(process_type):
            try:
                plugin = load_entry_point_from_string(process_type)
                label = plugin.__name__
            except EntryPointError:
                label = process_type
        else:
            label = process_type.rsplit('.', 1)[-1]

        if node_type.startswith('data.'):
            result[0]['subspaces'].append({
                'full_type': full_type,
                'label': label,
            })
        elif node_type.startswith('process.'):
            result[1]['subspaces'].append({
                'full_type': full_type,
                'label': label,
            })
        else:
            raise RuntimeError('corrupt node type')

    return result
