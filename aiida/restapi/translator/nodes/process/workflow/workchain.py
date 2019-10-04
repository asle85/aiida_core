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
Translator for workchain node
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from aiida.restapi.translator.nodes.process.process import ProcessTranslator


class WorkChainTranslator(ProcessTranslator):
    """
    Translator relative to resource 'workchain' and aiida class Process
    """

    # A label associated to the present class (coincides with the resource name)
    __label__ = 'workchain'
    # The AiiDA class one-to-one associated to the present class
    from aiida.orm import WorkChainNode
    _aiida_class = WorkChainNode
    # The string name of the AiiDA class
    _aiida_type = 'process.workflow.workchain.WorkChainNode'

    _result_type = __label__

    def __init__(self, **kwargs):
        """
        Initialise the parameters.
        Create the basic query_help
        """
        # basic query_help object
        super(WorkChainTranslator, self).__init__(Class=self.__class__, **kwargs)

    @staticmethod
    def get_derived_properties(node):
        """
        Generic function extended for workchain. Currently
        it is not implemented.

        :param node: node object
        :returns: raise RestFeatureNotAvailable exception
        """

        from aiida.restapi.common.exceptions import RestFeatureNotAvailable

        raise RestFeatureNotAvailable('This endpoint is not available for WorkChains.')

    @staticmethod
    def get_downloadable_data(node, download_format=None):
        """
        Generic function extended for workchain processes. Currently
        it is not implemented.

        :param node: node object that has to be downloaded
        :param download_format: file extension format
        :returns: raise RestFeatureNotAvailable exception
        """

        from aiida.restapi.common.exceptions import RestFeatureNotAvailable

        raise RestFeatureNotAvailable('This endpoint is not available for WorkChains.')