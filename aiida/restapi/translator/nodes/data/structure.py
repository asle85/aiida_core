# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""
Translator for structure data
"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from aiida.restapi.translator.nodes.data import DataTranslator
from aiida.restapi.common.exceptions import RestInputValidationError
from aiida.common.exceptions import LicensingException


class StructureDataTranslator(DataTranslator):
    """
    Translator relative to resource 'structures' and aiida class StructureData
    """

    # A label associated to the present class (coincides with the resource name)
    __label__ = 'structures'
    # The AiiDA class one-to-one associated to the present class
    from aiida.orm import StructureData
    _aiida_class = StructureData
    # The string name of the AiiDA class
    _aiida_type = 'data.structure.StructureData'

    _result_type = __label__

    def __init__(self, **kwargs):
        """
        Initialise the parameters.
        Create the basic query_help
        """
        super(StructureDataTranslator, self).__init__(Class=self.__class__, **kwargs)

    @staticmethod
    def get_derived_properties(node):
        """
        Returns: derived properties of the structure.
        """
        response = {}

        # Add extra information
        response['dimensionality'] = node.get_dimensionality()
        response['formula'] = node.get_formula()

        return response

    @staticmethod
    def get_downloadable_data(node, format='cif'):
        """
        Generic function extented for structure data

        :param node: node object that has to be visualized
        :param download_format: file extension format
        :returns: data in selected format to download
        """

        response = {}

        # This check is explicitly added here because sometimes
        # None is passed here as an value for download_format.
        if format is None:
            format = 'cif'

        if format in node.get_export_formats():
            try:
                response['data'] = node._exportcontent(format)[0]  # pylint: disable=protected-access
                response['status'] = 200
                response['filename'] = node.uuid + '_structure.' + format
            except LicensingException as exc:
                response['status'] = 500
                response['data'] = str(exc)

        return response
