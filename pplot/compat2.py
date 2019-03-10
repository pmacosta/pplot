# compat2.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R1717,W0122,W0613


###
# Functions
###
def _readlines(fname):  # pragma: no cover
    """Read all lines from file."""
    with open(fname, "r") as fobj:
        return fobj.readlines()


# Largely from From https://stackoverflow.com/questions/956867/
# how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
# with Python 2.6 compatibility changes
def _unicode_to_ascii(obj):  # pragma: no cover
    """Convert to ASCII."""
    # pylint: disable=E0602
    if isinstance(obj, dict):
        return dict(
            [
                (_unicode_to_ascii(key), _unicode_to_ascii(value))
                for key, value in obj.items()
            ]
        )
    if isinstance(obj, list):
        return [_unicode_to_ascii(element) for element in obj]
    if isinstance(obj, unicode):
        return obj.encode("utf-8")
    return obj


def _write(fobj, data):
    """Write data to file."""
    fobj.write(data)
