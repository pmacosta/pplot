# test_ptypes.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,W0108

# PyPI imports
from pmisc import AE

# Intra-package imports
import pplot.ptypes


###
# Global variables
###
emsg = lambda msg: (
    "[START CONTRACT MSG: {0}]Argument `*[argument_name]*` "
    "is not valid[STOP CONTRACT MSG]".format(msg)
)


###
# Helper functions
###
def check_contract(obj, name, value):
    AE(obj, ValueError, emsg(name), obj=value)


###
# Test functions
###
def test_color_space_option_contract():
    """Test for LineStyleOption pseudo-type."""
    obj = pplot.ptypes.color_space_option
    check_contract(obj, "color_space_option", 5)
    exmsg = (
        "[START CONTRACT MSG: color_space_option]Argument "
        "`*[argument_name]*` is not one of 'binary', 'Blues', 'BuGn', "
        "'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', "
        "'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', "
        "'YlOrBr' or 'YlOrRd' (case insensitive)[STOP CONTRACT MSG]"
    )
    AE(obj, ValueError, exmsg, obj="x")
    for item in [
        "binary",
        "Blues",
        "BuGn",
        "BuPu",
        "GnBu",
        "Greens",
        "Greys",
        "Oranges",
        "OrRd",
        "PuBu",
        "PuBuGn",
        "PuRd",
        "Purples",
        "RdPu",
        "Reds",
        "YlGn",
        "YlGnBu",
        "YlOrBr",
        "YlOrRd",
    ]:
        pplot.ptypes.color_space_option(item)


def test_interpolation_option_contract():
    """Test for InterpolationOption pseudo-type."""
    obj = pplot.ptypes.interpolation_option
    check_contract(obj, "interpolation_option", 5)
    exmsg = (
        "[START CONTRACT MSG: interpolation_option]Argument "
        "`*[argument_name]*` is not one of ['STRAIGHT', 'STEP', 'CUBIC', "
        "'LINREG'] (case insensitive)[STOP CONTRACT MSG]"
    )
    AE(obj, ValueError, exmsg, obj="x")
    obj(None)
    for item in ["STRAIGHT", "STEP", "CUBIC", "LINREG"]:
        obj(item)
        obj(item.lower())


def test_line_style_option_contract():
    """Test for LineStyleOption pseudo-type."""
    check_contract(pplot.ptypes.line_style_option, "line_style_option", 5)
    exmsg = (
        "[START CONTRACT MSG: line_style_option]Argument "
        "`*[argument_name]*` is not one of ['-', '--', '-.', "
        "':'][STOP CONTRACT MSG]"
    )
    AE(pplot.ptypes.line_style_option, ValueError, exmsg, obj="x")
    pplot.ptypes.line_style_option(None)
    for item in ["-", "--", "-.", ":"]:
        pplot.ptypes.line_style_option(item)
