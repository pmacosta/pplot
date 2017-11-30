# panel.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,C1801,R0912,R0913,R0914,R0915,W0105,W0212

# Standard library imports
import sys
# PyPI imports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import pmisc
import pexdoc.exh
import pexdoc.pcontracts
# Intra-package imports
from .series import Series
from .functions import _F, _intelligent_ticks, _uniquify_tick_labels
from .constants import (
    AXIS_LABEL_FONT_SIZE, AXIS_TICKS_FONT_SIZE, LEGEND_SCALE, TITLE_FONT_SIZE
)


###
# Exception tracing initialization code
###
"""
[[[cog
import os, sys
if sys.hexversion < 0x03000000:
    import __builtin__
else:
    import builtins as __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_plot_panel
exobj_plot = trace_ex_plot_panel.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Constants
###
INF = sys.float_info.max
SPACER = 0.2 # in inches


###
# Functions
###
def _legend_position_validation(obj):
    """ Validate if a string is a valid legend position """
    options = [
        'BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT',
        'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER',
        'UPPER CENTER', 'CENTER'
    ]
    if (obj is not None) and (not isinstance(obj, str)):
        return True
    if ((obj is None) or
       (obj and any([item.lower() == obj.lower() for item in options]))):
        return False
    return True


def _lmax(*args):
    return _lmm(max, 0, *args)


def _lmin(*args):
    return _lmm(min, INF, *args)


def _lmm(fpointer, limit, *args):
    ret = [
        item
        for item in pmisc.flatten_list(args)
        if (item is not None) and (-INF <= item <= INF)
    ]
    return fpointer(ret) if ret else limit


###
# Classes
###
class _Axis(object):
    # pylint: disable=R0902,R0903
    def __init__(self, axis, atype, ticklabels=None):
        self.axis = axis
        self.prim = atype.lower() == 'prim'
        self.sec = atype.lower() == 'sec'
        self.fig = axis.figure
        self.renderer = self.fig.canvas.get_renderer()
        self._spine_bbox = None
        self._min_spine_bbox = None
        self.dummy_bbox = None
        self._xlabel = None
        self._xlabel_bbox = None
        self._xticklabels = None
        self._xticklabels_bbox = None
        self._ylabel = None
        self._ylabel_bbox = None
        self._yticklabels = None
        self._yticklabels_bbox = None
        self._title = None
        self._title_bbox = None
        self._left = None
        self._bottom = None
        self._right = None
        self._top = None
        self._axis_bbox = None
        self._xlabel_plus_pad = None
        self._title_plus_pad = None
        self._left_overhang = None
        self._right_overhang = None
        self._ylabel_plus_pad = None
        self._bottom_overhang = None
        self._top_overhang = None
        self.ticklabels = ticklabels
        self.axis_bbox = self.axis.get_tightbbox(
            renderer=self.renderer
        ).transformed(self.fig.dpi_scale_trans.inverted())
        self._get_spine_bbox()
        self._get_xlabel()
        self._get_xlabel_bbox()
        self._get_xticklabels()
        self._get_xticklabels_bbox()
        self._get_ylabel()
        self._get_ylabel_bbox()
        self._get_yticklabels()
        self._get_yticklabels_bbox()
        self._get_title()
        self._get_title_bbox()
        self._get_left()
        self._get_bottom()
        self._get_right()
        self._get_top()
        self._get_axis_bbox()
        self._get_min_spine_bbox()
        self._get_title_plus_pad()
        self._get_xlabel_plus_pad()
        self._get_ylabel_plus_pad()
        self._get_left_overhang()
        self._get_right_overhang()
        self._get_top_overhang()
        self._get_bottom_overhang()

    def _axis_edge(self, axis, prop):
        bbox = axis.get_tightbbox(renderer=self.renderer)
        if bbox:
            obj = bbox.transformed(self.fig.dpi_scale_trans.inverted())
            return getattr(obj, prop)
        return None

    def _bbox(self, obj):
        """ Returns bounding box of an object """
        return obj.get_window_extent(renderer=self.renderer).transformed(
            self.fig.dpi_scale_trans.inverted()
        )

    def _get_axis_bbox(self):
        if self._axis_bbox is None:
            self.axis_bbox = Bbox(
                [[self.left, self.bottom], [self.right, self.top]]
            )
        return self._axis_bbox

    def _get_bottom(self):
        return _lmin([self.xaxis_bottom, self.yaxis_bottom])

    def _get_bottom_overhang(self):
        if self._bottom_overhang is None:
            self._bottom_overhang = self._get_yoverhang('ymin')
        return self._bottom_overhang

    def _get_left(self):
        return _lmin([self.xaxis_left, self.yaxis_left])

    def _get_left_overhang(self):
        if self._left_overhang is None:
            self._left_overhang = self._get_xoverhang('xmin')
        return self._left_overhang

    def _get_right(self):
        return _lmax([self.xaxis_right, self.yaxis_right])

    def _get_right_overhang(self):
        if self._right_overhang is None:
            self._right_overhang = self._get_xoverhang('xmax')
        return self._right_overhang

    def _get_spine_bbox(self):
        if self._spine_bbox is None:
            left = self._bbox(self.axis.spines['left']).xmin
            bottom = self._bbox(self.axis.spines['bottom']).ymin
            right = self._bbox(self.axis.spines['right']).xmax
            top = self._bbox(self.axis.spines['top']).ymax
            self._spine_bbox = Bbox([[left, bottom], [right, top]])
            # Create dummy bbox in the midle of the spine so as to not limit
            # measurements in any dimension
            xcenter = (left+right)/2.0
            ycenter = (top+bottom)/2.0
            self.dummy_bbox = Bbox([[xcenter, ycenter], [xcenter, ycenter]])
        return self._spine_bbox

    def _get_title(self):
        if self._title is None:
            self._title = self.axis.get_title().strip()
        return self._title or None

    def _get_title_bbox(self):
        if (self._title_bbox is None) and (self._title is None):
            self._title_bbox = self.dummy_bbox
        elif self._title_bbox is None:
            self._title_bbox = self._bbox(self.axis.title)
        return self._title_bbox

    def _get_title_plus_pad(self):
        if self._title_plus_pad is None:
            edge = max(self.yticklabels_bbox.ymax, self.ylabel_bbox.ymax)
            self._title_plus_pad = self.title_bbox.ymax-edge
        return self._title_plus_pad

    def _get_top(self):
        return _lmax([self.xaxis_top, self.yaxis_top])

    def _get_top_overhang(self):
        if self._top_overhang is None:
            self._top_overhang = self._get_yoverhang('ymax')
        return self._top_overhang

    def _get_xaxis_bottom(self):
        return self._axis_edge(self.axis.xaxis, 'ymin')

    def _get_xaxis_left(self):
        return self._axis_edge(self.axis.xaxis, 'xmin')

    def _get_xaxis_right(self):
        return self._axis_edge(self.axis.xaxis, 'xmax')

    def _get_xaxis_top(self):
        return self._axis_edge(self.axis.xaxis, 'ymax')

    def _get_xlabel(self):
        if self._xlabel is None:
            self._xlabel = self.axis.xaxis.get_label().get_text().strip()
        return self._xlabel or None

    def _get_xlabel_bbox(self):
        if (self._xlabel_bbox is None) and (self._xlabel is None):
            self._xlabel_bbox = self.dummy_bbox
        elif self._xlabel_bbox is None:
            self._xlabel_bbox = self._bbox(self.axis.xaxis.get_label())
        return self._xlabel_bbox

    def _get_xlabel_plus_pad(self):
        if self._xlabel_plus_pad is None:
            dim = lambda x: getattr(x, 'ymin')
            spine_edge = dim(self.spine_bbox)
            edge = min(dim(self.xticklabels_bbox), spine_edge)
            self._xlabel_plus_pad = max(0, edge-dim(self._xlabel_bbox))
        return self._xlabel_plus_pad

    def _get_xoverhang(self, prop):
        sign = -1 if prop == 'xmin' else +1
        dim = lambda x: getattr(x, prop)
        mid = dim(self.spine_bbox)
        label = dim(self.xlabel_bbox) if self.xlabel_bbox else mid
        label_overhang = max(0, sign*(label-mid))
        ytick = dim(self.yticklabels_bbox) if self.yticklabels_bbox else mid
        ytick_overhang = max(0, sign*(ytick-mid))
        xtick = dim(self.xticklabels_bbox) if self.xticklabels_bbox else mid
        xtick_overhang = max(0, sign*(xtick-mid))
        title = dim(self.title_bbox) if self.title_bbox else mid
        title_overhang = max(0, sign*(title-mid))
        return max(
            [label_overhang, ytick_overhang, xtick_overhang, title_overhang]
        )

    def _get_xticklabels(self):
        if self._xticklabels is None:
            self._xticklabels = [
                label.get_text().strip()
                for label in self.axis.xaxis.get_ticklabels()
                if label.get_text().strip()
            ]
        return self._xticklabels or None

    def _get_xticklabels_bbox(self):
        if self._xticklabels_bbox is None:
            ticks = self.axis.xaxis.get_ticklabels()
            tick_bboxes = [
                self._bbox(tick_bbox)
                for tick_bbox in ticks if tick_bbox.get_text().strip()
            ]
            if not tick_bboxes:
                self._xticklabels_bbox = self.dummy_bbox
            else:
                left = _lmin([tick_bbox.xmin for tick_bbox in tick_bboxes])
                right = _lmax([tick_bbox.xmax for tick_bbox in tick_bboxes])
                bottom = _lmin([tick_bbox.ymin for tick_bbox in tick_bboxes])
                top = _lmax([tick_bbox.ymax for tick_bbox in tick_bboxes])
                self._xticklabels_bbox = Bbox([[left, bottom], [right, top]])
        return self._xticklabels_bbox

    def _get_yticklabels(self):
        if self._yticklabels is None:
            self._yticklabels = [
                label.get_text().strip()
                for label in self.axis.yaxis.get_ticklabels()
                if label.get_text().strip()
            ]
        return self._yticklabels or None

    def _get_yaxis_bottom(self):
        return self._axis_edge(self.axis.yaxis, 'ymin')

    def _get_yaxis_left(self):
        return self._axis_edge(self.axis.yaxis, 'xmin')

    def _get_yaxis_right(self):
        return self._axis_edge(self.axis.yaxis, 'xmax')

    def _get_yaxis_top(self):
        return self._axis_edge(self.axis.yaxis, 'ymax')

    def _get_ylabel(self):
        if self._ylabel is None:
            self._ylabel = self.axis.yaxis.get_label().get_text().strip()
        return self._ylabel or None

    def _get_ylabel_bbox(self):
        if (self._ylabel_bbox is None) and (self._ylabel is None):
            self._ylabel_bbox = self.dummy_bbox
        elif self._ylabel_bbox is None:
            self._ylabel_bbox = self._bbox(self.axis.yaxis.get_label())
        return self._ylabel_bbox

    def _get_ylabel_plus_pad(self):
        if self._ylabel_plus_pad is None:
            sign = -1 if self.prim else +1
            func = min if self.prim else max
            prop = 'xmin' if self.prim else 'xmax'
            dim = lambda x: getattr(x, prop)
            spine_edge = dim(self.spine_bbox)
            edge = func(dim(self.yticklabels_bbox), spine_edge)
            self._ylabel_plus_pad = max(
                0, sign*(dim(self.ylabel_bbox)-edge)
            )
        return self._ylabel_plus_pad

    def _get_yoverhang(self, prop):
        sign = -1 if prop == 'ymin' else +1
        dim = lambda x: getattr(x, prop)
        mid = dim(self.spine_bbox)
        label = dim(self.ylabel_bbox)
        label_overhang = max(0, sign*(label-mid))
        xtick = dim(self.xticklabels_bbox) if self.xticklabels_bbox else mid
        xtick_overhang = max(0, sign*(xtick-mid))
        ytick = dim(self.yticklabels_bbox) if self.yticklabels_bbox else mid
        ytick_overhang = max(0, sign*(ytick-mid))
        return max(label_overhang, xtick_overhang, ytick_overhang)

    def _get_yticklabels_bbox(self):
        if self._yticklabels_bbox is None:
            ticks = self.axis.yaxis.get_ticklabels()
            tick_bboxes = [
                self._bbox(tick_bbox)
                for tick_bbox in ticks if tick_bbox.get_text().strip()
            ]
            left = _lmin([tick_bbox.xmin for tick_bbox in tick_bboxes])
            right = _lmax([tick_bbox.xmax for tick_bbox in tick_bboxes])
            bottom = _lmin([tick_bbox.ymin for tick_bbox in tick_bboxes])
            top = _lmax([tick_bbox.ymax for tick_bbox in tick_bboxes])
            self._yticklabels_bbox = Bbox([[left, bottom], [right, top]])
        return self._yticklabels_bbox

    def _get_min_spine_bbox(self):
        def core(xaxis):
            # pylint: disable=C0325
            sep = (1.5 if xaxis else 0.5)*SPACER
            dim = 'width' if xaxis else 'height'
            axis = self.axis.xaxis if xaxis else self.axis.yaxis
            locs = axis.get_ticklocs()
            if (not xaxis) or (xaxis and not self.ticklabels):
                tick_labels = axis.get_ticklabels()
                tick_labels = [
                    label for label in tick_labels if label.get_text().strip()
                ]
            else:
                tick_labels = self.ticklabels
            bboxes = [self._bbox(label) for label in tick_labels]
            bboxes = [
                bbox for bbox in bboxes if -INF <= getattr(bbox, dim) <= INF
            ]
            mult = 3 if axis.log_axis else 1
            label_half_dim = [
                (getattr(bbox, dim)+mult*sep)/2.0 for bbox in bboxes
            ]
            min_label_half_dim = (
                max(label_half_dim)*(len(label_half_dim)-1)
                if label_half_dim else
                0
            )
            if axis.log_axis or (not label_half_dim):
                return min_label_half_dim
            tick_diffs = np.diff(np.array(locs))
            curr_label, prev_label = label_half_dim[1:], label_half_dim[:-1]
            sep_dim = [curr+prev for curr, prev in zip(curr_label, prev_label)]
            dpu = max(sep_dim/tick_diffs)
            axis_box_dim = (locs[-1]-locs[0])*dpu
            return axis_box_dim
        if self._min_spine_bbox is None:
            width = core(xaxis=True)
            height = core(xaxis=False)
            self._min_spine_bbox = Bbox([[0, 0], [width, height]])
        return self._min_spine_bbox

    # Managed attributes
    bottom = property(_get_bottom)
    left = property(_get_left)
    min_spine_bbox = property(_get_min_spine_bbox)
    right = property(_get_right)
    spine_bbox = property(_get_spine_bbox)
    title = property(_get_title)
    title_bbox = property(_get_title_bbox)
    top = property(_get_top)
    xaxis_bottom = property(_get_xaxis_bottom)
    xaxis_left = property(_get_xaxis_left)
    xaxis_right = property(_get_xaxis_right)
    xaxis_top = property(_get_xaxis_top)
    xlabel = property(_get_xlabel)
    xlabel_bbox = property(_get_xlabel_bbox)
    xlabel_plus_pad = property(_get_xlabel_plus_pad)
    title_plus_pad = property(_get_title_plus_pad)
    xoverhang = property(_get_xoverhang)
    xticklabels = property(_get_xticklabels)
    xticklabels_bbox = property(_get_xticklabels_bbox)
    yaxis_bottom = property(_get_yaxis_bottom)
    yaxis_left = property(_get_yaxis_left)
    yaxis_right = property(_get_yaxis_right)
    yaxis_top = property(_get_yaxis_top)
    ylabel = property(_get_ylabel)
    ylabel_bbox = property(_get_ylabel_bbox)
    ylabel_plus_pad = property(_get_ylabel_plus_pad)
    left_overhang = property(_get_left_overhang)
    bottom_overhang = property(_get_bottom_overhang)
    right_overhang = property(_get_right_overhang)
    top_overhang = property(_get_top_overhang)
    yticklabels = property(_get_yticklabels)
    yticklabels_bbox = property(_get_yticklabels_bbox)


class Panel(object):
    r"""
    Defines a panel within a figure

    :param series: One or more data series
    :type  series: :py:class:`pplot.Series` *or list of*
                   :py:class:`pplot.Series` *or None*

    :param primary_axis_label: Primary dependent axis label
    :type  primary_axis_label: string

    :param primary_axis_units: Primary dependent axis units
    :type  primary_axis_units: string

    :param primary_axis_ticks: Primary dependent axis tick marks. If not None
                               overrides automatically generated tick
                               marks if the axis type is linear. If None
                               automatically generated tick marks are used for
                               the primary axis
    :type  primary_axis_ticks: list, Numpy vector or None

    :param secondary_axis_label: Secondary dependent axis label
    :type  secondary_axis_label: string

    :param secondary_axis_units: Secondary dependent axis units
    :type  secondary_axis_units: string

    :param secondary_axis_ticks: Secondary dependent axis tick marks. If not
                                 None overrides automatically generated tick
                                 marks if the axis type is linear. If None
                                 automatically generated tick marks are used
                                 for the secondary axis
    :type  secondary_axis_ticks: list, Numpy vector or None

    :param log_dep_axis: Flag that indicates whether the dependent (primary and
                         /or secondary) axis is linear (False) or logarithmic
                         (True)
    :type  log_dep_axis: boolean

    :param legend_props: Legend properties. See
                         :py:attr:`pplot.Panel.legend_props`. If None the
                         legend is placed in the best position in one column
    :type  legend_props: dictionary or None

    :param display_indep_axis: Flag that indicates whether the independent axis
                               is displayed (True) or not (False)
    :type  display_indep_axis: boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.__init__

    :raises:
     * RuntimeError (Argument \`display_indep_axis\` is not valid)

     * RuntimeError (Argument \`legend_props\` is not valid)

     * RuntimeError (Argument \`log_dep_axis\` is not valid)

     * RuntimeError (Argument \`primary_axis_label\` is not valid)

     * RuntimeError (Argument \`primary_axis_ticks\` is not valid)

     * RuntimeError (Argument \`primary_axis_units\` is not valid)

     * RuntimeError (Argument \`secondary_axis_label\` is not valid)

     * RuntimeError (Argument \`secondary_axis_ticks\` is not valid)

     * RuntimeError (Argument \`secondary_axis_units\` is not valid)

     * RuntimeError (Argument \`series\` is not valid)

     * RuntimeError (Legend property \`cols\` is not valid)

     * RuntimeError (Series item *[number]* is not fully specified)

     * TypeError (Legend property \`pos\` is not one of ['BEST', 'UPPER
       RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER
       LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER']
       (case insensitive))

     * ValueError (Illegal legend property \`*[prop_name]*\`)

     * ValueError (Series item *[number]* cannot be plotted in a
       logarithmic axis because it contains negative data points)

    .. [[[end]]]
    """
    # pylint: disable=R0902,R0903,W0102
    def __init__(self, series=None, primary_axis_label='',
                 primary_axis_units='', primary_axis_ticks=None,
                 secondary_axis_label='', secondary_axis_units='',
                 secondary_axis_ticks=None, log_dep_axis=False,
                 legend_props=None, display_indep_axis=False):
        # Public attributes
        self._series = None
        self._axis_prim = None
        self._axis_sec = None
        self._primary_axis_label = None
        self._secondary_axis_label = None
        self._primary_axis_units = None
        self._secondary_axis_units = None
        self._primary_axis_ticks = None
        self._secondary_axis_ticks = None
        self._log_dep_axis = None
        self._recalculate_series = False
        self._legend_props = {'pos':'BEST', 'cols':1}
        self._display_indep_axis = None
        self._left = None
        self._bottom = None
        self._right = None
        self._top = None
        self._min_spine_bbox = None
        self._min_bbox = None
        # Private attributes
        self._legend_pos_list = [
            'best', 'upper right', 'upper left', 'lower left', 'lower right',
            'right', 'center left', 'center right', 'lower center',
            'upper center', 'center'
        ]
        self._has_prim_axis = False
        self._has_sec_axis = False
        self._primary_dep_var_min = None
        self._primary_dep_var_max = None
        self._primary_dep_var_div = None
        self._primary_dep_var_unit_scale = None
        self._primary_dep_var_locs = None
        self._primary_dep_var_labels = None
        self._secondary_dep_var_min = None
        self._secondary_dep_var_max = None
        self._secondary_dep_var_div = None
        self._secondary_dep_var_unit_scale = None
        self._secondary_dep_var_locs = None
        self._secondary_dep_var_labels = None
        self._legend_props_list = ['pos', 'cols']
        self._legend_props_pos_list = [
            'BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT',
            'RIGHT', 'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER',
            'UPPER CENTER', 'CENTER'
        ]
        # Exceptions definition
        invalid_prim_ex = pexdoc.exh.addai('primary_axis_ticks')
        invalid_sec_ex = pexdoc.exh.addai('secondary_axis_ticks')
        invalid_prim_ex(
            (primary_axis_ticks is not None) and (
            (not isinstance(primary_axis_ticks, list)) and
            (not isinstance(primary_axis_ticks, np.ndarray))
            )
        )
        invalid_sec_ex(
            (secondary_axis_ticks is not None) and (
            (not isinstance(secondary_axis_ticks, list)) and
            (not isinstance(secondary_axis_ticks, np.ndarray)))
        )
        # Assignment of arguments to attributes
        # Order here is important to avoid unnecessary re-calculating of
        # panel axes if log_dep_axis is True
        self._set_log_dep_axis(log_dep_axis)
        self._primary_axis_ticks = (
            primary_axis_ticks
            if not self.log_dep_axis else
            None
        )
        self._secondary_axis_ticks = (
            secondary_axis_ticks
            if not self.log_dep_axis else
            None
        )
        self._set_series(series)
        self._set_primary_axis_label(primary_axis_label)
        self._set_primary_axis_units(primary_axis_units)
        self._set_secondary_axis_label(secondary_axis_label)
        self._set_secondary_axis_units(secondary_axis_units)
        self._set_legend_props(legend_props)
        self._set_display_indep_axis(display_indep_axis)

    def __bool__(self): # pragma: no cover
        """
        Returns :code:`True` if the panel has at least a series associated
        with it, :code:`False` otherwise

        .. note:: This method applies to Python 3.x
        """
        return self._series is not None

    def __iter__(self):
        """
        Returns an iterator over the series object(s) in the panel. For
        example:

        .. =[=cog
        .. import pmisc.incfile
        .. pmisc.incfile('plot_example_6.py', cog.out)
        .. =]=
        .. code-block:: python

            # plot_example_6.py
            from __future__ import print_function
            import numpy, pplot

            def panel_iterator_example(no_print):
                source1 = pplot.BasicSource(
                    indep_var=numpy.array([1, 2, 3, 4]),
                    dep_var=numpy.array([1, -10, 10, 5])
                )
                source2 = pplot.BasicSource(
                    indep_var=numpy.array([100, 200, 300, 400]),
                    dep_var=numpy.array([50, 75, 100, 125])
                )
                series1 = pplot.Series(
                    data_source=source1,
                    label='Goals'
                )
                series2 = pplot.Series(
                    data_source=source2,
                    label='Saves',
                    color='b',
                    marker=None,
                    interp='STRAIGHT',
                    line_style='--'
                )
                panel = pplot.Panel(
                    series=[series1, series2],
                    primary_axis_label='Time',
                    primary_axis_units='sec',
                    display_indep_axis=True
                )
                if not no_print:
                    for num, series in enumerate(panel):
                        print('Series {0}:'.format(num+1))
                        print(series)
                        print('')
                else:
                    return panel

        .. =[=end=]=

        .. code-block:: python

            >>> import docs.support.plot_example_6 as mod
            >>> mod.panel_iterator_example(False)
            Series 1:
            Independent variable: [ 1.0, 2.0, 3.0, 4.0 ]
            Dependent variable: [ 1.0, -10.0, 10.0, 5.0 ]
            Label: Goals
            Color: k
            Marker: o
            Interpolation: CUBIC
            Line style: -
            Secondary axis: False
            <BLANKLINE>
            Series 2:
            Independent variable: [ 100.0, 200.0, 300.0, 400.0 ]
            Dependent variable: [ 50.0, 75.0, 100.0, 125.0 ]
            Label: Saves
            Color: b
            Marker: None
            Interpolation: STRAIGHT
            Line style: --
            Secondary axis: False
            <BLANKLINE>
        """
        return iter(self._series)

    def __nonzero__(self):  # pragma: no cover
        """
        Returns :code:`True` if the panel has at least a series associated
        with it, :code:`False` otherwise

        .. note:: This method applies to Python 2.x
        """
        return self._series is not None

    def _get_series(self):
        return self._series

    def _set_series(self, series):
        # pylint: disable=C0103
        self._series = (
            (series if isinstance(series, list) else [series])
            if series is not None else
            series
        )
        self._recalculate_series = False
        if self.series is not None:
            self._validate_series()
            self._has_prim_axis = any(
                not series_obj.secondary_axis for series_obj in self.series
            )
            self._has_sec_axis = any(
                series_obj.secondary_axis for series_obj in self.series
            )
            comp_prim_dep_var = (
                (not self.log_dep_axis) and self._has_prim_axis
            )
            comp_sec_dep_var = (
                (not self.log_dep_axis) and self._has_sec_axis
            )
            panel_has_primary_interp_series = any(
                [
                    (not series_obj.secondary_axis) and
                    (series_obj.interp_dep_var is not None)
                    for series_obj in self.series
                ]
            )
            panel_has_secondary_interp_series = any(
                [
                    series_obj.secondary_axis and
                    (series_obj.interp_dep_var is not None)
                    for series_obj in self.series
                ]
            )
            # Compute panel scaling factor
            primary_min = None
            prim_interp_min = None
            secondary_min = None
            sec_interp_min = None
            primary_max = None
            prim_interp_max = None
            secondary_max = None
            sec_interp_max = None
            panel_min = None
            panel_max = None
            # Find union of all data points and panel minimum and maximum.
            # If panel has logarithmic dependent axis, limits are common and
            # the union of the limits of both axis
            # Primary axis
            glob_prim_dep_var = (
                np.unique(
                    np.concatenate(
                        [
                            series_obj.dep_var
                            for series_obj in self.series
                            if not series_obj.secondary_axis
                        ]
                    )
                )
                if comp_prim_dep_var else
                None
            )
            prim_interp_min = (
                min(
                    [
                        min(series_obj.dep_var)
                        for series_obj in self.series
                        if ((not series_obj.secondary_axis) and
                           (series_obj.interp_dep_var is not None))
                    ]
                )
                if panel_has_primary_interp_series else
                None
            )
            prim_interp_max = (
                max(
                    [
                        max(series_obj.dep_var)
                        for series_obj in self.series
                        if ((not series_obj.secondary_axis) and
                           (series_obj.interp_dep_var is not None))
                    ]
                )
                if panel_has_primary_interp_series else
                None
            )
            primary_min = (
                min(min(glob_prim_dep_var), prim_interp_min)
                if comp_prim_dep_var and (prim_interp_min is not None) else
                (min(glob_prim_dep_var) if comp_prim_dep_var else None)
            )
            primary_max = (
                max(max(glob_prim_dep_var), prim_interp_max)
                if comp_prim_dep_var and (prim_interp_min is not None) else
                (max(glob_prim_dep_var) if comp_prim_dep_var else None)
            )
            # Secondary axis
            glob_sec_dep_var = (
                np.unique(
                    np.concatenate(
                        [
                            series_obj.dep_var
                            for series_obj in self.series
                            if series_obj.secondary_axis
                        ]
                    )
                )
                if comp_sec_dep_var else
                None
            )
            sec_interp_min = (
                min(
                    [
                        min(series_obj.dep_var)
                        for series_obj in self.series
                        if (series_obj.secondary_axis and
                           (series_obj.interp_dep_var is not None))
                    ]
                ).tolist()
                if panel_has_secondary_interp_series else
                None
            )
            sec_interp_max = (
                max(
                    [
                        max(series_obj.dep_var)
                        for series_obj in self.series
                        if (series_obj.secondary_axis and
                           (series_obj.interp_dep_var is not None))
                    ]
                ).tolist()
                if panel_has_secondary_interp_series else
                None
            )
            secondary_min = (
                min(min(glob_sec_dep_var), sec_interp_min)
                if comp_sec_dep_var and (sec_interp_min is not None) else
                (min(glob_sec_dep_var) if comp_sec_dep_var else None)
            )
            secondary_max = (
                max(max(glob_sec_dep_var), sec_interp_max)
                if comp_sec_dep_var and (sec_interp_max is not None) else
                (max(glob_sec_dep_var) if comp_sec_dep_var else None)
            )
            # Global (for logarithmic dependent axis)
            glob_panel_dep_var = (
                None
                if not self.log_dep_axis else
                np.unique(
                    np.concatenate(
                        [series_obj.dep_var for series_obj in self.series]
                    )
                )
            )
            panel_min = (
                min(min(glob_panel_dep_var), prim_interp_min)
                if self.log_dep_axis and panel_has_primary_interp_series else
                (min(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            panel_max = (
                max(max(glob_panel_dep_var), prim_interp_max)
                if self.log_dep_axis and panel_has_primary_interp_series else
                (max(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            panel_min = (
                min(min(glob_panel_dep_var), sec_interp_min)
                if self.log_dep_axis and panel_has_secondary_interp_series else
                (min(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            panel_max = (
                max(max(glob_panel_dep_var), sec_interp_max)
                if self.log_dep_axis and panel_has_secondary_interp_series else
                (max(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            # Get axis tick marks locations
            if comp_prim_dep_var:
                (
                    self._primary_dep_var_locs,
                    self._primary_dep_var_labels,
                    self._primary_dep_var_min,
                    self._primary_dep_var_max,
                    self._primary_dep_var_div,
                    self._primary_dep_var_unit_scale
                ) = _intelligent_ticks(
                        glob_prim_dep_var,
                        primary_min,
                        primary_max,
                        tight=False,
                        log_axis=self.log_dep_axis,
                        tick_list=self._primary_axis_ticks,
                    )
            if comp_sec_dep_var:
                (
                    self._secondary_dep_var_locs,
                    self._secondary_dep_var_labels,
                    self._secondary_dep_var_min,
                    self._secondary_dep_var_max,
                    self._secondary_dep_var_div,
                    self._secondary_dep_var_unit_scale
                ) = _intelligent_ticks(
                        glob_sec_dep_var,
                        secondary_min,
                        secondary_max,
                        tight=False,
                        log_axis=self.log_dep_axis,
                        tick_list=self._secondary_axis_ticks,
                    )
            if self.log_dep_axis and self._has_prim_axis:
                (
                    self._primary_dep_var_locs,
                    self._primary_dep_var_labels,
                    self._primary_dep_var_min,
                    self._primary_dep_var_max,
                    self._primary_dep_var_div,
                    self._primary_dep_var_unit_scale
                ) = _intelligent_ticks(
                        glob_panel_dep_var,
                        panel_min,
                        panel_max,
                        tight=False,
                        log_axis=self.log_dep_axis
                    )
            if self.log_dep_axis and self._has_sec_axis:
                (
                    self._secondary_dep_var_locs,
                    self._secondary_dep_var_labels,
                    self._secondary_dep_var_min,
                    self._secondary_dep_var_max,
                    self._secondary_dep_var_div,
                    self._secondary_dep_var_unit_scale
                ) = _intelligent_ticks(
                        glob_panel_dep_var,
                        panel_min,
                        panel_max,
                        tight=False,
                        log_axis=self.log_dep_axis
                    )
            # Equalize number of ticks on primary and secondary axis so that
            # ticks are in the same percentage place within the dependent
            # variable plotting interval (for non-logarithmic panels)
            # If there is any tick override (primary and/or secondary) this
            # is not done, the user assumes responsibility for aesthetics of
            # final result
            if ((not self.log_dep_axis) and
               self._has_prim_axis and
               self._has_sec_axis and
               (self._primary_axis_ticks is None) and
               (self._secondary_axis_ticks is None)):
                max_ticks = max(
                    len(self._primary_dep_var_locs),
                    len(self._secondary_dep_var_locs)
                )-1
                primary_delta = (
                    (
                        self._primary_dep_var_locs[-1]-
                        self._primary_dep_var_locs[0]
                    )
                    /
                    float(max_ticks)
                )
                secondary_delta = (
                    (
                        self._secondary_dep_var_locs[-1]-
                        self._secondary_dep_var_locs[0]
                    )
                    /
                    float(max_ticks)
                )
                self._primary_dep_var_locs = [
                    self._primary_dep_var_locs[0]+(num*primary_delta)
                    for num in range(max_ticks+1)
                ]
                self._secondary_dep_var_locs = [
                    self._secondary_dep_var_locs[0]+(num*secondary_delta)
                    for num in range(max_ticks+1)
                ]
                (
                    self._primary_dep_var_locs,
                    self._primary_dep_var_labels
                ) = _uniquify_tick_labels(
                        self._primary_dep_var_locs,
                        self._primary_dep_var_locs[0],
                        self._primary_dep_var_locs[-1]
                    )
                (
                    self._secondary_dep_var_locs,
                    self._secondary_dep_var_labels
                ) = _uniquify_tick_labels(
                        self._secondary_dep_var_locs,
                        self._secondary_dep_var_locs[0],
                        self._secondary_dep_var_locs[-1]
                    )
            self._primary_axis_ticks = self._primary_dep_var_locs
            self._secondary_axis_ticks = self._secondary_dep_var_locs
            # Scale panel
            self._scale_dep_var(
                self._primary_dep_var_div,
                self._secondary_dep_var_div
            )

    def _get_primary_axis_scale(self):
        return self._primary_dep_var_div

    def _get_primary_axis_ticks(self):
        return self._primary_axis_ticks

    def _get_secondary_axis_scale(self):
        return self._secondary_dep_var_div

    def _get_secondary_axis_ticks(self):
        return self._secondary_axis_ticks

    def _get_primary_axis_label(self):
        return self._primary_axis_label

    @pexdoc.pcontracts.contract(primary_axis_label='None|str')
    def _set_primary_axis_label(self, primary_axis_label):
        self._primary_axis_label = primary_axis_label

    def _get_primary_axis_units(self):
        return self._primary_axis_units

    @pexdoc.pcontracts.contract(primary_axis_units='None|str')
    def _set_primary_axis_units(self, primary_axis_units):
        self._primary_axis_units = primary_axis_units

    def _get_secondary_axis_label(self):
        return self._secondary_axis_label

    @pexdoc.pcontracts.contract(secondary_axis_label='None|str')
    def _set_secondary_axis_label(self, secondary_axis_label):
        self._secondary_axis_label = secondary_axis_label

    def _get_secondary_axis_units(self):
        return self._secondary_axis_units

    @pexdoc.pcontracts.contract(secondary_axis_units='None|str')
    def _set_secondary_axis_units(self, secondary_axis_units):
        self._secondary_axis_units = secondary_axis_units

    def _get_log_dep_axis(self):
        return self._log_dep_axis

    @pexdoc.pcontracts.contract(log_dep_axis='None|bool')
    def _set_log_dep_axis(self, log_dep_axis):
        self._recalculate_series = self.log_dep_axis != log_dep_axis
        self._log_dep_axis = log_dep_axis
        if self._recalculate_series:
            self._set_series(self._series)

    def _get_display_indep_axis(self):
        return self._display_indep_axis

    @pexdoc.pcontracts.contract(display_indep_axis='None|bool')
    def _set_display_indep_axis(self, display_indep_axis):
        self._display_indep_axis = display_indep_axis

    def _get_legend_props(self):
        return self._legend_props

    @pexdoc.pcontracts.contract(legend_props='None|dict')
    def _set_legend_props(self, legend_props):
        invalid_ex = pexdoc.exh.addex(
            ValueError, 'Illegal legend property `*[prop_name]*`'
        )
        illegal_ex = pexdoc.exh.addex(
            TypeError,
            "Legend property `pos` is not one of ['BEST', 'UPPER RIGHT', "
            "'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', "
            "'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', "
            "'UPPER CENTER', 'CENTER'] (case insensitive)"
        )
        cols_ex = pexdoc.exh.addex(
            RuntimeError, 'Legend property `cols` is not valid'
        )
        self._legend_props = (
            legend_props
            if legend_props is not None else
            {'pos':'BEST', 'cols':1}
        )
        self._legend_props.setdefault('pos', 'BEST')
        self._legend_props.setdefault('cols', 1)
        for key, value in self.legend_props.items():
            invalid_ex(
                key not in self._legend_props_list, _F('prop_name', key)
            )
            illegal_ex(
                (key == 'pos') and
                _legend_position_validation(self.legend_props['pos'])
            )
            cols_ex(
                ((key == 'cols') and (not isinstance(value, int))) or
                ((key == 'cols') and
                (isinstance(value, int) is True) and (value < 0))
            )
        self._legend_props['pos'] = self._legend_props['pos'].upper()

    def __str__(self):
        """
        Prints panel information. For example:

        .. code-block:: python

            >>> from __future__ import print_function
            >>> import docs.support.plot_example_6 as mod
            >>> print(mod.panel_iterator_example(True))
            Series 0:
               Independent variable: [ 1.0, 2.0, 3.0, 4.0 ]
               Dependent variable: [ 1.0, -10.0, 10.0, 5.0 ]
               Label: Goals
               Color: k
               Marker: o
               Interpolation: CUBIC
               Line style: -
               Secondary axis: False
            Series 1:
               Independent variable: [ 100.0, 200.0, 300.0, 400.0 ]
               Dependent variable: [ 50.0, 75.0, 100.0, 125.0 ]
               Label: Saves
               Color: b
               Marker: None
               Interpolation: STRAIGHT
               Line style: --
               Secondary axis: False
            Primary axis label: Time
            Primary axis units: sec
            Secondary axis label: not specified
            Secondary axis units: not specified
            Logarithmic dependent axis: False
            Display independent axis: True
            Legend properties:
               cols: 1
               pos: BEST
        """
        ret = ''
        if (self.series is None) or (len(self.series) == 0):
            ret += 'Series: None\n'
        else:
            for num, element in enumerate(self.series):
                ret += 'Series {0}:\n'.format(num)
                temp = str(element).split('\n')
                temp = [3*' '+line for line in temp]
                ret += '\n'.join(temp)
                ret += '\n'
        ret += 'Primary axis label: {0}\n'.format(
            self.primary_axis_label
            if self.primary_axis_label not in ['', None] else
            'not specified'
        )
        ret += 'Primary axis units: {0}\n'.format(
            self.primary_axis_units
            if self.primary_axis_units not in ['', None] else
            'not specified'
        )
        ret += 'Secondary axis label: {0}\n'.format(
            self.secondary_axis_label
            if self.secondary_axis_label not in ['', None] else
            'not specified'
        )
        ret += 'Secondary axis units: {0}\n'.format(
            self.secondary_axis_units
            if self.secondary_axis_units not in ['', None] else
            'not specified'
        )
        ret += 'Logarithmic dependent axis: {0}\n'.format(self.log_dep_axis)
        ret += (
            'Display independent '
            'axis: {0}\n'.format(self.display_indep_axis)
        )
        ret += 'Legend properties:\n'
        iobj = enumerate(sorted(list(self.legend_props.items())))
        for num, (key, value) in iobj:
            ret += '   {0}: {1}{2}'.format(
                key, value, '\n' if num+1 < len(self.legend_props) else ''
            )
        return ret

    def _top_adjust(self):
        axes = [self._axis_prim, self._axis_sec]
        axes = [axis for axis in axes if axis]
        title_top = _lmax([axis.title_bbox.ymax for axis in axes])
        title_bot = _lmax([axis.title_bbox.ymin for axis in axes])
        ytick_top = _lmax([axis.yticklabels_bbox.ymax for axis in axes])
        ylabel_top = _lmax([axis.ylabel_bbox.ymax for axis in axes])
        top = _lmax([title_top, ytick_top, ylabel_top])
        bottom = _lmax([title_bot, ytick_top, ylabel_top])
        return top-bottom

    def _validate_series(self):
        """
        Verifies that elements of series list are of the right type and
        fully specified
        """
        invalid_ex = pexdoc.exh.addai('series')
        incomplete_ex = pexdoc.exh.addex(
            RuntimeError, 'Series item *[number]* is not fully specified'
        )
        log_ex = pexdoc.exh.addex(
            ValueError,
            'Series item *[number]* cannot be plotted in a logarithmic '
            'axis because it contains negative data points'
        )
        for num, obj in enumerate(self.series):
            invalid_ex(not isinstance(obj, Series))
            incomplete_ex(not obj._complete, _F('number', num))
            log_ex(
                bool((min(obj.dep_var) <= 0) and self.log_dep_axis),
                _F('number', num)
            )

    def _get_complete(self):
        """
        Returns True if panel is fully specified, otherwise returns False
        """
        return (self.series is not None) and (len(self.series) > 0)

    def _left_adjust(self):
        axes = [self._axis_prim or self._axis_sec]
        title_edge = _lmin([axis.title_bbox.xmin for axis in axes])
        xtick_edge = _lmin([axis.xticklabels_bbox.xmin for axis in axes])
        xlabel_edge = _lmin([axis.xlabel_bbox.xmin for axis in axes])
        spine_edge = _lmin([axis.spine_bbox.xmin for axis in axes])
        x_edge = (
            -_lmin([axis.xaxis_left for axis in axes])
            if (not self._axis_prim) and self._axis_sec else
            _lmin(title_edge, spine_edge, xtick_edge, xlabel_edge)
        )
        y_edge = _lmin([axis.yaxis_left for axis in axes])
        return (
            x_edge
            if (not self._axis_prim) and self._axis_sec else
            -_lmin(y_edge, x_edge)
        )

    def _right_adjust(self):
        axes = [self._axis_prim, self._axis_sec]
        axes = [axis for axis in axes if axis]
        title_edge = _lmax([axis.title_bbox.xmax for axis in axes])
        xtick_edge = _lmax([axis.xticklabels_bbox.xmax for axis in axes])
        xlabel_edge = _lmax([axis.xlabel_bbox.xmax for axis in axes])
        spine_edge = _lmax([axis.spine_bbox.xmax for axis in axes])
        x_edge = (
            _lmax(title_edge, spine_edge, xtick_edge, xlabel_edge)
            if self._axis_prim and self._axis_sec else
            self._axis_sec.yaxis_left
        )
        y_edge = self._axis_sec.yaxis_right
        return _lmax(0, y_edge-x_edge)

    def _scale_indep_var(self, scaling_factor):
        """ Scale independent variable of panel series """
        for series_obj in self.series:
            series_obj._scale_indep_var(scaling_factor)

    def _scale_dep_var(self, primary_scaling_factor, secondary_scaling_factor):
        """ Scale dependent variable of panel series """
        for series_obj in self.series:
            if not series_obj.secondary_axis:
                series_obj._scale_dep_var(primary_scaling_factor)
            else:
                series_obj._scale_dep_var(secondary_scaling_factor)

    def _setup_axis(
            self, axis_type, axis_obj,
            indep_min, indep_max,
            indep_tick_locs, indep_tick_labels,
            indep_axis_label, indep_axis_units, indep_axis_scale, draw_label
    ):
        """ Configure dependent axis """
        prim_dict = dict(
            ymin=self._primary_dep_var_min,
            ymax=self._primary_dep_var_max,
            ticks=self._primary_dep_var_locs,
            tick_labels=self._primary_dep_var_labels,
            axis_label=self.primary_axis_label,
            axis_units=self.primary_axis_units,
            axis_scale=self._primary_dep_var_unit_scale,
        )
        sec_dict = dict(
            ymin=self._secondary_dep_var_min,
            ymax=self._secondary_dep_var_max,
            ticks=self._secondary_dep_var_locs,
            tick_labels=self._secondary_dep_var_labels,
            axis_label=self.secondary_axis_label,
            axis_units=self.secondary_axis_units,
            axis_scale=self._secondary_dep_var_unit_scale,
        )
        #
        dep_dict = prim_dict if axis_type == 'PRIMARY' else sec_dict
        ylim = [dep_dict['ymin'], dep_dict['ymax']]
        lsize = AXIS_TICKS_FONT_SIZE
        axis_obj.tick_params(axis='x', which='major', labelsize=lsize, zorder=4)
        axis_obj.tick_params(axis='y', which='major', labelsize=lsize, zorder=4)
        axis_obj.xaxis.set_ticks(indep_tick_locs)
        axis_obj.yaxis.set_ticks(dep_dict['ticks'])
        axis_obj.set_xlim([indep_min, indep_max], emit=True, auto=False)
        axis_obj.set_ylim(ylim, emit=True, auto=False)
        axis_obj.set_axisbelow(True)
        axis_obj.xaxis.set_ticklabels(indep_tick_labels)
        axis_obj.yaxis.set_ticklabels(dep_dict['tick_labels'])
        if draw_label:
            self._draw_label(
                axis_obj.xaxis,
                indep_axis_label,
                indep_axis_units,
                indep_axis_scale
            )
        self._draw_label(
            axis_obj.yaxis,
            dep_dict['axis_label'],
            dep_dict['axis_units'],
            dep_dict['axis_scale']
        )

    def _bottom_adjust(self):
        axes = [self._axis_prim, self._axis_sec]
        axes = [axis for axis in axes if axis]
        y_edge = _lmin([axis.yaxis_bottom for axis in axes])
        x_edge = (self._axis_prim or self._axis_sec).xaxis_bottom
        return _lmax(0, -_lmin(y_edge, x_edge))

    def _draw(
            self,
            num_panels,
            num_panel,
            indep_axis_dict,
            title,
            fig_width=None,
            fig_height=None
    ):
        disp_indep_axis = (num_panels == 1) or self._display_indep_axis
        self._draw_core(
            num_panels, num_panel, indep_axis_dict, disp_indep_axis, title
        )
        if fig_width and fig_height:
            xdelta_right = (
                self._right_adjust()/fig_width if self._axis_sec else 0
            )
            xdelta_left = self._left_adjust()/fig_width
            ydelta_top = self._top_adjust()/fig_height
            ydelta_bot = self._bottom_adjust()/fig_height
            fbbox = [
                0+xdelta_left, 0+ydelta_bot, 1-xdelta_right, 1-ydelta_top
            ]
            if xdelta_right or xdelta_left or ydelta_top or ydelta_bot:
                plt.delaxes(self._axis_prim.axis)
                self._draw_core(
                    num_panels,
                    num_panel,
                    indep_axis_dict,
                    disp_indep_axis,
                    title,
                    fbbox
                )

    def _draw_core(
            self,
            num_panels,
            num_panel,
            indep_axis_dict,
            disp_indep_axis,
            title,
            fbbox=None,
    ):
        """ Draw panel series """
        # pylint: disable=W0612
        def amin(prim, sec, prop):
            return min(
                getattr(prim, prop) if self._axis_prim else INF,
                getattr(sec, prop) if self._axis_sec else INF
            )
        def amax(prim, sec, prop):
            return max(
                getattr(prim, prop) if self._axis_prim else -INF,
                getattr(sec, prop) if self._axis_sec else -INF
            )
        zero = lambda x: x if x is not None else 0
        gkey = lambda key: (
            ''
            if indep_axis_dict[key] is None or not disp_indep_axis else
            indep_axis_dict[key].strip()
        )
        axis_prim = plt.subplot(num_panels, 1, num_panel+1)
        if self._has_prim_axis:
            self._setup_axis(
                'PRIMARY',
                axis_prim,
                indep_axis_dict['indep_var_min'],
                indep_axis_dict['indep_var_max'],
                indep_axis_dict['indep_var_locs'],
                indep_axis_dict.get('indep_var_labels', None),
                gkey('indep_axis_label'),
                gkey('indep_axis_units'),
                gkey('indep_axis_unit_scale'),
                True
            )
        plt.tight_layout(rect=fbbox, pad=0, h_pad=2)
        axis_sec = None
        tobjs = None
        if self._has_sec_axis:
            axis_sec = plt.axes(axis_prim.get_position(), frameon=False)
            self._setup_axis(
                'SECONDARY',
                axis_sec,
                indep_axis_dict['indep_var_min'],
                indep_axis_dict['indep_var_max'],
                indep_axis_dict['indep_var_locs'],
                indep_axis_dict.get('indep_var_labels', None),
                gkey('indep_axis_label'),
                gkey('indep_axis_units'),
                gkey('indep_axis_unit_scale'),
                not self._has_prim_axis
            )
            axis_sec.yaxis.set_label_position('right')
            axis_sec.yaxis.set_ticks_position('right')
            if self._has_prim_axis:
                # Get individual label tick boxes to determine minimum spine
                # size before they are turned off
                tobjs = axis_sec.xaxis.get_ticklabels()
                tobjs = [
                    label for label in tobjs if label.get_text().strip()
                ]
                axis_sec.tick_params(
                    axis='x', which='both', length=0, labelbottom='off'
                )
                axis_prim.set_zorder(axis_sec.get_zorder()+1)
                axis_prim.patch.set_visible(False)
            else:
                axis_prim.xaxis.set_ticks([])
                axis_prim.yaxis.set_ticks([])
            axis_sec.xaxis.grid(True, which='both', zorder=2)
            axis_sec.yaxis.grid(True, which='both', zorder=2)
        else:
            axis_prim.xaxis.grid(True, which='both', zorder=2)
            axis_prim.yaxis.grid(True, which='both', zorder=2)
        # Place data series in their appropriate axis (primary or secondary)
        prim_log_axis = sec_log_axis = False
        # Reverse series list so that first series is drawn on top
        for series_obj in reversed(self.series):
            series_obj._draw(
                axis_prim if not series_obj.secondary_axis else axis_sec,
                indep_axis_dict['log_indep'],
                self.log_dep_axis,
            )
            prim_log_axis = (
                prim_log_axis
                if prim_log_axis else
                (not series_obj.secondary_axis) and self.log_dep_axis
            )
            sec_log_axis = (
                sec_log_axis
                if sec_log_axis else
                series_obj.secondary_axis and self.log_dep_axis
            )
        # Print legend
        if (len(self.series) > 1) and (len(self.legend_props) > 0):
            _, primary_labels = (
                axis_prim.get_legend_handles_labels()
                if self._has_prim_axis else
                (None, [])
            )
            _, secondary_labels = (
                axis_sec.get_legend_handles_labels()
                if self._has_sec_axis else
                (None, [])
            )
            lprim = len(primary_labels)
            lsec = len(secondary_labels)
            labels = (
                (
                    [r'$\Leftarrow$'+label for label in primary_labels]+
                    [label+r'$\Rightarrow$' for label in secondary_labels]
                )
                if (lprim > 0) and (lsec > 0) else
                primary_labels+secondary_labels
            )
            if any([bool(label) for label in labels]):
                leg_artist = [
                    series_obj._legend_artist(LEGEND_SCALE)
                    for series_obj in self.series
                    if series_obj._check_series_is_plottable()
                ]
                legend_axis = (
                    axis_prim
                    if self._has_prim_axis and (
                        not self._has_sec_axis
                    ) else
                    axis_sec
                )
                loc_key = self._legend_pos_list.index(
                    self.legend_props['pos'].lower()
                    if 'pos' in self.legend_props else 'lower left'
                )
                legend_axis.legend(
                    leg_artist,
                    labels,
                    ncol=(
                        self.legend_props['cols']
                        if 'cols' in self.legend_props else
                        len(labels)
                    ),
                    loc=self._legend_pos_list[loc_key],
                    numpoints=1,
                    fontsize=AXIS_LABEL_FONT_SIZE/LEGEND_SCALE,
                    facecolor='white',
                    framealpha=1.0,
                )
        if title not in [None, '']:
            axis = (
                axis_prim if self._has_prim_axis else axis_sec
            )
            axis.set_title(
                title,
                horizontalalignment='center',
                verticalalignment='bottom',
                multialignment='center',
                fontsize=TITLE_FONT_SIZE
            )
        # This is necessary because if there is no primary axis but there
        # is a secondary axis, then the independent axis bounding boxes
        # are all stacked up in the same spot
        axis_prim.display_indep_axis = (
            self.display_indep_axis or (num_panels == 1)
        )
        axis_prim.yaxis.log_axis = prim_log_axis
        axis_prim.xaxis.log_axis = indep_axis_dict['log_indep']
        if axis_sec:
            axis_sec.xaxis.log_axis = indep_axis_dict['log_indep']
            axis_sec.yaxis.log_axis = sec_log_axis
            axis_sec.display_indep_axis = False
        self._axis_prim = _Axis(axis_prim, 'prim', tobjs) if axis_prim else None
        self._axis_sec = _Axis(axis_sec, 'sec', tobjs) if axis_sec else None
        self._left = amin(self._axis_prim, self._axis_sec, 'left')
        self._bottom = amin(self._axis_prim, self._axis_sec, 'bottom')
        self._right = amax(self._axis_prim, self._axis_sec, 'right')
        self._top = amax(self._axis_prim, self._axis_sec, 'top')
        spine_min_width = amax(
            self._axis_prim._min_spine_bbox if self._axis_prim else None,
            self._axis_sec._min_spine_bbox if self._axis_sec else None,
            'width'
        )
        spine_min_height = amax(
            self._axis_prim._min_spine_bbox if self._axis_prim else None,
            self._axis_sec._min_spine_bbox if self._axis_sec else None,
            'height'
        )
        self._min_spine_bbox = Bbox(
            [[0, 0], [spine_min_width, spine_min_height]]
        )
        left_label_plus_pad = 0
        right_label_plus_pad = 0
        prim_left_overhang = 0
        prim_bottom_overhang = 0
        prim_right_overhang = 0
        prim_top_overhang = 0
        prim_title_plus_pad = 0
        prim_xlabel_plus_pad = 0
        sec_label_plus_pad = 0
        sec_left_overhang = 0
        sec_bottom_overhang = 0
        sec_right_overhang = 0
        sec_top_overhang = 0
        sec_title_plus_pad = 0
        sec_xlabel_plus_pad = 0
        if self._has_prim_axis:
            left_label_plus_pad = zero(self._axis_prim.ylabel_plus_pad)
            prim_left_overhang = zero(self._axis_prim.left_overhang)
            prim_right_overhang = zero(self._axis_prim.right_overhang)
            prim_bottom_overhang = zero(self._axis_prim.bottom_overhang)
            prim_top_overhang = zero(self._axis_prim.top_overhang)
            prim_title_plus_pad = zero(self._axis_prim.title_plus_pad)
            prim_xlabel_plus_pad = zero(
                self._axis_prim.xlabel_plus_pad
            )
        if self._has_sec_axis:
            right_label_plus_pad = zero(self._axis_sec.ylabel_plus_pad)
            sec_left_overhang = zero(self._axis_sec.left_overhang)
            sec_right_overhang = zero(self._axis_sec.right_overhang)
            sec_bottom_overhang = zero(self._axis_sec.bottom_overhang)
            sec_top_overhang = zero(self._axis_sec.top_overhang)
            sec_title_plus_pad = zero(self._axis_sec.title_plus_pad)
            sec_xlabel_plus_pad = zero(
                self._axis_sec.xlabel_plus_pad
            )
        title_plus_pad = max(
            prim_title_plus_pad, sec_title_plus_pad
        )
        left_overhang = max(prim_left_overhang, sec_left_overhang)
        bottom_overhang = max(prim_bottom_overhang, sec_bottom_overhang)
        right_overhang = max(prim_right_overhang, sec_right_overhang)
        top_overhang = max(prim_top_overhang, sec_top_overhang)
        xlabel_plus_pad = max(
            prim_xlabel_plus_pad, sec_bottom_overhang
        )
        panel_min_width = (
            left_label_plus_pad+
            left_overhang+
            self._min_spine_bbox.width+
            right_overhang+
            right_label_plus_pad
        )
        panel_min_height = (
            xlabel_plus_pad+
            bottom_overhang+
            self._min_spine_bbox.height+
            top_overhang+
            title_plus_pad
        )
        self._min_bbox = Bbox([[0, 0], [panel_min_width, panel_min_height]])

    def _draw_label(self, axis, axis_label, axis_units, axis_scale):
        # pylint: disable=R0201
        if (axis_label not in [None, '']) or (axis_units not in [None, '']):
            axis_label = (axis_label or '').strip()
            unit_scale = (axis_scale or '').strip()
            empty_units = (unit_scale == '') and (axis_units == '')
            units_str = ' [{0}{1}]'.format(unit_scale, axis_units or '-')
            fdict = dict(fontsize=AXIS_LABEL_FONT_SIZE)
            axis.set_label_text(
                axis_label+('' if empty_units else units_str), fontdict=fdict
            )

    _complete = property(_get_complete)

    display_indep_axis = property(
        _get_display_indep_axis,
        _set_display_indep_axis,
        doc='Show independent axis flag'
    )
    r"""
    Gets or sets the independent axis display flag; indicates whether the
    independent axis is displayed (True) or not (False)

    :type: boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.display_indep_axis

    :raises: (when assigned) RuntimeError (Argument \`display_indep_axis\`
     is not valid)

    .. [[[end]]]
    """

    legend_props = property(
        _get_legend_props, _set_legend_props, doc='Panel legend box properties'
    )
    r"""
    Gets or sets the panel legend box properties; this is a dictionary that
    has properties (dictionary key) and their associated values (dictionary
    values). Currently supported properties are:

    * **pos** (*string*) -- legend box position, one of :code:`'BEST'`,
      :code:`'UPPER RIGHT'`, :code:`'UPPER LEFT'`, :code:`'LOWER LEFT'`,
      :code:`'LOWER RIGHT'`, :code:`'RIGHT'`, :code:`'CENTER LEFT'`,
      :code:`'CENTER RIGHT'`, :code:`'LOWER CENTER'`, :code:`'UPPER CENTER'`
      or :code:`'CENTER'` (case insensitive)

    * **cols** (integer) -- number of columns of the legend box

    If :code:`None` the default used is :code:`{'pos':'BEST', 'cols':1}`

    .. note:: No legend is shown if a panel has only one series in it or if no
              series has a label

    :type: dictionary

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.legend_props

    :raises: (when assigned)

     * RuntimeError (Argument \`legend_props\` is not valid)

     * RuntimeError (Legend property \`cols\` is not valid)

     * TypeError (Legend property \`pos\` is not one of ['BEST', 'UPPER
       RIGHT', 'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', 'CENTER
       LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', 'CENTER']
       (case insensitive))

     * ValueError (Illegal legend property \`*[prop_name]*\`)

    .. [[[end]]]
    """

    log_dep_axis = property(
        _get_log_dep_axis,
        _set_log_dep_axis,
        doc='Panel logarithmic dependent axis flag'
    )
    r"""
    Gets or sets the panel logarithmic dependent (primary and/or secondary)
    axis flag; indicates whether the dependent (primary and/or secondary) axis
    is linear (False) or logarithmic (True)

    :type: boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.log_dep_axis

    :raises: (when assigned)

     * RuntimeError (Argument \`log_dep_axis\` is not valid)

     * RuntimeError (Argument \`series\` is not valid)

     * RuntimeError (Series item *[number]* is not fully specified)

     * ValueError (Series item *[number]* cannot be plotted in a
       logarithmic axis because it contains negative data points)

    .. [[[end]]]
    """

    primary_axis_label = property(
        _get_primary_axis_label,
        _set_primary_axis_label,
        doc='Panel primary axis label'
    )
    r"""
    Gets or sets the panel primary dependent axis label

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.primary_axis_label

    :raises: (when assigned) RuntimeError (Argument \`primary_axis_label\`
     is not valid)

    .. [[[end]]]
    """

    primary_axis_scale = property(
        _get_primary_axis_scale, doc='Primary axis scale'
    )
    """
    Gets the scale of the panel primary axis, :code:`None` if axis has no
    series associated with it

    :type: float or None
    """

    primary_axis_ticks = property(
        _get_primary_axis_ticks, doc='Primary axis tick locations'
    )
    """
    Gets the primary axis (scaled) tick locations, :code:`None` if axis has no
    series associated with it

    :type: list or None
    """

    primary_axis_units = property(
        _get_primary_axis_units,
        _set_primary_axis_units,
        doc='Panel primary axis units'
    )
    r"""
    Gets or sets the panel primary dependent axis units

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.primary_axis_units

    :raises: (when assigned) RuntimeError (Argument \`primary_axis_units\`
     is not valid)

    .. [[[end]]]
    """

    secondary_axis_label = property(
        _get_secondary_axis_label,
        _set_secondary_axis_label,
        doc='Panel secondary axis label'
    )
    r"""
    Gets or sets the panel secondary dependent axis label

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.secondary_axis_label

    :raises: (when assigned) RuntimeError (Argument
     \`secondary_axis_label\` is not valid)

    .. [[[end]]]
    """

    secondary_axis_scale = property(
        _get_secondary_axis_scale,
        doc='Secondary axis scale'
    )
    """
    Gets the scale of the panel secondary axis, :code:`None` if axis has no
    series associated with it

    :type: float or None
    """

    secondary_axis_ticks = property(
        _get_secondary_axis_ticks, doc='secondary axis tick locations'
    )
    """
    Gets the secondary axis (scaled) tick locations, :code:`None` if axis has
    no series associated with it


    :type:  list or None
     with it
    """

    secondary_axis_units = property(
        _get_secondary_axis_units,
        _set_secondary_axis_units,
        doc='Panel secondary axis units'
    )
    r"""
    Gets or sets the panel secondary dependent axis units

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.secondary_axis_units

    :raises: (when assigned) RuntimeError (Argument
     \`secondary_axis_units\` is not valid)

    .. [[[end]]]
    """

    series = property(_get_series, _set_series, doc='Panel series')
    r"""
    Gets or sets the panel series, :code:`None` if there are no series
    associated with the panel

    :type: :py:class:`pplot.Series`, list of
           :py:class:`pplot.Series` or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.series

    :raises: (when assigned)

     * RuntimeError (Argument \`series\` is not valid)

     * RuntimeError (Series item *[number]* is not fully specified)

     * ValueError (Series item *[number]* cannot be plotted in a
       logarithmic axis because it contains negative data points)

    .. [[[end]]]
    """
