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
Translator for computer
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from aiida.restapi.translator.base import BaseTranslator
from aiida import orm


class ComputerTranslator(BaseTranslator):
    """
    Translator relative to resource 'computers' and aiida class Computer
    """
    # A label associated to the present class (coincides with the resource name)
    __label__ = 'computers'
    # The AiiDA class one-to-one associated to the present class
    _aiida_class = orm.Computer
    # The string name of the AiiDA class
    _aiida_type = 'Computer'

    # If True (False) the corresponding AiiDA class has (no) uuid property
    _has_uuid = True

    _result_type = __label__

    def __init__(self, **kwargs):
        """
        Initialise the parameters.
        Create the basic query_help
        """
        super(ComputerTranslator, self).__init__(Class=self.__class__, **kwargs)

    def get_projectable_properties(self):
        """
        Get projectable properties specific for Computer
        :return: dict of projectable properties and column_order list
        """
        projectable_properties = {
            'description': {
                'display_name': 'Description',
                'help_text': 'short description of the Computer',
                'is_foreign_key': False,
                'type': 'str',
                'is_display': False
            },
            'hostname': {
                'display_name': 'Host',
                'help_text': 'Name of the host',
                'is_foreign_key': False,
                'type': 'str',
                'is_display': True
            },
            'id': {
                'display_name': 'Id',
                'help_text': 'Id of the object',
                'is_foreign_key': False,
                'type': 'int',
                'is_display': False
            },
            'name': {
                'display_name': 'Name',
                'help_text': 'Name of the object',
                'is_foreign_key': False,
                'type': 'str',
                'is_display': True
            },
            'scheduler_type': {
                'display_name': 'Scheduler',
                'help_text': 'Scheduler type',
                'is_foreign_key': False,
                'type': 'str',
                'valid_choices': {
                    'direct': {
                        'doc': 'Support for the direct execution bypassing schedulers.'
                    },
                    'pbsbaseclasses.PbsBaseClass': {
                        'doc': 'Base class with support for the PBSPro scheduler'
                    },
                    'pbspro': {
                        'doc': 'Subclass to support the PBSPro scheduler'
                    },
                    'sge': {
                        'doc':
                        'Support for the Sun Grid Engine scheduler and its variants/forks (Son of Grid Engine, '
                        'Oracle Grid Engine, ...)'
                    },
                    'slurm': {
                        'doc': 'Support for the SLURM scheduler (http://slurm.schedmd.com/).'
                    },
                    'torque': {
                        'doc': 'Subclass to support the Torque scheduler.'
                    }
                },
                'is_display': True
            },
            'transport_type': {
                'display_name': 'Transport type',
                'help_text': 'Transport Type',
                'is_foreign_key': False,
                'type': 'str',
                'valid_choices': {
                    'local': {
                        'doc':
                        'Support copy and command execution on the same host on which AiiDA is running via direct '
                        'file copy and execution commands.'
                    },
                    'ssh': {
                        'doc':
                        'Support connection, command execution and data transfer to remote computers via SSH+SFTP.'
                    }
                },
                'is_display': False
            },
            'uuid': {
                'display_name': 'Unique ID',
                'help_text': 'Universally Unique Identifier',
                'is_foreign_key': False,
                'type': 'unicode',
                'is_display': True
            }
        }

        # Note: final schema will contain details for only the fields present in column order
        column_order = ['uuid', 'name', 'hostname', 'description', 'scheduler_type', 'transport_type']

        return projectable_properties, column_order
