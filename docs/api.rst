.. api.rst
.. Copyright (c) 2013-2017 Pablo Acosta-Serafini
.. See LICENSE for details

###
API
###

****************
Global variables
****************

.. autodata:: pplot.constants.AXIS_LABEL_FONT_SIZE
.. autodata:: pplot.constants.LINE_WIDTH
.. autodata:: pplot.constants.LEGEND_SCALE
.. autodata:: pplot.constants.MARKER_SIZE
.. autodata:: pplot.constants.MIN_TICKS
.. autodata:: pplot.constants.PRECISION
.. autodata:: pplot.constants.SUGGESTED_MAX_TICKS
.. autodata:: pplot.constants.TITLE_FONT_SIZE

*********
Functions
*********

.. autofunction:: pplot.parameterized_color_space

*******
Classes
*******

 .. autoclass:: pplot.functions.DataSource
	:members: __str__, _set_indep_var, _set_dep_var
	:show-inheritance:
 .. autoclass:: pplot.BasicSource
	:members: __str__, dep_var, indep_max, indep_min, indep_var
	:show-inheritance:
 .. autoclass:: pplot.CsvSource
	:members: __str__, dep_col_label, dep_var, fname, fproc, fproc_eargs,
	          indep_col_label, indep_max, indep_min, indep_var, rfilter
	:show-inheritance:
 .. autoclass:: pplot.Series
	:members: __str__, color, data_source, interp, label, line_style,
                  marker, secondary_axis
	:show-inheritance:
 .. autoclass:: pplot.Panel
	:members: display_indep_axis, legend_props, log_dep_axis,
	          primary_axis_label, primary_axis_scale, primary_axis_ticks,
                  primary_axis_units, secondary_axis_label,
                  secondary_axis_scale, secondary_axis_ticks,
                  secondary_axis_units, series, __bool__, __iter__,
                  __nonzero__, __str__
	:show-inheritance:
 .. autoclass:: pplot.Figure
	:members: axes_list, fig, fig_height, fig_width,
	          indep_axis_scale, indep_axis_ticks, indep_var_label,
                  indep_var_units, log_indep_axis, panels, save, show, title,
                  __bool__, __iter__, __nonzero__, __str__
	:show-inheritance:

**********************
Contracts pseudo-types
**********************

Introduction
============

The pseudo-types defined below can be used in contracts of the
`PyContracts <https://andreacensi.github.io/contracts>`_ or
`Pexdoc <http://pexdoc.readthedocs.org>`_ libraries. As an example, with the
latter:

    .. code-block:: python

        >>> from __future__ import print_function
        >>> import pexdoc
        >>> from pplot.ptypes import interpolation_option
        >>> @pexdoc.pcontracts.contract(ioption='interpolation_option')
        ... def myfunc(ioption):
        ...     print('Option received: '+str(ioption))
        ...
        >>> myfunc('STEP')
        Option received: STEP
        >>> myfunc(35)
        Traceback (most recent call last):
            ...
        RuntimeError: Argument `ioption` is not valid

Alternatively each pseudo-type has a :ref:`checker function <ContractCheckers>`
associated with it that can be used to verify membership. For example:

    .. code-block:: python

        >>> import pplot.ptypes
        >>> # None is returned if object belongs to pseudo-type
        >>> pplot.ptypes.interpolation_option('STEP')
        >>> # ValueError is raised if object does not belong to pseudo-type
        >>> pplot.ptypes.interpolation_option(3.5) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: [START CONTRACT MSG: interpolation_option]...

Description
===========

.. _ColorSpaceOption:

ColorSpaceOption
^^^^^^^^^^^^^^^^

Import as :code:`color_space_option`. String representing a `Matplotlib
<http://matplotlib.org/>`_ color space, one :code:`'binary'`, :code:`'Blues'`,
:code:`'BuGn'`, :code:`'BuPu'`, :code:`'GnBu'`, :code:`'Greens'`,
:code:`'Greys'`, :code:`'Oranges'`, :code:`'OrRd'`, :code:`'PuBu'`,
:code:`'PuBuGn'`, :code:`'PuRd'`, :code:`'Purples'`, :code:`'RdPu'`,
:code:`'Reds'`, :code:`'YlGn'`, :code:`'YlGnBu'`, :code:`'YlOrBr`',
:code:`'YlOrRd'` or :code:`None`

.. _InterpolationOption:

InterpolationOption
^^^^^^^^^^^^^^^^^^^

Import as :code:`interpolation_option`. String representing an interpolation
type, one of :code:`'STRAIGHT'`, :code:`'STEP'`, :code:`'CUBIC'`,
:code:`'LINREG'` (case insensitive) or :code:`None`

.. _LineStyleOption:

LineStyleOption
^^^^^^^^^^^^^^^

Import as :code:`line_style_option`. String representing a `Matplotlib`_ line
style, one of :code:`'-'`, :code:`'--'`, :code:`'-.'`, :code:`':'` or
:code:`None`

.. _ContractCheckers:

Checker functions
=================

.. autofunction:: pplot.ptypes.color_space_option
.. autofunction:: pplot.ptypes.interpolation_option
.. autofunction:: pplot.ptypes.line_style_option
