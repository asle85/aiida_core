# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""Translator for node"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from aiida.common.exceptions import InputValidationError, ValidationError, \
    InvalidOperation
from aiida.restapi.common.exceptions import RestValidationError
from aiida.restapi.translator.base import BaseTranslator
from aiida.manage.manager import get_manager
from aiida import orm


class NodeTranslator(BaseTranslator):
    # pylint: disable=too-many-instance-attributes,anomalous-backslash-in-string,too-many-arguments,too-many-branches,fixme
    """
    Translator relative to resource 'nodes' and aiida class Node
    """

    # A label associated to the present class (coincides with the resource name)
    __label__ = 'nodes'

    # The AiiDA class one-to-one associated to the present class
    _aiida_class = orm.Node

    # The string name of the AiiDA class
    _aiida_type = 'node.Node'

    # If True (False) the corresponding AiiDA class has (no) uuid property
    _has_uuid = True

    _result_type = __label__

    _content_type = None

    _alist = None
    _nalist = None
    _elist = None
    _nelist = None
    _download_format = None
    _download = None
    _filename = None
    _rtype = None

    def __init__(self, Class=None, **kwargs):
        """
        Initialise the parameters.
        Create the basic query_help
        """

        # Assume default class is this class (cannot be done in the
        # definition as it requires self)
        if Class is None:
            Class = self.__class__

        # basic initialization
        super(NodeTranslator, self).__init__(Class=Class, **kwargs)

        self._default_projections = ['id', 'label', 'node_type', 'ctime', 'mtime', 'uuid', 'user_id']
        self._default_user_projections = ['email']

        ## node schema
        # All the values from column_order must present in additional info dict
        # Note: final schema will contain details for only the fields present in column order
        self._schema_projections = {
            'column_order':
            ['id', 'label', 'node_type', 'ctime', 'mtime', 'uuid', 'user_id', 'user_email', 'attributes', 'extras'],
            'additional_info': {
                'id': {
                    'is_display': True
                },
                'label': {
                    'is_display': False
                },
                'node_type': {
                    'is_display': True
                },
                'ctime': {
                    'is_display': True
                },
                'mtime': {
                    'is_display': True
                },
                'uuid': {
                    'is_display': False
                },
                'user_id': {
                    'is_display': False
                },
                'user_email': {
                    'is_display': True
                },
                'attributes': {
                    'is_display': False
                },
                'extras': {
                    'is_display': False
                }
            }
        }

        # Inspect the subclasses of NodeTranslator, to avoid hard-coding
        # (should resemble the following tree)
        """
                                              /- CodeTranslator
                                             /
                                            /- KpointsTranslator
                                           /
                           /- DataTranslator -- StructureTranslator
                          /                \
                         /                  \- BandsTranslator
                        /
        NodeTranslator
                        \
                         \- CalculationTranslator
        """

        self._subclasses = self._get_subclasses()
        self._backend = get_manager().get_backend()

    def set_query_type(
        self,
        query_type,
        alist=None,
        nalist=None,
        elist=None,
        nelist=None,
        download_format=None,
        download=None,
        filename=None,
        rtype=None,
    ):
        """
        sets one of the mutually exclusive values for self._result_type and
        self._content_type.

        :param query_type:(string) the value assigned to either variable.
        """

        if query_type == 'default':
            pass
        elif query_type == 'incoming':
            self._result_type = 'with_outgoing'
        elif query_type == 'outgoing':
            self._result_type = 'with_incoming'
        elif query_type == 'attributes':
            self._content_type = 'attributes'
            self._alist = alist
            self._nalist = nalist
        elif query_type == 'extras':
            self._content_type = 'extras'
            self._elist = elist
            self._nelist = nelist
        elif query_type == 'derived_properties':
            self._content_type = 'derived_properties'
        elif query_type == 'download_formats':
            self._content_type = 'download_formats'
        elif query_type == 'download':
            self._content_type = 'download'
            self._download_format = download_format
            self._download = download
        elif query_type == 'comments':
            self._content_type = 'comments'
        elif query_type == 'repo_list':
            self._content_type = 'repo_list'
            self._filename = filename
        elif query_type == 'repo_contents':
            self._content_type = 'repo_contents'
            self._filename = filename
        elif query_type == 'retrieved_inputs':
            self._content_type = 'retrieved_inputs'
            self._filename = filename
            self._rtype = rtype
        elif query_type == 'retrieved_outputs':
            self._content_type = 'retrieved_outputs'
            self._filename = filename
            self._rtype = rtype
        else:
            raise InputValidationError('invalid result/content value: {}'.format(query_type))

        # Add input/output relation to the query help
        if self._result_type != self.__label__:
            self._query_help['path'].append({
                'entity_type': ('node.Node.', 'data.Data.'),
                'tag': self._result_type,
                self._result_type: self.__label__
            })

    def set_query(
        self,
        filters=None,
        orders=None,
        projections=None,
        query_type=None,
        node_id=None,
        alist=None,
        nalist=None,
        elist=None,
        nelist=None,
        download_format=None,
        download=None,
        filename=None,
        rtype=None,
        attributes=None,
        attributes_filter=None,
        extras=None,
        extras_filter=None
    ):
        """
        Adds filters, default projections, order specs to the query_help,
        and initializes the qb object

        :param filters: dictionary with the filters
        :param orders: dictionary with the order for each tag
        :param projections: dictionary with the projection. It is discarded
            if query_type=='attributes'/'extras'
        :param query_type: (string) specify the result or the content ("attr")
        :param id: (integer) id of a specific node
        :param alist: list of attributes queried for node
        :param nalist: list of attributes, returns all attributes except this for node
        :param elist: list of extras queries for node
        :param nelist: list of extras, returns all extras except this for node
        :param format: file format to download e.g. cif, xyz
        :param filename: name of the file to return its content
        :param rtype: return type of the file
        :param attributes: flag to show attributes for nodes
        :param attributes_filter: list of attributes to query
        :param extras: flag to show extras for nodes
        :param extras_filter: list of extras to query
        """

        ## Check the compatibility of query_type and id
        if query_type != 'default' and id is None:
            raise ValidationError(
                'non default result/content can only be '
                'applied to a specific node (specify an id)'
            )

        ## Set the type of query
        self.set_query_type(
            query_type,
            alist=alist,
            nalist=nalist,
            elist=elist,
            nelist=nelist,
            download_format=download_format,
            download=download,
            filename=filename,
            rtype=rtype
        )

        ## Define projections
        if self._content_type is not None:
            # Use '*' so that the object itself will be returned.
            # In get_results() we access attributes/extras by
            # calling the attributes/extras.
            projections = ['*']
        else:
            pass  # i.e. use the input parameter projection

        # TODO this actually works, but the logic is a little bit obscure.
        # Make it clearer
        if self._result_type is not self.__label__:
            projections = self._default_projections

        super(NodeTranslator, self).set_query(
            filters=filters,
            orders=orders,
            projections=projections,
            node_id=node_id,
            attributes=attributes,
            attributes_filter=attributes_filter,
            extras=extras,
            extras_filter=extras_filter
        )

    def _get_content(self):
        """
        Used by get_results() in case of endpoint include "content" option
        :return: data: a dictionary containing the results obtained by
        running the query
        """
        # pylint: disable=too-many-statements

        if not self._is_qb_initialized:
            raise InvalidOperation('query builder object has not been initialized.')

        # Count the total number of rows returned by the query (if not already done)
        if self._total_count is None:
            self.count()

        # If count==0 return
        if self._total_count == 0:
            return {}

        # otherwise ...
        node = self.qbobj.first()[1]

        # content/attributes
        if self._content_type == 'attributes':
            # Get all attrs if nalist and alist are both None
            if self._alist is None and self._nalist is None:
                data = {self._content_type: node.attributes}
            # Get all attrs except those contained in nalist
            elif self._alist is None and self._nalist is not None:
                attrs = {}
                for key in node.attributes.keys():
                    if key not in self._nalist:
                        attrs[key] = node.get_attribute(key)
                data = {self._content_type: attrs}
            # Get all attrs contained in alist
            elif self._alist is not None and self._nalist is None:
                attrs = {}
                for key in node.attributes.keys():
                    if key in self._alist:
                        attrs[key] = node.get_attribute(key)
                data = {self._content_type: attrs}
            else:
                raise RestValidationError('you cannot specify both alist and nalist')
        # content/extras
        elif self._content_type == 'extras':

            # Get all extras if nelist and elist are both None
            if self._elist is None and self._nelist is None:
                data = {self._content_type: node.extras}

            # Get all extras except those contained in nelist
            elif self._elist is None and self._nelist is not None:
                extras = {}
                for key in node.extras.keys():
                    if key not in self._nelist:
                        extras[key] = node.get_extra(key)
                data = {self._content_type: extras}

            # Get all extras contained in elist
            elif self._elist is not None and self._nelist is None:
                extras = {}
                for key in node.extras.keys():
                    if key in self._elist:
                        extras[key] = node.get_extra(key)
                data = {self._content_type: extras}

            else:
                raise RestValidationError('you cannot specify both elist and nelist')

        # Data needed for visualization appropriately serialized (this
        # actually works only for data derived classes)
        # TODO refactor the code so to have this option only in data and
        # derived classes
        elif self._content_type == 'derived_properties':
            data = {self._content_type: self.get_derived_properties(node)}

        elif self._content_type == 'download':
            # In this we do not return a dictionary but download the file in
            # specified format if available
            data = {self._content_type: self.get_downloadable_data(node, self._download_format)}

        elif self._content_type == 'download_formats':
            # returns the possible download formats for given node
            data = {self._content_type: self.get_download_formats(node)}

        elif self._content_type == 'retrieved_inputs':
            # This type is only available for calc nodes. In case of job calc it
            # returns calc incoming prepared to submit calc on the cluster else []
            data = {self._content_type: self.get_retrieved_inputs(node, self._filename, self._rtype)}

        elif self._content_type == 'retrieved_outputs':
            # This type is only available for calc nodes. In case of job calc it
            # returns calc outgoing retrieved from the cluster else []
            data = {self._content_type: self.get_retrieved_outputs(node, self._filename, self._rtype)}

        elif self._content_type == 'repo_list':
            # return the node comments
            data = {self._content_type: self.get_repo_list(node, self._filename)}

        elif self._content_type == 'repo_contents':
            # return the node comments
            data = {self._content_type: self.get_repo_contents(node, self._filename)}

        elif self._content_type == 'comments':
            # return the node comments
            data = {self._content_type: self.get_comments(node)}

        else:
            raise ValidationError('invalid content type')

        return data

    def _get_subclasses(self, parent=None, parent_class=None, recursive=True):
        """
        Import all submodules of the package containing the present class.
        Includes subpackages recursively, if specified.

        :param parent: package/class.
            If package looks for the classes in submodules.
            If class, first looks for the package where it is contained
        :param parent_class: class of which to look for subclasses
        :param recursive: True/False (go recursively into submodules)
        """

        import pkgutil
        import imp
        import inspect
        import os

        # If no parent class is specified set it to self.__class
        parent = self.__class__ if parent is None else parent

        # Suppose parent is class
        if inspect.isclass(parent):

            # Set the package where the class is contained
            classfile = inspect.getfile(parent)
            package_path = os.path.dirname(classfile)

            # If parent class is not specified, assume it is the parent
            if parent_class is None:
                parent_class = parent

        # Suppose parent is a package (directory containing __init__.py).
        # Check if it contains attribute __path__
        elif inspect.ismodule(parent) and hasattr(parent, '__path__'):

            # Assume path is one element list
            package_path = parent.__path__[0]

            # if parent is a package, parent_class cannot be None
            if parent_class is None:
                raise TypeError('argument parent_class cannot be None')

                # Recursively check the subpackages
        results = {}

        for _, name, is_pkg in pkgutil.walk_packages([package_path]):
            # N.B. pkgutil.walk_package requires a LIST of paths.

            full_path_base = os.path.join(package_path, name)

            if is_pkg:
                app_module = imp.load_package(full_path_base, full_path_base)
            else:
                full_path = full_path_base + '.py'
                # I could use load_module but it takes lots of arguments,
                # then I use load_source
                app_module = imp.load_source('rst' + name, full_path)

            # Go through the content of the module
            if not is_pkg:
                for fname, obj in inspect.getmembers(app_module):
                    if inspect.isclass(obj) and issubclass(obj, parent_class):
                        results[fname] = obj
            # Look in submodules
            elif is_pkg and recursive:
                results.update(self._get_subclasses(parent=app_module, parent_class=parent_class))
        return results

    def get_derived_properties(self, node):
        """
        Generic function to get the derived properties of the node.
        Actual definition is in child classes as the content to be
        returned depends on the plugin specific
        to the resource

        :param node: node object that has to be visualized
        :returns: derived properties of the node

        If this method is called by Node resource it will look for the type
        of object and invoke the correct method in the lowest-compatible
        subclass
        """

        # Look for the translator associated to the class of which this node
        # is instance
        tclass = type(node)

        for subclass in self._subclasses.values():
            if subclass._aiida_type.split('.')[-1] == tclass.__name__:  # pylint: disable=protected-access
                lowtrans = subclass

        derived_properties = lowtrans.get_derived_properties(node)

        return derived_properties

    @staticmethod
    def get_download_formats(node):
        """
        returns the list of possible formats in which give node can be downloaded.
        :param node: node object
        """

        try:
            return node.get_export_formats()
        except AttributeError:
            from aiida.restapi.common.exceptions import RestFeatureNotAvailable
            raise RestFeatureNotAvailable('This endpoint is not available for node type {}'.format(node.node_type))

    @staticmethod
    def get_all_download_formats():
        """
        returns dict of possible node formats for all available node types
        """

        def get_all_subclasses(class_name, all_subclasses):
            """ returns all of all subclasses for given class """
            for subclass in class_name.__subclasses__():
                all_subclasses.append(subclass)
                if subclass.__subclasses__():
                    get_all_subclasses(subclass, all_subclasses)
            return all_subclasses

        from aiida.orm import Data
        all_subclasses = get_all_subclasses(Data, [])

        all_formats = {}
        for cls in all_subclasses:
            ntype = cls.class_node_type.split('.')[-2]
            try:
                available_formats = cls.get_export_formats()
                if available_formats:
                    all_formats[ntype] = available_formats
            except AttributeError:
                pass
        return all_formats

    def get_downloadable_data(self, node, download_format=None):
        """
        Generic function to download file in specified format.
        Actual definition is in child classes as the content to be
        returned and its format depends on the download plugin specific
        to the resource

        :param node: node object
        :param download_format: file extension format
        :returns: data in selected format to download

        If this method is called by Node resource it will look for the type
        of object and invoke the correct method in the lowest-compatible
        subclass
        """

        # Look for the translator associated to the class of which this node
        # is instance
        tclass = type(node)
        for subclass in self._subclasses.values():
            if subclass._aiida_type.split('.')[-1] == tclass.__name__:  # pylint: disable=protected-access
                lowtrans = subclass

        downloadable_data = lowtrans.get_downloadable_data(node, download_format=download_format)

        return downloadable_data

    @staticmethod
    def get_retrieved_inputs(node, filename=None, rtype=None):
        """
        Generic function to return output of calc inputls verdi command.
        Actual definition is in child classes as the content to be
        returned and its format depends on the plugin specific
        to the resource

        :param node: node object
        :returns: list of calc inputls command
        """
        # pylint: disable=unused-argument
        return []

    @staticmethod
    def get_retrieved_outputs(node, filename=None, rtype=None):
        """
        Generic function to return output of calc outputls verdi command.
        Actual definition is in child classes as the content to be
        returned and its format depends on the plugin specific
        to the resource

        :param node: node object
        :returns: list of calc outputls command
        """
        # pylint: disable=unused-argument
        return []

    @staticmethod
    def get_repo_list(node, filename=''):
        """
        Every node in AiiDA is having repo folder.
        This function returns the metadata using get_object() method
        :param node: node object
        :param filename: folder or file name (optional)
        :return: folder list / file metadata
        """
        from aiida.orm.utils.repository import File
        try:
            flist = node.list_objects(filename)
        except NotADirectoryError:
            flist = node.get_object(filename)
            if isinstance(flist, File):
                flist = [flist]
        response = []
        for fobj in flist:
            response.append({'name': fobj.name, 'type': fobj.type.name})
        return response

    @staticmethod
    def get_repo_contents(node, filename=''):
        """
        Every node in AiiDA is having repo folder.
        This function returns the metadata using get_object() method
        :param node: node object
        :param filename: folder or file name (optional)
        :return: folder list / file metadata
        """
        from aiida.restapi.common.exceptions import RestInputValidationError
        if filename:
            try:
                data = node.get_object_content(filename)
                return data
            except IsADirectoryError:
                raise RestInputValidationError('It is a directory. Please pass filename.')
            except FileNotFoundError:
                raise RestInputValidationError('No such file is present')
        raise RestInputValidationError('filename is not provided')

    @staticmethod
    def get_comments(node):
        """
        :param node: node object
        :return: node comments
        """
        comments = node.get_comments()
        response = []
        for cobj in comments:
            response.append({
                'created_time': cobj.ctime,
                'modified_time': cobj.mtime,
                'user': cobj.user.first_name + ' ' + cobj.user.last_name,
                'message': cobj.content
            })
        return response

    @staticmethod
    def get_file_content(node, file_name):
        """
        It reads the file from directory and returns its content.

        Instead of using "send_from_directory" from flask, this method is written
        because in next aiida releases the file can be stored locally or in object storage.

        :param node: aiida folderData node which contains file
        :param file_name: name of the file to return its contents
        :return:
        """
        import os
        file_parts = file_name.split(os.sep)

        if len(file_parts) > 1:
            file_name = file_parts.pop()
            for folder in file_parts:
                node = node.get_subfolder(folder)

        with node.open(file_name) as fobj:
            return fobj.read()

    def get_results(self):
        """
        Returns either a list of nodes or details of single node from database

        :return: either a list of nodes or the details of single node
            from the database
        """
        if self._content_type is not None:
            return self._get_content()

        return super(NodeTranslator, self).get_results()

    def get_statistics(self, user_pk=None):
        """Return statistics for a given node"""

        qmanager = self._backend.query_manager
        return qmanager.get_creation_statistics(user_pk=user_pk)

    def get_types(self):
        """
        return available distinct types of nodes from database
        """
        from aiida.orm.querybuilder import QueryBuilder

        qb_obj = QueryBuilder()
        qb_obj.append(self._aiida_class, project=['node_type'])
        qb_response = qb_obj.distinct().all()
        results = {}
        if qb_response:
            for ntype in qb_response:
                ntype = ntype[0]
                ntype_parts = ntype.split('.')
                if ntype_parts:
                    dict_key = ntype_parts[0]
                    if dict_key not in results.keys():
                        results[dict_key] = []
                    results[dict_key].append(ntype)

        for key, values in results.items():
            results[key] = sorted(values)
        return results

    def get_io_tree(self, uuid_pattern, tree_in_limit, tree_out_limit):
        # pylint: disable=too-many-statements,too-many-locals
        """
        json data to display nodes in tree format
        :param uuid_pattern: main node uuid
        :return: json data to display node tree
        """
        from aiida.orm.querybuilder import QueryBuilder
        from aiida.orm import Node

        def get_node_description(node):
            """
            Get the description of the node.
            CalcJobNodes migrated from AiiDA < 1.0.0 do not have a valid CalcJobState,
            in this case the function returns as description the type of the node (CalcJobNode)
            :param node: node object
            :return: description of the node
            """
            try:
                description = node.get_description()
            except ValueError:
                description = node.node_type.split('.')[-2]
            return description

        # Check whether uuid_pattern identifies a unique node
        self._check_id_validity(uuid_pattern)

        qb_obj = QueryBuilder()
        qb_obj.append(Node, tag='main', project=['*'], filters=self._id_filter)

        nodes = []

        if qb_obj.count() > 0:
            main_node = qb_obj.first()[0]
            pk = main_node.pk
            uuid = main_node.uuid
            nodetype = main_node.node_type
            nodelabel = main_node.label
            description = get_node_description(main_node)
            ctime = main_node.ctime
            mtime = main_node.mtime

            nodes.append({
                'ctime': ctime,
                'mtime': mtime,
                'id': pk,
                'uuid': uuid,
                'node_type': nodetype,
                'node_label': nodelabel,
                'description': description,
                'incoming': [],
                'outgoing': []
            })

        # get all incoming
        qb_obj = QueryBuilder()
        qb_obj.append(Node, tag='main', project=['*'], filters=self._id_filter)
        qb_obj.append(Node, tag='in', project=['*'], edge_project=['label', 'type'],
                      with_outgoing='main').order_by({'in': [{
                          'id': {
                              'order': 'asc'
                          }
                      }]})
        if tree_in_limit is not None:
            qb_obj.limit(tree_in_limit)

        sent_no_of_incomings = qb_obj.count()

        if sent_no_of_incomings > 0:
            for node_input in qb_obj.iterdict():
                node = node_input['in']['*']
                pk = node.pk
                linklabel = node_input['main--in']['label']
                linktype = node_input['main--in']['type']
                uuid = node.uuid
                nodetype = node.node_type
                nodelabel = node.label
                description = get_node_description(node)
                node_ctime = node.ctime
                node_mtime = node.mtime

                nodes[0]['incoming'].append({
                    'ctime': node_ctime,
                    'mtime': node_mtime,
                    'id': pk,
                    'uuid': uuid,
                    'node_type': nodetype,
                    'node_label': nodelabel,
                    'description': description,
                    'link_label': linklabel,
                    'link_type': linktype
                })

        # get all outgoing
        qb_obj = QueryBuilder()
        qb_obj.append(Node, tag='main', project=['*'], filters=self._id_filter)
        qb_obj.append(Node, tag='out', project=['*'], edge_project=['label', 'type'],
                      with_incoming='main').order_by({'out': [{
                          'id': {
                              'order': 'asc'
                          }
                      }]})
        if tree_out_limit is not None:
            qb_obj.limit(tree_out_limit)

        sent_no_of_outgoings = qb_obj.count()

        if sent_no_of_outgoings > 0:
            for output in qb_obj.iterdict():
                node = output['out']['*']
                pk = node.pk
                linklabel = output['main--out']['label']
                linktype = output['main--out']['type']
                uuid = node.uuid
                nodetype = node.node_type
                nodelabel = node.label
                description = get_node_description(node)
                node_ctime = node.ctime
                node_mtime = node.mtime

                nodes[0]['outgoing'].append({
                    'ctime': node_ctime,
                    'mtime': node_mtime,
                    'id': pk,
                    'uuid': uuid,
                    'node_type': nodetype,
                    'node_label': nodelabel,
                    'description': description,
                    'link_label': linklabel,
                    'link_type': linktype
                })

        # count total no of nodes
        builder = QueryBuilder()
        builder.append(Node, tag='main', project=['id'], filters=self._id_filter)
        builder.append(Node, tag='in', project=['id'], with_outgoing='main')
        total_no_of_incomings = builder.count()

        builder = QueryBuilder()
        builder.append(Node, tag='main', project=['id'], filters=self._id_filter)
        builder.append(Node, tag='out', project=['id'], with_incoming='main')
        total_no_of_outgoings = builder.count()

        metadata = [{
            'total_no_of_incomings': total_no_of_incomings,
            'total_no_of_outgoings': total_no_of_outgoings,
            'sent_no_of_incomings': sent_no_of_incomings,
            'sent_no_of_outgoings': sent_no_of_outgoings
        }]

        return {'nodes': nodes, 'metadata': metadata}
