#!/usr/bin/env python
# patch_pylint.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import os
import sys


###
# Functions
###
def main(pkg_dir):
    """ Processing """
    fname = os.path.join(pkg_dir, 'astroid', 'brain', 'pysix_moves.py')
    ret = []
    with open(fname, 'r') as fobj:
        lines = fobj.readlines()
    in_func = False
    for line in [item.rstrip() for item in lines]:
        if (not in_func) and line.startswith('def six_moves_transform'):
            in_func = True
        if in_func and line.strip() == '{}':
            ret.append('    {0}')
            in_func = False
        else:
            ret.append(line)
    with open(fname, 'w') as fobj:
        fobj.write(os.linesep.join(ret))


if __name__ == '__main__':
    main(sys.argv[1])
