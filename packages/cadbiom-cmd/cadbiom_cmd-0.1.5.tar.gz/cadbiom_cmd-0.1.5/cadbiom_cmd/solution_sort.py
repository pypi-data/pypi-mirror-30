# -*- coding: utf-8 -*-
# Copyright (C) 2017  IRISA
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# The original code contained here was initially developed by:
#
#     Pierre Vignet.
#     IRISA
#     Dyliss team
#     IRISA Campus de Beaulieu
#     35042 RENNES Cedex, FRANCE
"""This module provides some functions to do some analyzes on the output
files of Cadbiom.
"""
from __future__ import unicode_literals
from __future__ import print_function

import os
import glob
from collections import Counter
from collections import defaultdict
import csv


## Handle output files #########################################################

def get_solutions(file_descriptor):
    """Generator of solution lines and corresponding stripped lines.

    .. note: Do not return events ! Just sets of frontier places.

    :param: Opened file.
    :type: <file>
    :return: Line (without '\n') and stripped line (with '\' replaced by ' '
        (except for final '\t')).
    :rtype: <tuple <str>, <str>>
    """

    for line in file_descriptor:
        # Remove possible \t separator from first line (frontier solution)
        line = line.rstrip('\n')
        stripped_line = line.rstrip('\t').replace('\t', ' ')

        # Next Line if empty
        if stripped_line == '':
            continue

        # Remove events or other lines
        if stripped_line[0] not in ('%', '=', ' '):
            # print(stripped_line)
            # Sort in lower case, remove ' ' empty elements
            yield line, stripped_line

## Sort functions ##############################################################

def sort_solutions_in_file(filepath):
    """Sort all solutions in the given file in alphabetical order.

    .. warning:: The file is modified in place.

    :param: Filepath to be opened and in which solutions will be sorted.
    :arg: <str>
    """

    solutions = dict()

    with open(filepath, 'r+') as fd:

        # Get old line as key and ordered line as value
        for line, stripped_line in get_solutions(fd):
            # Sort in lower case, remove ' ' empty elements
            solutions[line] = \
                " ".join(sorted([place for place in stripped_line.split(' ')
                                 if place != ' '], key=lambda s: s.lower()))

        # Rewind the whole file
        fd.seek(0)

        # Load all the content
        file_text = fd.read()

        # Replace old sols with the new ones
        for original_sol, sorted_sol in solutions.items():
            file_text = file_text.replace(original_sol, sorted_sol)

        # Rewind the whole file
        fd.seek(0)

        # Write all text in the current opened file
        fd.write(file_text)


def sort_solutions(path):
    """Entry point for sorting solutions.

    Parse a solution file and sort all frontier places in alphabetical order.

    :param: Filepath or directory path containing Cadbiom solutions.
    :type: <str>
    """

    # Check valid input file/directory
    assert os.path.isfile(path) or os.path.isdir(path)

    if os.path.isdir(path):
        # Recursive search of *cam* files
        # (cam.txt, cam_complete.txt, cam_step.txt)
        path = path if path[-1] == '/' else path + '/'
        [sort_solutions_in_file(file) for file in glob.glob(path + '*cam*')]
    else:
        sort_solutions_in_file(path)

################################################################################
