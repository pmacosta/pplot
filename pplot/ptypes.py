# ptypes.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0916

# PyPI imports
import pexdoc.pcontracts


###
# Functions
###
@pexdoc.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_bad_choice=(
        ValueError,
        (
            "Argument `*[argument_name]*` is not one of 'binary', 'Blues', "
            "'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', "
            "'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', "
            "'YlGnBu', 'YlOrBr' or 'YlOrRd' (case insensitive)"
        )
    )
)
def color_space_option(obj):
    r"""
    Validates if an object is a ColorSpaceOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the name of the argument the contract
       is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not one of 'binary',
       'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
       'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
       'YlOrBr' or 'YlOrRd). The token \*[argument_name]\* is replaced by the
       name of the argument the contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if (obj is not None) and (not isinstance(obj, str)):
        raise ValueError(exdesc['argument_invalid'])
    if (obj is None) or (obj and any([
            item.lower() == obj.lower()
            for item in [
                    'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens',
                    'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd',
                    'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu',
                    'YlOrBr', 'YlOrRd'
            ]
    ])):
        return None
    raise ValueError(exdesc['argument_bad_choice'])


@pexdoc.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_bad_choice=(
        ValueError,
        (
            "Argument `*[argument_name]*` is not one of ['STRAIGHT', 'STEP', "
            "'CUBIC', 'LINREG'] (case insensitive)"
        )
    )
)
def interpolation_option(obj):
    r"""
    Validates if an object is an InterpolationOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the name of the argument the contract
       is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not one of ['STRAIGHT',
       'STEP', 'CUBIC', 'LINREG'] (case insensitive)). The token
       \*[argument_name]\* is replaced by the name of the argument
       the contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if (obj is not None) and (not isinstance(obj, str)):
        raise ValueError(exdesc['argument_invalid'])
    if ((obj is None) or
       (obj and any([
           item.lower() == obj.lower()
           for item in ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']]))):
        return None
    raise ValueError(exdesc['argument_bad_choice'])


@pexdoc.pcontracts.new_contract(
    argument_invalid='Argument `*[argument_name]*` is not valid',
    argument_bad_choice=(
        ValueError,
        "Argument `*[argument_name]*` is not one of ['-', '--', '-.', ':']"
    )
)
def line_style_option(obj):
    r"""
    Validates if an object is a LineStyleOption pseudo-type object

    :param obj: Object
    :type  obj: any

    :raises:
     * RuntimeError (Argument \`*[argument_name]*\` is not valid). The token
       \*[argument_name]\* is replaced by the name of the argument the contract
       is attached to

     * RuntimeError (Argument \`*[argument_name]*\` is not one of ['-', '--',
       '-.', ':']). The token \*[argument_name]\* is replaced by the name of
       the argument the contract is attached to

    :rtype: None
    """
    exdesc = pexdoc.pcontracts.get_exdesc()
    if (obj is not None) and (not isinstance(obj, str)):
        raise ValueError(exdesc['argument_invalid'])
    if obj in [None, '-', '--', '-.', ':']:
        return None
    raise ValueError(exdesc['argument_bad_choice'])
