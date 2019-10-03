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
        from aiida.orm import Log, CalcJobNode

        def get_dict(log):
            """Returns the dict representation of log object"""
            return {
                'time': log.time,
                'loggername': log.loggername,
                'levelname': log.levelname,
                'dbnode_id': log.dbnode_id,
                'message': log.message,
            }

        report = {}
        report['logs'] = [get_dict(log) for log in Log.objects.get_logs_for(process)]

        if isinstance(process, CalcJobNode):
            report['scheduler_output'] = process.get_scheduler_stdout()
            report['scheduler_error'] = process.get_scheduler_stderr()

        return report
