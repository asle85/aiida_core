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
Translator for process node
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from aiida.restapi.translator.nodes.node import NodeTranslator


class ProcessTranslator(NodeTranslator):
    """
    Translator relative to resource 'data' and aiida class `~aiida.orm.nodes.data.data.Data`
    """

    # A label associated to the present class (coincides with the resource name)
    __label__ = 'process'
    # The AiiDA class one-to-one associated to the present class
    from aiida.orm import ProcessNode
    _aiida_class = ProcessNode
    # The string name of the AiiDA class
    _aiida_type = 'process.ProcessNode'

    _result_type = __label__

    def __init__(self, Class=None, **kwargs):
        """
        Initialise the parameters.
        Create the basic query_help
        """

        # Assume default class is this class (cannot be done in the
        # definition as it requires self)
        if Class is None:
            Class = self.__class__

        super(ProcessTranslator, self).__init__(Class=Class, **kwargs)

    @staticmethod
    def get_report(process):
        """Show the log report for one or multiple processes."""
        from aiida.cmdline.utils.common import get_calcjob_report, get_workchain_report, get_process_function_report
        from aiida.orm import CalcJobNode, WorkChainNode, CalcFunctionNode, WorkFunctionNode

        if isinstance(process, CalcJobNode):
            report = get_calcjob_report(process)
        elif isinstance(process, WorkChainNode):
            report = get_workchain_report(process) #levelname, indent_size, max_depth??
        elif isinstance(process, (CalcFunctionNode, WorkFunctionNode)):
            report = get_process_function_report(process)
        else:
            report = 'Nothing to show for node type {}'.format(process.__class__)

        return report

    @staticmethod
    def get_status(process):
        """Print the status of one or multiple processes."""
        from aiida.cmdline.utils.ascii_vis import format_call_graph

        graph = format_call_graph(process)
        return graph
