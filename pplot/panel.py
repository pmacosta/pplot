"""
Define a panel within a figure.

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
# panel.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,C1801,R0205,R0902,R0903,R0912,R0913,R0914,R0915
# pylint: disable=W0105,W0212

# Standard library imports
import sys
import warnings

# PyPI imports
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.text import Text
    from matplotlib.transforms import Bbox
import pmisc
import pexdoc.exh
import pexdoc.pcontracts

# Intra-package imports
from .series import Series
from .functions import _F, _intelligent_ticks, _uniquify_tick_labels
from .constants import AXIS_LABEL_FONT_SIZE, AXIS_TICKS_FONT_SIZE, LEGEND_SCALE


###
# Constants
###
INF = sys.float_info.max
SPACER = 0.2  # in inches
GRID_ZORDER = 2
TICK_ZORDER = 4


###
# Functions
###
def _legend_position_validation(obj):
    """Validate if a string is a valid legend position."""
    options = [
        "BEST",
        "UPPER RIGHT",
        "UPPER LEFT",
        "LOWER LEFT",
        "LOWER RIGHT",
        "RIGHT",
        "CENTER LEFT",
        "CENTER RIGHT",
        "LOWER CENTER",
        "UPPER CENTER",
        "CENTER",
    ]
    if (obj is not None) and (not isinstance(obj, str)):
        return True
    if (obj is None) or (
        obj and any([item.lower() == obj.lower() for item in options])
    ):
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


def _turn_off_axis(axis, atype="x"):
    obj = axis.xaxis if atype == "x" else axis.yaxis
    for tick in obj.get_ticklabels() + obj.get_minorticklabels():
        tick.set_visible(False)
    for tick in obj.get_ticklines() + obj.get_minorticklines():
        tick.set_visible(False)
    obj.get_label().set_visible(False)


def _turn_off_minor_labels(axis, atype="x"):
    obj = axis.xaxis if atype == "x" else axis.yaxis
    for tick in obj.get_minorticklabels():
        tick.set_visible(False)
    for tick in obj.get_minorticklines():
        tick.set_visible(False)


###
# Classes
###
class _Axis(object):
    def __init__(self, axis, atype, ticklabels=None):
        self.axis = axis
        self.prim = atype.lower() == "prim"
        self.sec = atype.lower() == "sec"
        self.fig = axis.figure
        self.renderer = self.fig.canvas.get_renderer()
        self.ticklabels = ticklabels
        self.dummy_bbox = None
        # This call needs to happen first because it calculates the
        # dummy bounding box used for other getters
        self._get_spine_bbox()
        #
        self._xlabel = self.axis.xaxis.get_label().get_text().strip()
        self._ylabel = self.axis.yaxis.get_label().get_text().strip()
        self._get_xlabel()
        self._get_xlabel_bbox()
        self._get_xticklabels()
        self._get_xticklabels_bbox()
        self._get_ylabel()
        self._get_ylabel_bbox()
        self._get_yticklabels()
        self._get_yticklabels_bbox()
        self._get_left()
        self._get_bottom()
        self._get_right()
        self._get_top()
        self._get_min_spine_bbox()
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
            axis_dim = getattr(obj, prop)
            if prop in ["ymin", "ymax"]:
                spine_dim = getattr(self.spine_bbox, prop)
                func = _lmin if prop == "ymin" else _lmax
                return func(axis_dim, spine_dim)
            return axis_dim
        return None

    def _bbox(self, obj):
        """Return bounding box of an object."""
        return obj.get_window_extent(renderer=self.renderer).transformed(
            self.fig.dpi_scale_trans.inverted()
        )

    def _get_bottom(self):
        return _lmin([self.xaxis_bottom, self.yaxis_bottom])

    def _get_bottom_overhang(self):
        return self._get_yoverhang("ymin")

    def _get_left(self):
        return _lmin([self.xaxis_left, self.yaxis_left])

    def _get_left_overhang(self):
        return self._get_xoverhang("xmin")

    def _get_right(self):
        return _lmax([self.xaxis_right, self.yaxis_right])

    def _get_right_overhang(self):
        return self._get_xoverhang("xmax")

    def _get_spine_bbox(self):
        left = self._bbox(self.axis.spines["left"]).xmin
        bottom = self._bbox(self.axis.spines["bottom"]).ymin
        right = self._bbox(self.axis.spines["right"]).xmax
        top = self._bbox(self.axis.spines["top"]).ymax
        if self.dummy_bbox is None:
            # Create dummy bbox in the middle of the spine so as to not limit
            # measurements in any dimension
            xcenter = (left + right) / 2.0
            ycenter = (top + bottom) / 2.0
            self.dummy_bbox = Bbox([[xcenter, ycenter], [xcenter, ycenter]])
        return Bbox([[left, bottom], [right, top]])

    def _get_top(self):
        return _lmax([self.xaxis_top, self.yaxis_top])

    def _get_top_overhang(self):
        return self._get_yoverhang("ymax")

    def _get_xaxis_bottom(self):
        return self._axis_edge(self.axis.xaxis, "ymin")

    def _get_xaxis_left(self):
        return self._axis_edge(self.axis.xaxis, "xmin")

    def _get_xaxis_right(self):
        return self._axis_edge(self.axis.xaxis, "xmax")

    def _get_xaxis_top(self):
        return self._axis_edge(self.axis.xaxis, "ymax")

    def _get_xlabel(self):
        return self.axis.xaxis.get_label().get_text().strip()

    def _get_xlabel_bbox(self):
        return (
            self.dummy_bbox
            if self._xlabel is None
            else self._bbox(self.axis.xaxis.get_label())
        )

    def _get_xlabel_plus_pad(self):
        dim = lambda x: getattr(x, "ymin")
        spine_edge = dim(self.spine_bbox)
        edge = min(dim(self.xticklabels_bbox), spine_edge)
        return max(0, edge - dim(self.xlabel_bbox))

    def _get_xoverhang(self, prop):
        sign = -1 if prop == "xmin" else +1
        dim = lambda x: getattr(x, prop)
        mid = dim(self.spine_bbox)
        ylabel_overhang = self._get_ylabel_plus_pad()
        ytick = dim(self.yticklabels_bbox) if self.yticklabels_bbox else mid
        ytick_overhang = max(0, sign * (ytick - mid))
        xtick = dim(self.xticklabels_bbox) if self.xticklabels_bbox else mid
        xtick_overhang = (
            max(0, sign * (xtick - mid)) if self.axis.display_indep_axis else 0
        )
        xlabel_overhang = (
            max(0, sign * (dim(self.xlabel_bbox) - mid))
            if self.axis.display_indep_axis
            else 0
        )
        if (self.prim and (prop == "xmin")) or (self.sec and (prop == "xmax")):
            ret = max(
                max(xtick_overhang, ytick_overhang) + ylabel_overhang, xlabel_overhang
            )
        else:
            ret = xtick_overhang
        return ret

    def _get_xticklabels(self):
        return [
            label.get_text().strip()
            for label in self.axis.xaxis.get_ticklabels()
            if label.get_text().strip()
        ] or None

    def _get_xticklabels_bbox(self):
        ticks = self.axis.xaxis.get_ticklabels()
        tick_bboxes = [
            self._bbox(tick_bbox) for tick_bbox in ticks if tick_bbox.get_text().strip()
        ]
        if not tick_bboxes:
            return self.dummy_bbox
        left = _lmin([tick_bbox.xmin for tick_bbox in tick_bboxes])
        right = _lmax([tick_bbox.xmax for tick_bbox in tick_bboxes])
        bottom = _lmin([tick_bbox.ymin for tick_bbox in tick_bboxes])
        top = _lmax([tick_bbox.ymax for tick_bbox in tick_bboxes])
        return Bbox([[left, bottom], [right, top]])

    def _get_yticklabels(self):
        return [
            label.get_text().strip()
            for label in self.axis.yaxis.get_ticklabels()
            if label.get_text().strip()
        ] or None

    def _get_yaxis_bottom(self):
        return self._axis_edge(self.axis.yaxis, "ymin")

    def _get_yaxis_left(self):
        return self._axis_edge(self.axis.yaxis, "xmin")

    def _get_yaxis_right(self):
        return self._axis_edge(self.axis.yaxis, "xmax")

    def _get_yaxis_top(self):
        return self._axis_edge(self.axis.yaxis, "ymax")

    def _get_ylabel(self):
        return self.axis.yaxis.get_label().get_text().strip()

    def _get_ylabel_bbox(self):
        return (
            self.dummy_bbox
            if self._ylabel is None
            else self._bbox(self.axis.yaxis.get_label())
        )

    def _get_ylabel_plus_pad(self):
        if not self.ylabel:
            return 0
        sign = -1 if self.prim else +1
        func = min if self.prim else max
        prop = "xmin" if self.prim else "xmax"
        dim = lambda x: getattr(x, prop)
        spine_edge = dim(self.spine_bbox)
        edge = func(dim(self.yticklabels_bbox), spine_edge)
        return max(0, sign * (dim(self.ylabel_bbox) - edge))

    def _get_yoverhang(self, prop):
        sign = -1 if prop == "ymin" else +1
        dim = lambda x: getattr(x, prop)
        mid = dim(self.spine_bbox)
        label = dim(self.ylabel_bbox)
        label_overhang = max(0, sign * (label - mid))
        xtick = dim(self.xticklabels_bbox) if self.xticklabels_bbox else mid
        xtick_overhang = max(0, sign * (xtick - mid))
        ytick = dim(self.yticklabels_bbox) if self.yticklabels_bbox else mid
        ytick_overhang = max(0, sign * (ytick - mid))
        return max(label_overhang, xtick_overhang, ytick_overhang)

    def _get_yticklabels_bbox(self):
        ticks = self.axis.yaxis.get_ticklabels()
        tick_bboxes = [
            self._bbox(tick_bbox) for tick_bbox in ticks if tick_bbox.get_text().strip()
        ]
        left = _lmin([tick_bbox.xmin for tick_bbox in tick_bboxes])
        right = _lmax([tick_bbox.xmax for tick_bbox in tick_bboxes])
        bottom = _lmin([tick_bbox.ymin for tick_bbox in tick_bboxes])
        top = _lmax([tick_bbox.ymax for tick_bbox in tick_bboxes])
        return Bbox([[left, bottom], [right, top]])

    def _get_min_spine_bbox(self):
        def core(xaxis):
            # pylint: disable=C0325
            sep = (1.5 if xaxis else 0.5) * SPACER
            dim = "width" if xaxis else "height"
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
            # Get rid of NaNs in bboxes
            bboxes = [
                self._bbox(Text(x=0.5, y=0.5, text=label, figure=self.fig))
                if not (-INF <= getattr(bbox, dim) <= INF)
                else bbox
                for bbox, label in zip(bboxes[:], tick_labels)
            ]
            bboxes = [bbox for bbox in bboxes if -INF <= getattr(bbox, dim) <= INF]
            mult = 3 if axis.log_axis else 1
            label_half_dim = [
                (getattr(bbox, dim) + mult * sep) / 2.0 for bbox in bboxes
            ]
            min_label_half_dim = (
                max(label_half_dim) * (len(label_half_dim) - 1) if label_half_dim else 0
            )
            if axis.log_axis or (not label_half_dim):
                return min_label_half_dim
            tick_diffs = np.diff(np.array(locs))
            curr_label, prev_label = label_half_dim[1:], label_half_dim[:-1]
            sep_dim = [curr + prev for curr, prev in zip(curr_label, prev_label)]
            dpu = max(sep_dim / tick_diffs)
            axis_box_dim = (locs[-1] - locs[0]) * dpu
            return axis_box_dim

        width = core(xaxis=True)
        height = core(xaxis=False)
        ret = Bbox([[0, 0], [width, height]])
        return ret

    # Managed attributes
    bottom = property(_get_bottom)
    left = property(_get_left)
    min_spine_bbox = property(_get_min_spine_bbox)
    right = property(_get_right)
    spine_bbox = property(_get_spine_bbox)
    top = property(_get_top)
    xaxis_bottom = property(_get_xaxis_bottom)
    xaxis_left = property(_get_xaxis_left)
    xaxis_right = property(_get_xaxis_right)
    xaxis_top = property(_get_xaxis_top)
    xlabel = property(_get_xlabel)
    xlabel_bbox = property(_get_xlabel_bbox)
    xlabel_plus_pad = property(_get_xlabel_plus_pad)
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
    Define a panel within a figure.

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

    # pylint: disable=W0102
    def __init__(
        self,
        series=None,
        primary_axis_label="",
        primary_axis_units="",
        primary_axis_ticks=None,
        secondary_axis_label="",
        secondary_axis_units="",
        secondary_axis_ticks=None,
        log_dep_axis=False,
        legend_props=None,
        display_indep_axis=False,
    ):  # noqa
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
        self._legend_props = {"pos": "BEST", "cols": 1}
        self._display_indep_axis = None
        self._left = None
        self._bottom = None
        self._right = None
        self._top = None
        self._min_spine_bbox = None
        self._min_bbox = None
        self._panel_bbox = None
        self._left_overhang = None
        self._right_overhang = None
        self._indep_label_width = None
        self._prim_xlabel_plus_pad = None
        self._sec_xlabel_plus_pad = None
        self._prim_yaxis_annot = None
        self._sec_yaxis_annot = None
        self._legend_width = None
        self._legend_height = None
        # Private attributes
        self._legend_pos_list = [
            "best",
            "upper right",
            "upper left",
            "lower left",
            "lower right",
            "right",
            "center left",
            "center right",
            "lower center",
            "upper center",
            "center",
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
        self._legend_props_list = ["pos", "cols"]
        self._legend_props_pos_list = [
            "BEST",
            "UPPER RIGHT",
            "UPPER LEFT",
            "LOWER LEFT",
            "LOWER RIGHT",
            "RIGHT",
            "CENTER LEFT",
            "CENTER RIGHT",
            "LOWER CENTER",
            "UPPER CENTER",
            "CENTER",
        ]
        # Exceptions definition
        invalid_prim_ex = pexdoc.exh.addai("primary_axis_ticks")
        invalid_sec_ex = pexdoc.exh.addai("secondary_axis_ticks")
        invalid_prim_ex(
            (primary_axis_ticks is not None)
            and (
                (not isinstance(primary_axis_ticks, list))
                and (not isinstance(primary_axis_ticks, np.ndarray))
            )
        )
        invalid_sec_ex(
            (secondary_axis_ticks is not None)
            and (
                (not isinstance(secondary_axis_ticks, list))
                and (not isinstance(secondary_axis_ticks, np.ndarray))
            )
        )
        # Assignment of arguments to attributes
        # Order here is important to avoid unnecessary re-calculating of
        # panel axes if log_dep_axis is True
        self._set_log_dep_axis(log_dep_axis)
        self._primary_axis_ticks = primary_axis_ticks if not self.log_dep_axis else None
        self._secondary_axis_ticks = (
            secondary_axis_ticks if not self.log_dep_axis else None
        )
        self._set_series(series)
        self._set_primary_axis_label(primary_axis_label)
        self._set_primary_axis_units(primary_axis_units)
        self._set_secondary_axis_label(secondary_axis_label)
        self._set_secondary_axis_units(secondary_axis_units)
        self._set_legend_props(legend_props)
        self._set_display_indep_axis(display_indep_axis)

    def __bool__(self):  # pragma: no cover
        """
        Test if the panel has at least a series associated with it.

        .. note:: This method applies to Python 3.x
        """
        return self._series is not None

    def __iter__(self):
        """
        Return an iterator over the series object(s) in the panel.

        For example:

        .. =[=cog
        .. import pmisc.incfile
        .. pmisc.incfile('plot_example_6.py', cog.out)
        .. =]=
        .. code-block:: python

            # plot_example_6.py
            from __future__ import print_function
            import numpy as np
            import pplot

            def panel_iterator_example(no_print):
                source1 = pplot.BasicSource(
                    indep_var=np.array([1, 2, 3, 4]),
                    dep_var=np.array([1, -10, 10, 5])
                )
                source2 = pplot.BasicSource(
                    indep_var=np.array([100, 200, 300, 400]),
                    dep_var=np.array([50, 75, 100, 125])
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
        Test if the panel has at least a series associated with it.

        .. note:: This method applies to Python 2.x
        """
        return self._series is not None

    def _get_series(self):
        return self._series

    def _set_series(self, series):
        # pylint: disable=C0103
        self._series = (
            (series if isinstance(series, list) else [series])
            if series is not None
            else series
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
            comp_prim_dep_var = (not self.log_dep_axis) and self._has_prim_axis
            comp_sec_dep_var = (not self.log_dep_axis) and self._has_sec_axis
            panel_has_primary_interp_series = any(
                [
                    (not series_obj.secondary_axis)
                    and (series_obj.interp_dep_var is not None)
                    for series_obj in self.series
                ]
            )
            panel_has_secondary_interp_series = any(
                [
                    series_obj.secondary_axis
                    and (series_obj.interp_dep_var is not None)
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
                if comp_prim_dep_var
                else None
            )
            prim_interp_min = (
                min(
                    [
                        min(series_obj.dep_var)
                        for series_obj in self.series
                        if (
                            (not series_obj.secondary_axis)
                            and (series_obj.interp_dep_var is not None)
                        )
                    ]
                )
                if panel_has_primary_interp_series
                else None
            )
            prim_interp_max = (
                max(
                    [
                        max(series_obj.dep_var)
                        for series_obj in self.series
                        if (
                            (not series_obj.secondary_axis)
                            and (series_obj.interp_dep_var is not None)
                        )
                    ]
                )
                if panel_has_primary_interp_series
                else None
            )
            primary_min = (
                min(min(glob_prim_dep_var), prim_interp_min)
                if comp_prim_dep_var and (prim_interp_min is not None)
                else (min(glob_prim_dep_var) if comp_prim_dep_var else None)
            )
            primary_max = (
                max(max(glob_prim_dep_var), prim_interp_max)
                if comp_prim_dep_var and (prim_interp_min is not None)
                else (max(glob_prim_dep_var) if comp_prim_dep_var else None)
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
                if comp_sec_dep_var
                else None
            )
            sec_interp_min = (
                min(
                    [
                        min(series_obj.dep_var)
                        for series_obj in self.series
                        if (
                            series_obj.secondary_axis
                            and (series_obj.interp_dep_var is not None)
                        )
                    ]
                ).tolist()
                if panel_has_secondary_interp_series
                else None
            )
            sec_interp_max = (
                max(
                    [
                        max(series_obj.dep_var)
                        for series_obj in self.series
                        if (
                            series_obj.secondary_axis
                            and (series_obj.interp_dep_var is not None)
                        )
                    ]
                ).tolist()
                if panel_has_secondary_interp_series
                else None
            )
            secondary_min = (
                min(min(glob_sec_dep_var), sec_interp_min)
                if comp_sec_dep_var and (sec_interp_min is not None)
                else (min(glob_sec_dep_var) if comp_sec_dep_var else None)
            )
            secondary_max = (
                max(max(glob_sec_dep_var), sec_interp_max)
                if comp_sec_dep_var and (sec_interp_max is not None)
                else (max(glob_sec_dep_var) if comp_sec_dep_var else None)
            )
            # Global (for logarithmic dependent axis)
            glob_panel_dep_var = (
                None
                if not self.log_dep_axis
                else np.unique(
                    np.concatenate([series_obj.dep_var for series_obj in self.series])
                )
            )
            panel_min = (
                min(min(glob_panel_dep_var), prim_interp_min)
                if self.log_dep_axis and panel_has_primary_interp_series
                else (min(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            panel_max = (
                max(max(glob_panel_dep_var), prim_interp_max)
                if self.log_dep_axis and panel_has_primary_interp_series
                else (max(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            panel_min = (
                min(min(glob_panel_dep_var), sec_interp_min)
                if self.log_dep_axis and panel_has_secondary_interp_series
                else (min(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            panel_max = (
                max(max(glob_panel_dep_var), sec_interp_max)
                if self.log_dep_axis and panel_has_secondary_interp_series
                else (max(glob_panel_dep_var) if self.log_dep_axis else None)
            )
            # Get axis tick marks locations
            if comp_prim_dep_var:
                (
                    self._primary_dep_var_locs,
                    self._primary_dep_var_labels,
                    self._primary_dep_var_min,
                    self._primary_dep_var_max,
                    self._primary_dep_var_div,
                    self._primary_dep_var_unit_scale,
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
                    self._secondary_dep_var_unit_scale,
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
                    self._primary_dep_var_unit_scale,
                ) = _intelligent_ticks(
                    glob_panel_dep_var,
                    panel_min,
                    panel_max,
                    tight=False,
                    log_axis=self.log_dep_axis,
                )
            if self.log_dep_axis and self._has_sec_axis:
                (
                    self._secondary_dep_var_locs,
                    self._secondary_dep_var_labels,
                    self._secondary_dep_var_min,
                    self._secondary_dep_var_max,
                    self._secondary_dep_var_div,
                    self._secondary_dep_var_unit_scale,
                ) = _intelligent_ticks(
                    glob_panel_dep_var,
                    panel_min,
                    panel_max,
                    tight=False,
                    log_axis=self.log_dep_axis,
                )
            # Equalize number of ticks on primary and secondary axis so that
            # ticks are in the same percentage place within the dependent
            # variable plotting interval (for non-logarithmic panels)
            # If there is any tick override (primary and/or secondary) this
            # is not done, the user assumes responsibility for aesthetics of
            # final result
            if (
                (not self.log_dep_axis)
                and self._has_prim_axis
                and self._has_sec_axis
                and (self._primary_axis_ticks is None)
                and (self._secondary_axis_ticks is None)
            ):
                max_ticks = (
                    max(
                        len(self._primary_dep_var_locs),
                        len(self._secondary_dep_var_locs),
                    )
                    - 1
                )
                primary_delta = (
                    self._primary_dep_var_locs[-1] - self._primary_dep_var_locs[0]
                ) / float(max_ticks)
                secondary_delta = (
                    self._secondary_dep_var_locs[-1] - self._secondary_dep_var_locs[0]
                ) / float(max_ticks)
                self._primary_dep_var_locs = [
                    self._primary_dep_var_locs[0] + (num * primary_delta)
                    for num in range(max_ticks + 1)
                ]
                self._secondary_dep_var_locs = [
                    self._secondary_dep_var_locs[0] + (num * secondary_delta)
                    for num in range(max_ticks + 1)
                ]
                (
                    self._primary_dep_var_locs,
                    self._primary_dep_var_labels,
                ) = _uniquify_tick_labels(
                    self._primary_dep_var_locs,
                    self._primary_dep_var_locs[0],
                    self._primary_dep_var_locs[-1],
                )
                (
                    self._secondary_dep_var_locs,
                    self._secondary_dep_var_labels,
                ) = _uniquify_tick_labels(
                    self._secondary_dep_var_locs,
                    self._secondary_dep_var_locs[0],
                    self._secondary_dep_var_locs[-1],
                )
            self._primary_axis_ticks = self._primary_dep_var_locs
            self._secondary_axis_ticks = self._secondary_dep_var_locs
            # Scale panel
            self._scale_dep_var(self._primary_dep_var_div, self._secondary_dep_var_div)

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

    @pexdoc.pcontracts.contract(primary_axis_label="None|str")
    def _set_primary_axis_label(self, primary_axis_label):
        self._primary_axis_label = primary_axis_label

    def _get_primary_axis_units(self):
        return self._primary_axis_units

    @pexdoc.pcontracts.contract(primary_axis_units="None|str")
    def _set_primary_axis_units(self, primary_axis_units):
        self._primary_axis_units = primary_axis_units

    def _get_secondary_axis_label(self):
        return self._secondary_axis_label

    @pexdoc.pcontracts.contract(secondary_axis_label="None|str")
    def _set_secondary_axis_label(self, secondary_axis_label):
        self._secondary_axis_label = secondary_axis_label

    def _get_secondary_axis_units(self):
        return self._secondary_axis_units

    @pexdoc.pcontracts.contract(secondary_axis_units="None|str")
    def _set_secondary_axis_units(self, secondary_axis_units):
        self._secondary_axis_units = secondary_axis_units

    def _get_log_dep_axis(self):
        return self._log_dep_axis

    @pexdoc.pcontracts.contract(log_dep_axis="None|bool")
    def _set_log_dep_axis(self, log_dep_axis):
        self._recalculate_series = self.log_dep_axis != log_dep_axis
        self._log_dep_axis = log_dep_axis
        if self._recalculate_series:
            self._set_series(self._series)

    def _get_display_indep_axis(self):
        return self._display_indep_axis

    @pexdoc.pcontracts.contract(display_indep_axis="None|bool")
    def _set_display_indep_axis(self, display_indep_axis):
        self._display_indep_axis = display_indep_axis

    def _get_legend_props(self):
        return self._legend_props

    @pexdoc.pcontracts.contract(legend_props="None|dict")
    def _set_legend_props(self, legend_props):
        invalid_ex = pexdoc.exh.addex(
            ValueError, "Illegal legend property `*[prop_name]*`"
        )
        illegal_ex = pexdoc.exh.addex(
            TypeError,
            "Legend property `pos` is not one of ['BEST', 'UPPER RIGHT', "
            "'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', "
            "'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', "
            "'UPPER CENTER', 'CENTER'] (case insensitive)",
        )
        cols_ex = pexdoc.exh.addex(RuntimeError, "Legend property `cols` is not valid")
        self._legend_props = (
            legend_props if legend_props is not None else {"pos": "BEST", "cols": 1}
        )
        self._legend_props.setdefault("pos", "BEST")
        self._legend_props.setdefault("cols", 1)
        for key, value in self.legend_props.items():
            invalid_ex(key not in self._legend_props_list, _F("prop_name", key))
            illegal_ex(
                (key == "pos") and _legend_position_validation(self.legend_props["pos"])
            )
            cols_ex(
                ((key == "cols") and (not isinstance(value, int)))
                or (
                    (key == "cols") and (isinstance(value, int) is True) and (value < 0)
                )
            )
        self._legend_props["pos"] = self._legend_props["pos"].upper()

    def __str__(self):
        """
        Print panel information.

        For example:

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
        ret = ""
        if (self.series is None) or (len(self.series) == 0):
            ret += "Series: None\n"
        else:
            for num, element in enumerate(self.series):
                ret += "Series {0}:\n".format(num)
                temp = str(element).split("\n")
                temp = [3 * " " + line for line in temp]
                ret += "\n".join(temp)
                ret += "\n"
        ret += "Primary axis label: {0}\n".format(
            self.primary_axis_label
            if self.primary_axis_label not in ["", None]
            else "not specified"
        )
        ret += "Primary axis units: {0}\n".format(
            self.primary_axis_units
            if self.primary_axis_units not in ["", None]
            else "not specified"
        )
        ret += "Secondary axis label: {0}\n".format(
            self.secondary_axis_label
            if self.secondary_axis_label not in ["", None]
            else "not specified"
        )
        ret += "Secondary axis units: {0}\n".format(
            self.secondary_axis_units
            if self.secondary_axis_units not in ["", None]
            else "not specified"
        )
        ret += "Logarithmic dependent axis: {0}\n".format(self.log_dep_axis)
        ret += "Display independent " "axis: {0}\n".format(self.display_indep_axis)
        ret += "Legend properties:\n"
        iobj = enumerate(sorted(list(self.legend_props.items())))
        for num, (key, value) in iobj:
            ret += "   {0}: {1}{2}".format(
                key, value, "\n" if num + 1 < len(self.legend_props) else ""
            )
        return ret

    def _validate_series(self):
        """Verify elements of series list are of the right type and fully specified."""
        invalid_ex = pexdoc.exh.addai("series")
        incomplete_ex = pexdoc.exh.addex(
            RuntimeError, "Series item *[number]* is not fully specified"
        )
        log_ex = pexdoc.exh.addex(
            ValueError,
            "Series item *[number]* cannot be plotted in a logarithmic "
            "axis because it contains negative data points",
        )
        for num, obj in enumerate(self.series):
            invalid_ex(not isinstance(obj, Series))
            incomplete_ex(not obj._complete, _F("number", num))
            log_ex(
                bool((min(obj.dep_var) <= 0) and self.log_dep_axis), _F("number", num)
            )

    def _get_complete(self):
        """Return True if panel is fully specified, otherwise returns False."""
        return (self.series is not None) and (len(self.series) > 0)

    def _scale_indep_var(self, scaling_factor):
        """Scale independent variable of panel series."""
        for series_obj in self.series:
            series_obj._scale_indep_var(scaling_factor)

    def _scale_dep_var(self, primary_scaling_factor, secondary_scaling_factor):
        """Scale dependent variable of panel series."""
        for series_obj in self.series:
            if not series_obj.secondary_axis:
                series_obj._scale_dep_var(primary_scaling_factor)
            else:
                series_obj._scale_dep_var(secondary_scaling_factor)

    def _setup_axis(
        self,
        axis_type,
        axis_obj,
        indep_min,
        indep_max,
        indep_tick_locs,
        indep_tick_labels,
        indep_axis_label,
        indep_axis_units,
        indep_axis_scale,
        draw_label,
    ):
        """Configure dependent axis."""
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
        dep_dict = prim_dict if axis_type == "PRIMARY" else sec_dict
        ylim = [dep_dict["ymin"], dep_dict["ymax"]]
        lsize = AXIS_TICKS_FONT_SIZE
        axis_obj.tick_params(
            axis="x", which="major", labelsize=lsize, zorder=TICK_ZORDER
        )
        axis_obj.tick_params(
            axis="y", which="major", labelsize=lsize, zorder=TICK_ZORDER
        )
        axis_obj.xaxis.set_ticks(indep_tick_locs)
        axis_obj.yaxis.set_ticks(dep_dict["ticks"])
        axis_obj.set_xlim([indep_min, indep_max], emit=True, auto=False)
        axis_obj.set_ylim(ylim, emit=True, auto=False)
        axis_obj.set_axisbelow(True)
        axis_obj.xaxis.set_ticklabels(indep_tick_labels)
        axis_obj.yaxis.set_ticklabels(dep_dict["tick_labels"])
        if draw_label:
            self._draw_label(
                axis_obj.xaxis, indep_axis_label, indep_axis_units, indep_axis_scale
            )
        self._draw_label(
            axis_obj.yaxis,
            dep_dict["axis_label"],
            dep_dict["axis_units"],
            dep_dict["axis_scale"],
        )

    def _draw(self, disp_indep_axis, indep_axis_dict, axis_prim):
        """Draw panel series."""
        # pylint: disable=W0612
        axis_sec = None
        tobjs = None
        if self._has_sec_axis:
            axis_sec = plt.axes(
                axis_prim.get_position(), frameon=not self._has_prim_axis
            )
        zero = lambda x: x if x is not None else 0

        def amin(prim, sec, prop):
            return min(
                getattr(prim, prop) if self._axis_prim else INF,
                getattr(sec, prop) if self._axis_sec else INF,
            )

        def amax(prim, sec, prop):
            return max(
                getattr(prim, prop) if self._axis_prim else -INF,
                getattr(sec, prop) if self._axis_sec else -INF,
            )

        # Grid control
        if self._has_sec_axis:
            axis_prim.xaxis.grid(False)
            axis_prim.yaxis.grid(False)
            axis_prim.set_zorder(axis_sec.get_zorder() + 1)
            axis_prim.patch.set_visible(False)
            axis_sec.xaxis.grid(True, which="both", zorder=GRID_ZORDER)
            axis_sec.yaxis.grid(True, which="both", zorder=GRID_ZORDER)
        else:
            axis_prim.xaxis.grid(True, which="both", zorder=GRID_ZORDER)
            axis_prim.yaxis.grid(True, which="both", zorder=GRID_ZORDER)
        # Place data series in their appropriate axis (primary or secondary)
        # Reverse series list so that first series is drawn on top
        prim_series = [series for series in self.series if not series.secondary_axis]
        sec_series = [series for series in self.series if series.secondary_axis]
        self._draw_series(sec_series, axis_sec, indep_axis_dict)
        self._draw_series(prim_series, axis_prim, indep_axis_dict)
        if self._has_prim_axis:
            self._setup_axis(
                "PRIMARY",
                axis_prim,
                indep_axis_dict["indep_var_min"],
                indep_axis_dict["indep_var_max"],
                indep_axis_dict["indep_var_locs"],
                indep_axis_dict.get("indep_var_labels", None),
                indep_axis_dict["indep_axis_label"],
                indep_axis_dict["indep_axis_units"],
                indep_axis_dict["indep_axis_unit_scale"],
                True,
            )
        if self._has_sec_axis:
            self._setup_axis(
                "SECONDARY",
                axis_sec,
                indep_axis_dict["indep_var_min"],
                indep_axis_dict["indep_var_max"],
                indep_axis_dict["indep_var_locs"],
                indep_axis_dict.get("indep_var_labels", None),
                indep_axis_dict["indep_axis_label"],
                indep_axis_dict["indep_axis_units"],
                indep_axis_dict["indep_axis_unit_scale"],
                not self._has_prim_axis,
            )
            axis_sec.yaxis.set_label_position("right")
            axis_sec.yaxis.set_ticks_position("right")
            if self._has_prim_axis:
                # Get individual label tick boxes to determine minimum spine
                # size before they are turned off
                tobjs = axis_sec.xaxis.get_ticklabels()
                tobjs = [label for label in tobjs if label.get_text().strip()]
                axis_sec.tick_params(
                    axis="x", which="both", length=0, labelbottom=False
                )
        # Delete labels so that they are not counted in sizing computations
        if (not disp_indep_axis) and axis_prim:
            axis_prim.xaxis.set_ticklabels([])
        if (
            disp_indep_axis
            and self._axis_prim
            and self._axis_prim.xticklabels
            and self._axis_sec
            and self._axis_sec.xticklabels
        ):
            axis_prim.xaxis.set_ticklabels([])
        if (not disp_indep_axis) and axis_sec:
            axis_sec.xaxis.set_ticklabels([])
        if (not len(prim_series)) and len(sec_series) and axis_prim:
            axis_prim.yaxis.set_ticklabels([])
        #
        prim_log_axis = len(prim_series) and self.log_dep_axis
        sec_log_axis = len(sec_series) and self.log_dep_axis
        # Print legend
        legend_width = legend_height = 0
        if (len(self.series) > 1) and (len(self.legend_props) > 0):
            _, primary_labels = (
                axis_prim.get_legend_handles_labels()
                if self._has_prim_axis
                else (None, [])
            )
            _, secondary_labels = (
                axis_sec.get_legend_handles_labels()
                if self._has_sec_axis
                else (None, [])
            )
            lprim = len(primary_labels)
            lsec = len(secondary_labels)
            labels = (
                (
                    [r"$\Leftarrow$" + label for label in primary_labels]
                    + [label + r"$\Rightarrow$" for label in secondary_labels]
                )
                if (lprim > 0) and (lsec > 0)
                else primary_labels + secondary_labels
            )
            if any([bool(label) for label in labels]):
                top_axis = axis_prim if self._has_prim_axis else axis_sec
                top_zorder = (
                    max(
                        [
                            axis_prim.get_zorder() if self._has_prim_axis else 0,
                            axis_sec.get_zorder() if self._has_sec_axis else 0,
                            GRID_ZORDER,
                            TICK_ZORDER,
                        ]
                    )
                    + 1
                )
                leg_artist = [
                    series_obj._legend_artist(LEGEND_SCALE)
                    for series_obj in self.series
                    if series_obj._check_series_is_plottable()
                ]
                loc_key = self._legend_pos_list.index(
                    self.legend_props["pos"].lower()
                    if "pos" in self.legend_props
                    else "lower left"
                )
                lobj = top_axis.legend(
                    leg_artist,
                    labels,
                    ncol=(
                        self.legend_props["cols"]
                        if "cols" in self.legend_props
                        else len(labels)
                    ),
                    loc=self._legend_pos_list[loc_key],
                    numpoints=1,
                    fontsize=AXIS_LABEL_FONT_SIZE / LEGEND_SCALE,
                    facecolor="white",
                    framealpha=1.0,
                )
                lobj.set_zorder(top_zorder + 1000)
                ratio = 101.25 / 100.00
                legend_width = ratio * lobj.handlelength
                legend_height = ratio * lobj.handleheight
        # This is necessary because if there is no primary axis but there
        # is a secondary axis, then the independent axis bounding boxes
        # are all stacked up in the same spot
        axis_prim.display_indep_axis = disp_indep_axis
        axis_prim.xaxis.log_axis = indep_axis_dict["log_indep"]
        axis_prim.yaxis.log_axis = prim_log_axis
        if axis_sec:
            axis_sec.xaxis.log_axis = indep_axis_dict["log_indep"]
            axis_sec.yaxis.log_axis = sec_log_axis
            axis_sec.display_indep_axis = False
        self._axis_prim = _Axis(axis_prim, "prim", tobjs) if axis_prim else None
        self._axis_sec = _Axis(axis_sec, "sec", tobjs) if axis_sec else None
        self._left = amin(self._axis_prim, self._axis_sec, "left")
        self._bottom = amin(self._axis_prim, self._axis_sec, "bottom")
        self._right = amax(self._axis_prim, self._axis_sec, "right")
        self._top = amax(self._axis_prim, self._axis_sec, "top")
        spine_min_width = amax(
            self._axis_prim.min_spine_bbox if self._axis_prim else None,
            self._axis_sec.min_spine_bbox if self._axis_sec else None,
            "width",
        )
        spine_min_height = amax(
            self._axis_prim.min_spine_bbox if self._axis_prim else None,
            self._axis_sec.min_spine_bbox if self._axis_sec else None,
            "height",
        )
        self._min_spine_bbox = Bbox([[0, 0], [spine_min_width, spine_min_height]])
        prim_left_overhang = 0
        prim_bottom_overhang = 0
        prim_right_overhang = 0
        prim_top_overhang = 0
        prim_xlabel_plus_pad = 0
        prim_yaxis_annot = 0
        sec_label_plus_pad = 0
        sec_left_overhang = 0
        sec_bottom_overhang = 0
        sec_right_overhang = 0
        sec_top_overhang = 0
        sec_xlabel_plus_pad = 0
        sec_yaxis_annot = 0
        indep_label_width = 0
        dep_label_height = 0
        if self._has_prim_axis:
            prim_left_overhang = zero(self._axis_prim.left_overhang)
            prim_right_overhang = zero(self._axis_prim.right_overhang)
            prim_bottom_overhang = zero(self._axis_prim.bottom_overhang)
            prim_top_overhang = zero(self._axis_prim.top_overhang)
            prim_xlabel_plus_pad = zero(self._axis_prim.xlabel_plus_pad)
            prim_yaxis_annot = zero(
                self._axis_prim.yaxis_right - self._axis_prim.yaxis_left
            )
            indep_label_width = max(
                indep_label_width, self._axis_prim.xlabel_bbox.width
            )
            dep_label_height = max(dep_label_height, self._axis_prim.ylabel_bbox.height)
        if self._has_sec_axis:
            sec_left_overhang = zero(self._axis_sec.left_overhang)
            sec_right_overhang = zero(self._axis_sec.right_overhang)
            sec_bottom_overhang = zero(self._axis_sec.bottom_overhang)
            sec_top_overhang = zero(self._axis_sec.top_overhang)
            sec_xlabel_plus_pad = zero(self._axis_sec.xlabel_plus_pad)
            sec_yaxis_annot = zero(
                self._axis_sec.yaxis_right - self._axis_sec.yaxis_left
            )
            indep_label_width = max(indep_label_width, self._axis_sec.xlabel_bbox.width)
            dep_label_height = max(dep_label_height, self._axis_sec.ylabel_bbox.height)
        left_overhang = max(prim_left_overhang, sec_left_overhang)
        bottom_overhang = max(prim_bottom_overhang, sec_bottom_overhang)
        right_overhang = max(prim_right_overhang, sec_right_overhang)
        top_overhang = max(prim_top_overhang, sec_top_overhang)
        xlabel_plus_pad = max(prim_xlabel_plus_pad, sec_bottom_overhang)
        panel_min_width = (
            left_overhang
            + max(legend_width, self._min_spine_bbox.width)
            + right_overhang
        )
        panel_min_width = max(
            [
                panel_min_width,
                prim_xlabel_plus_pad + indep_label_width + sec_xlabel_plus_pad,
            ]
        )
        panel_min_height = (
            xlabel_plus_pad
            + bottom_overhang
            + max(legend_height, self._min_spine_bbox.height, dep_label_height)
            + top_overhang
        )
        self._legend_width = legend_width
        self._legend_height = legend_height
        self._indep_label_width = indep_label_width
        self._prim_xlabel_plus_pad = prim_xlabel_plus_pad
        self._sec_xlabel_plus_pad = sec_xlabel_plus_pad
        self._prim_yaxis_annot = prim_yaxis_annot
        self._sec_yaxis_annot = sec_yaxis_annot
        self._left_overhang = left_overhang
        self._right_overhang = right_overhang
        self._min_bbox = Bbox([[0, 0], [panel_min_width, panel_min_height]])
        #
        self._panel_bbox = Bbox([[self._left, self._bottom], [self._right, self._top]])
        if (not disp_indep_axis) and axis_prim:
            _turn_off_axis(axis_prim, "x")
        if (
            disp_indep_axis
            and self._axis_prim
            and self._axis_prim.xticklabels
            and self._axis_sec
            and self._axis_sec.xticklabels
        ):
            _turn_off_axis(axis_prim, "x")
        if (not disp_indep_axis) and axis_sec:
            _turn_off_axis(axis_sec, "x")
        if (not len(prim_series)) and len(sec_series) and axis_prim:
            _turn_off_axis(axis_prim, "y")
        if disp_indep_axis and axis_prim:
            _turn_off_minor_labels(axis_prim, "x")
        if disp_indep_axis and axis_sec:
            _turn_off_minor_labels(axis_sec, "x")
        if prim_log_axis:
            _turn_off_minor_labels(axis_prim, "y")
        if sec_log_axis:
            _turn_off_minor_labels(axis_sec, "y")
        zlist = [line.get_zorder() for line in axis_prim.get_lines()]
        zmax = 0 if not zlist else max(zlist)
        if axis_sec:
            zlist = [line.get_zorder() for line in axis_sec.get_lines()]
            zmax = max(zmax, 0 if not zlist else max(zlist))
        spines = ["left", "bottom", "right", "top"]
        for spine in spines:
            axis_prim.spines[spine].set_zorder(zmax + 1)
        if axis_sec:
            for spine in spines:
                axis_sec.spines[spine].set_zorder(zmax + 1)

    def _draw_label(self, axis, axis_label, axis_units, axis_scale):
        # pylint: disable=R0201
        if (axis_label not in [None, ""]) or (axis_units not in [None, ""]):
            axis_label = (axis_label or "").strip()
            unit_scale = (axis_scale or "").strip()
            empty_units = (unit_scale == "") and (axis_units == "")
            units_str = " [{0}{1}]".format(unit_scale, axis_units or "-")
            fdict = dict(fontsize=AXIS_LABEL_FONT_SIZE)
            axis.set_label_text(
                axis_label + ("" if empty_units else units_str), fontdict=fdict
            )

    def _draw_series(self, series_list, axis, indep_axis_dict):
        for series in reversed(series_list):
            series._draw(axis, indep_axis_dict["log_indep"], self.log_dep_axis)

    _complete = property(_get_complete)

    display_indep_axis = property(
        _get_display_indep_axis,
        _set_display_indep_axis,
        doc="Show independent axis flag",
    )
    r"""
    Get or set the independent axis display flag.

    This flag indicates whether the independent axis is displayed (True) or not (False)

    :type: boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.display_indep_axis

    :raises: (when assigned) RuntimeError (Argument \`display_indep_axis\`
     is not valid)

    .. [[[end]]]
    """

    legend_props = property(
        _get_legend_props, _set_legend_props, doc="Panel legend box properties"
    )
    r"""
    Get or set the panel legend box properties.

    This property is a dictionary that has properties (dictionary key) and
    their associated values (dictionary values). Currently supported properties
    are:

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
        doc="Panel logarithmic dependent axis flag",
    )
    r"""
    Get or set the panel logarithmic dependent (primary and/or secondary) axis flag.

    This flag indicates whether the dependent (primary and/or secondary) axis
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
        _get_primary_axis_label, _set_primary_axis_label, doc="Panel primary axis label"
    )
    r"""
    Get or set the panel primary dependent axis label.

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.primary_axis_label

    :raises: (when assigned) RuntimeError (Argument \`primary_axis_label\`
     is not valid)

    .. [[[end]]]
    """

    primary_axis_scale = property(_get_primary_axis_scale, doc="Primary axis scale")
    """
    Get the scale of the panel primary axis.

    :code:`None` is returned if axis has no series associated with it

    :type: float or None
    """

    primary_axis_ticks = property(
        _get_primary_axis_ticks, doc="Primary axis tick locations"
    )
    """
    Get the primary axis (scaled) tick locations.

    :code:`None` is returned if axis has no series associated with it

    :type: list or None
    """

    primary_axis_units = property(
        _get_primary_axis_units, _set_primary_axis_units, doc="Panel primary axis units"
    )
    r"""
    Get or set the panel primary dependent axis units.

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
        doc="Panel secondary axis label",
    )
    r"""
    Get or set the panel secondary dependent axis label.

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.secondary_axis_label

    :raises: (when assigned) RuntimeError (Argument
     \`secondary_axis_label\` is not valid)

    .. [[[end]]]
    """

    secondary_axis_scale = property(
        _get_secondary_axis_scale, doc="Secondary axis scale"
    )
    """
    Get the scale of the panel secondary axis.

    :code:`None` is returned if axis has no series associated with it

    :type: float or None
    """

    secondary_axis_ticks = property(
        _get_secondary_axis_ticks, doc="secondary axis tick locations"
    )
    """
    Get the secondary axis (scaled) tick locations.

    :code:`None` is returned if axis has no series associated with it

    :type:  list or None
     with it
    """

    secondary_axis_units = property(
        _get_secondary_axis_units,
        _set_secondary_axis_units,
        doc="Panel secondary axis units",
    )
    r"""
    Get or set the panel secondary dependent axis units.

    :type: string

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.panel.Panel.secondary_axis_units

    :raises: (when assigned) RuntimeError (Argument
     \`secondary_axis_units\` is not valid)

    .. [[[end]]]
    """

    series = property(_get_series, _set_series, doc="Panel series")
    r"""
    Get or set the panel series.

    :code:`None` is returned if there are no series associated with the panel

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
