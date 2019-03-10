# compat3.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0122,W0613


###
# Functions
###
def _readlines(fname, fpointer1=open, fpointer2=open):
    """Read all lines from file."""
    # fpointer1, fpointer2 arguments to ease testing
    try:  # pragma: no cover
        with fpointer1(fname, "r") as fobj:
            return fobj.readlines()
    except UnicodeDecodeError:  # pragma: no cover
        with fpointer2(fname, "r", encoding="utf-8") as fobj:
            return fobj.readlines()


def _unicode_to_ascii(obj):  # pragma: no cover
    # pylint: disable=E0602
    return obj


def _write(fobj, data):
    """Write data to file."""
    fobj.write(data)
