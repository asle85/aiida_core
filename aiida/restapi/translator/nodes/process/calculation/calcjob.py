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
Translator for calculation node
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
import os

from aiida.restapi.translator.nodes.process.process import ProcessTranslator
from aiida.restapi.common.exceptions import RestInputValidationError
from aiida.orm.utils.repository import FileType


class CalcJobTranslator(ProcessTranslator):
    """
    Translator relative to resource 'calculations' and aiida class Calculation
    """

    # A label associated to the present class (coincides with the resource name)
    __label__ = 'calcjobs'
    # The AiiDA class one-to-one associated to the present class
    from aiida.orm import CalcJobNode
    _aiida_class = CalcJobNode
    # The string name of the AiiDA class
    _aiida_type = 'process.calculation.calcjob.CalcJobNode.'

    _result_type = __label__

    def __init__(self, **kwargs):
        """
        Initialise the parameters.
        Create the basic query_help
        """
        # basic query_help object
        super(CalcJobTranslator, self).__init__(Class=self.__class__, **kwargs)


    @staticmethod
    def get_files_list(node_obj, dir_obj=None, files=None, prefix=None):
        """
        Return the list of all files contained in the node object repository
        If a directory object `dir_obj` of the repository is passed, get the list of all files
        recursively in the specified directory

        :param node_obj: node object
        :param dir_obj: directory in which files will be searched
        :param files: list of files if any
        :param prefix: file name prefix if any
        :return: the list of files
        """
        if files is None:
            files = []
        if prefix is None:
            prefix = []

        if dir_obj:
            flist = node_obj.list_objects(dir_obj)
        else:
            flist = node_obj.list_objects()

        for fname, ftype in flist:
            if ftype == FileType.FILE:
                filename = os.path.join(*(prefix + [fname]))
                files.append(filename)
            elif ftype == FileType.DIRECTORY:
                CalcJobTranslator.get_files_list(node_obj, fname, files, prefix + [fname])
        return files

    @staticmethod
    def get_input_files(node):
        """
        Get the submitted input files for job calculation
        :param node: aiida node
        :return: the retrieved input files for job calculation
        """

        try:
            retrieved = CalcJobTranslator.get_files_list(node)
        except:
            retrieved = 'Error in getting input files for CalcJob.'

        return retrieved



    @staticmethod
    def get_output_files(node):
        """
        Get the retrieved output files for job calculation
        :param node: aiida node
        :return: the retrieved output files for job calculation
        """

        retrieved_folder_node = node.outputs.retrieved
        response = {}

        if retrieved_folder_node is None:
            response['status'] = 200
            response['data'] = 'This node does not have retrieved folder'
            return response

        retrieved = CalcJobTranslator.get_files_list(retrieved_folder_node)
        return retrieved

