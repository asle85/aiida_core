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
Translator for upf data
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from aiida.restapi.translator.nodes.data import DataTranslator
from aiida.restapi.common.exceptions import RestInputValidationError


class UpfDataTranslator(DataTranslator):
    """
    Translator relative to resource 'upfs' and aiida class UpfData
    """

    # A label associated to the present class (coincides with the resource name)
    __label__ = 'upfs'
    # The AiiDA class one-to-one associated to the present class
    from aiida.orm import UpfData
    _aiida_class = UpfData
    # The string name of the AiiDA class
    _aiida_type = 'data.upf.UpfData'

    _result_type = __label__

    def __init__(self, **kwargs):
        """
        Initialise the parameters.
        Create the basic query_help
        """
        super(UpfDataTranslator, self).__init__(Class=self.__class__, **kwargs)

    @staticmethod
    def get_derived_properties(node):
        """
        :param node: node object that has to be visualized
        :returns: raise RestFeatureNotAvailable exception
        """

        from aiida.restapi.common.exceptions import RestFeatureNotAvailable

        raise RestFeatureNotAvailable('This endpoint is not available for upf.')

    @staticmethod
    def get_downloadable_data(node, download_format=None):
        """
        Generic function extended for upf data

        :param node: node object that has to be downloaded
        :param download_format: file extension format
        :returns: data in selected format to download
        """

        response = {}

        filename = node.filename
        try:
            content = node.get_content()
        except IOError:
            error = 'Error in getting {} content'.format(filename)
            raise RestInputValidationError(error)

        response['status'] = 200
        response['data'] = content
        response['filename'] = filename

        return response
