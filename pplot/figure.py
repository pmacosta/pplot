"""
Generate presentation-quality plots.

[[[cog
import os, sys
if sys.hexversion < 0x03000000:
    import __builtin__
else:
    import builtins as __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_plot_figure
exobj_plot = trace_ex_plot_figure.trace_module(no_print=True)
]]]
[[[end]]]
"""
# figure.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,R0201,R0205,R0914,R0915,W0105,W0212

# Standard library imports
from __future__ import print_function
import math
import os
import sys
import warnings

# import warnings
# PyPI imports
import PIL

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.transforms import Bbox
import pmisc
import pexdoc.exh
import pexdoc.pcontracts
import peng

# Intra-package imports
from .constants import TITLE_FONT_SIZE
from .panel import Panel
from .functions import _F, _MF, _intelligent_ticks


###
# Global variables
###
INF = sys.float_info.max
SPACER = 0.2  # in inches
PANEL_SEP = 10 * SPACER


###
# Class
###
class Figure(object):
    r"""
    Generate presentation-quality plots.

    :param panels: One or more data panels
    :type  panels: :py:class:`pplot.Panel` *or list of*
                   :py:class:`pplot.Panel` *or None*

    :param indep_var_label: Independent variable label
    :type  indep_var_label: string

    :param indep_var_units: Independent variable units
    :type  indep_var_units: string

    :param indep_axis_tick_labels: Independent axis tick labels. If not None
                                   overrides ticks automatically generated
                                   or as given by the **indep_axis_ticks**
                                   argument (ignored for figures with a
                                   logarithmic independent axis)
    :type  indep_axis_tick_labels: list of strings or None

    :param indep_axis_ticks: Independent axis tick marks. If not None
                             overrides automatically generated tick marks if
                             the axis type is linear. If None automatically
                             generated tick marks are used for the independent
                             axis
    :type  indep_axis_ticks: list, Numpy vector or None

    :param fig_width: Hard copy plot width in inches. If None the width is
                      automatically calculated so that the figure has a 4:3
                      aspect ratio and there is no horizontal overlap between
                      any two text elements in the figure
    :type  fig_width: `PositiveRealNum <https://pexdoc.readthedocs.io/en/
                      stable/ptypes.html#positiverealnum>`_ or None

    :param fig_height: Hard copy plot height in inches. If None the height is
                       automatically calculated so that the figure has a 4:3
                       aspect ratio and there is no vertical overlap between
                       any two text elements in the figure
    :type  fig_height: `PositiveRealNum <https://pexdoc.readthedocs.io/en/
                       stable/ptypes.html#positiverealnum>`_ or None

    :param title: Plot title
    :type  title: string

    :param log_indep_axis: Flag that indicates whether the independent
                           axis is linear (False) or logarithmic (True)
    :type  log_indep_axis: boolean

    :param dpi: Dots per inch to be used while showing or displaying figure
    :type  dpi: positive number

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.__init__

    :raises:
     * RuntimeError (Argument \`dpi\` is not valid)

     * RuntimeError (Argument \`fig_height\` is not valid)

     * RuntimeError (Argument \`fig_width\` is not valid)

     * RuntimeError (Argument \`indep_axis_tick_labels\` is not valid)

     * RuntimeError (Argument \`indep_axis_ticks\` is not valid)

     * RuntimeError (Argument \`indep_var_label\` is not valid)

     * RuntimeError (Argument \`indep_var_units\` is not valid)

     * RuntimeError (Argument \`log_indep_axis\` is not valid)

     * RuntimeError (Argument \`panels\` is not valid)

     * RuntimeError (Argument \`title\` is not valid)

     * RuntimeError (Figure size is too small: minimum width *[min_width]*,
       minimum height *[min_height]*)

     * RuntimeError (Number of tick locations and number of tick labels
       mismatch)

     * TypeError (Panel *[panel_num]* is not fully specified)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """

    # pylint: disable=R0902,R0913
    def __init__(
        self,
        panels=None,
        indep_var_label="",
        indep_var_units="",
        indep_axis_tick_labels=None,
        indep_axis_ticks=None,
        fig_width=None,
        fig_height=None,
        title="",
        log_indep_axis=False,
        dpi=100.0,
    ):  # noqa
        pexdoc.exh.addai(
            "indep_axis_ticks",
            (indep_axis_ticks is not None)
            and (
                (not isinstance(indep_axis_ticks, list))
                and (not isinstance(indep_axis_ticks, np.ndarray))
            ),
        )
        pexdoc.exh.addai(
            "indep_axis_tick_labels",
            (indep_axis_tick_labels is not None)
            and (
                (not isinstance(indep_axis_tick_labels, list))
                or (
                    isinstance(indep_axis_tick_labels, list)
                    and (indep_axis_ticks is not None)
                    and (len(indep_axis_tick_labels) != len(indep_axis_ticks))
                )
            ),
        )
        # Private attributes
        self._need_redraw = False
        self._min_fig_width = None
        self._min_fig_height = None
        self._size_given = False
        # Public attributes
        self._dpi = None
        self._indep_axis_ticks = None
        self._indep_axis_tick_labels = None
        self._fig = None
        self._panels = None
        self._indep_var_label = None
        self._title = None
        self._log_indep_axis = None
        self._fig_width = None
        self._fig_height = None
        self._indep_var_units = None
        self._indep_var_div = None
        self._axes_list = []
        self._scaling_done = False
        self._indep_axis_dict = None
        self._title_obj = None
        # Assignment of arguments to attributes
        self._set_dpi(dpi)
        self._set_indep_var_label(indep_var_label)
        self._set_indep_var_units(indep_var_units)
        self._set_title(title)
        self._set_log_indep_axis(log_indep_axis)
        self._set_indep_axis_ticks(
            indep_axis_ticks if not self.log_indep_axis else None
        )
        self._set_indep_axis_tick_labels(indep_axis_tick_labels)
        self._set_panels(panels)
        self._set_fig_width(fig_width)
        self._set_fig_height(fig_height)

    def __bool__(self):  # pragma: no cover
        """
        Test if the figure has at least a panel associated with it.

        .. note:: This method applies to Python 3.x
        """
        return self._panels is not None

    def __iter__(self):
        r"""
        Return an iterator over the panel object(s) in the figure.

        For example:

        .. =[=cog
        .. import pmisc
        .. pmisc.incfile('plot_example_7.py', cog.out)
        .. =]=
        .. code-block:: python

            # plot_example_7.py
            from __future__ import print_function
            import numpy as np
            import pplot

            def figure_iterator_example(no_print):
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
                panel1 = pplot.Panel(
                    series=series1,
                    primary_axis_label='Average',
                    primary_axis_units='A',
                    display_indep_axis=False
                )
                panel2 = pplot.Panel(
                    series=series2,
                    primary_axis_label='Standard deviation',
                    primary_axis_units=r'$\sqrt{{A}}$',
                    display_indep_axis=True
                )
                figure = pplot.Figure(
                    panels=[panel1, panel2],
                    indep_var_label='Time',
                    indep_var_units='sec',
                    title='Sample Figure'
                )
                if not no_print:
                    for num, panel in enumerate(figure):
                        print('Panel {0}:'.format(num+1))
                        print(panel)
                        print('')
                else:
                    return figure

        .. =[=end=]=

        .. code-block:: python

            >>> import docs.support.plot_example_7 as mod
            >>> mod.figure_iterator_example(False)
            Panel 1:
            Series 0:
               Independent variable: [ 1.0, 2.0, 3.0, 4.0 ]
               Dependent variable: [ 1.0, -10.0, 10.0, 5.0 ]
               Label: Goals
               Color: k
               Marker: o
               Interpolation: CUBIC
               Line style: -
               Secondary axis: False
            Primary axis label: Average
            Primary axis units: A
            Secondary axis label: not specified
            Secondary axis units: not specified
            Logarithmic dependent axis: False
            Display independent axis: False
            Legend properties:
               cols: 1
               pos: BEST
            <BLANKLINE>
            Panel 2:
            Series 0:
               Independent variable: [ 100.0, 200.0, 300.0, 400.0 ]
               Dependent variable: [ 50.0, 75.0, 100.0, 125.0 ]
               Label: Saves
               Color: b
               Marker: None
               Interpolation: STRAIGHT
               Line style: --
               Secondary axis: False
            Primary axis label: Standard deviation
            Primary axis units: $\sqrt{{A}}$
            Secondary axis label: not specified
            Secondary axis units: not specified
            Logarithmic dependent axis: False
            Display independent axis: True
            Legend properties:
               cols: 1
               pos: BEST
            <BLANKLINE>

        .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
        .. [[[end]]]
        """
        return iter(self._panels)

    def __nonzero__(self):  # pragma: no cover
        """
        Test if the figure has at least a panel associated with it.

        .. note:: This method applies to Python 2.x
        """
        return self._panels is not None

    def __str__(self):
        r"""
        Print figure information.

        For example:

            >>> from __future__ import print_function
            >>> import docs.support.plot_example_7 as mod
            >>> print(mod.figure_iterator_example(True))    #doctest: +ELLIPSIS
            Panel 0:
               Series 0:
                  Independent variable: [ 1.0, 2.0, 3.0, 4.0 ]
                  Dependent variable: [ 1.0, -10.0, 10.0, 5.0 ]
                  Label: Goals
                  Color: k
                  Marker: o
                  Interpolation: CUBIC
                  Line style: -
                  Secondary axis: False
               Primary axis label: Average
               Primary axis units: A
               Secondary axis label: not specified
               Secondary axis units: not specified
               Logarithmic dependent axis: False
               Display independent axis: False
               Legend properties:
                  cols: 1
                  pos: BEST
            Panel 1:
               Series 0:
                  Independent variable: [ 100.0, 200.0, 300.0, 400.0 ]
                  Dependent variable: [ 50.0, 75.0, 100.0, 125.0 ]
                  Label: Saves
                  Color: b
                  Marker: None
                  Interpolation: STRAIGHT
                  Line style: --
                  Secondary axis: False
               Primary axis label: Standard deviation
               Primary axis units: $\sqrt{{A}}$
               Secondary axis label: not specified
               Secondary axis units: not specified
               Logarithmic dependent axis: False
               Display independent axis: True
               Legend properties:
                  cols: 1
                  pos: BEST
            Independent variable label: Time
            Independent variable units: sec
            Logarithmic independent axis: False
            Title: Sample Figure
            Figure width: ...
            Figure height: ...
            <BLANKLINE>
        """
        # pylint: disable=C1801
        self._create_figure()
        fig_width, fig_height = self._fig_dims()
        ret = ""
        if (self.panels is None) or (len(self.panels) == 0):
            ret += "Panels: None\n"
        else:
            for num, element in enumerate(self.panels):
                ret += "Panel {0}:\n".format(num)
                temp = str(element).split("\n")
                temp = [3 * " " + line for line in temp]
                ret += "\n".join(temp)
                ret += "\n"
        ret += "Independent variable label: {0}\n".format(
            self.indep_var_label
            if self.indep_var_label not in ["", None]
            else "not specified"
        )
        ret += "Independent variable units: {0}\n".format(
            self.indep_var_units
            if self.indep_var_units not in ["", None]
            else "not specified"
        )
        ret += "Logarithmic independent axis: {0}\n".format(self.log_indep_axis)
        ret += "Title: {0}\n".format(
            self.title if self.title not in ["", None] else "not specified"
        )
        ret += "Figure width: {0}\n".format(fig_width)
        ret += "Figure height: {0}\n".format(fig_height)
        return ret

    def _bbox(self, obj):
        """Return bounding box of an object."""
        renderer = self._fig.canvas.get_renderer()
        return obj.get_window_extent(renderer=renderer).transformed(
            self._fig.dpi_scale_trans.inverted()
        )

    def _calculate_min_figure_size(self):
        """Calculate minimum panel and figure size."""
        dround = lambda x: math.floor(x) / self.dpi
        title_width = 0
        if self.title not in [None, ""]:
            title_bbox = self._bbox(self._title_obj)
            title_width = title_bbox.width
        min_width = max(
            [
                (
                    max(panel._left_overhang for panel in self.panels)
                    + max(
                        max(panel._min_spine_bbox.width, panel._legend_width)
                        for panel in self.panels
                    )
                    + max(panel._right_overhang for panel in self.panels)
                ),
                max(
                    panel._prim_yaxis_annot
                    + panel._indep_label_width
                    + panel._sec_yaxis_annot
                    for panel in self.panels
                ),
                title_width,
            ]
        )
        self._min_fig_width = dround(min_width * self.dpi)
        npanels = len(self.panels)
        self._min_fig_height = dround(
            npanels * max([panel._min_bbox.height * self.dpi for panel in self.panels])
            + ((npanels - 1) * PANEL_SEP)
        )

    def _check_figure_spec(self, fig_width=None, fig_height=None):
        """Validate given figure size against minimum dimension."""
        small_ex = pexdoc.exh.addex(
            RuntimeError,
            "Figure size is too small: minimum width *[min_width]*, "
            "minimum height *[min_height]*",
        )
        small_ex(
            bool(
                (fig_width and (fig_width < self._min_fig_width))
                or (fig_height and (fig_height < self._min_fig_height))
            ),
            [
                _F("min_width", self._min_fig_width),
                _F("min_height", self._min_fig_height),
            ],
        )

    def _create_figure(self, raise_exception=False):
        """Create and resize figure."""
        if raise_exception:
            specified_ex = pexdoc.exh.addex(
                RuntimeError, "Figure object is not fully specified"
            )
            specified_ex(raise_exception and (not self._complete))
        if not self._complete:
            return Bbox([[0, 0], [0, 0]])
        if self._need_redraw:
            self._size_given = (self._fig_width is not None) and (
                self._fig_height is not None
            )
            # First _draw call is to calculate approximate figure size, (until
            # matplotlib actually draws the figure, all the bounding boxes of
            # the elements in the figure are null boxes. The second _draw call
            # is to draw figure with either the calculated minimum dimensions
            # or the user-given dimensions, provided they are equal or greater
            # than the minimum dimensions
            self._draw()
            if not self._size_given:
                self._draw()
            bbox = self._fig_bbox()
            fig_width, fig_height = self._fig_dims()
            self._fig.set_size_inches(fig_width, fig_height, forward=True)
            self._need_redraw = False
            # From https://github.com/matplotlib/matplotlib/issues/7984:
            # When the Figure is drawn, its Axes are sorted based on zorder
            # with a stable sort, and then drawn in that order. Then within
            # each Axes, artists are sorted based on zorder. Therefore you
            # can't interleave the drawing orders of artists from one Axes with
            # those from another.
        else:
            bbox = self._fig_bbox()
        fig_width, fig_height = self._fig_dims()
        # Get figure pixel size exact
        width = int(round(fig_width * self._dpi))
        lwidth = int(round(width / 2.0))
        rwidth = width - lwidth
        height = int(round(fig_height * self._dpi))
        bheight = int(round(height / 2.0))
        theight = height - bheight
        bbox_xcenter = bbox.xmin + 0.5 * bbox.width
        bbox_ycenter = bbox.ymin + 0.5 * bbox.height
        bbox = Bbox(
            [
                [
                    bbox_xcenter - (lwidth / self._dpi),
                    bbox_ycenter - (bheight / self._dpi),
                ],
                [
                    bbox_xcenter + (rwidth / self._dpi),
                    bbox_ycenter + (theight / self._dpi),
                ],
            ]
        )
        return bbox

    def _draw(self):
        # pylint: disable=C0326,W0612
        num_panels = len(self.panels)
        if not self._scaling_done:
            # Find union of the independent variable data set of all panels
            indep_axis_ticks = self._get_global_xaxis()
            self._indep_var_div = indep_axis_ticks.div
            self._indep_axis_ticks = indep_axis_ticks.locs
            # Scale all panel series
            for panel_obj in self.panels:
                panel_obj._scale_indep_var(self._indep_var_div)
            self._indep_axis_tick_labels = (
                self._indep_axis_tick_labels or indep_axis_ticks.labels
            )
            self._indep_axis_dict = {
                "log_indep": self.log_indep_axis,
                "indep_var_min": indep_axis_ticks.min,
                "indep_var_max": indep_axis_ticks.max,
                "indep_var_locs": indep_axis_ticks.locs,
                "indep_var_labels": self._indep_axis_tick_labels,
                "indep_axis_label": self.indep_var_label,
                "indep_axis_units": self.indep_var_units,
                "indep_axis_unit_scale": indep_axis_ticks.unit_scale,
            }
            self._scaling_done = True
        # Create required number of panels
        self._draw_panels()
        # Draw figure otherwise some bounding boxes return NaN
        FigureCanvasAgg(self._fig).draw()
        self._calculate_min_figure_size()

    def _draw_panels(self, fbbox=None):
        def init_figure(num_panels, fbbox=None):
            fig_width, fig_height = self._fig_dims()
            figsize = (fig_width, fig_height) if fig_width and fig_height else None
            plt.close("all")
            self._fig, axesh = plt.subplots(
                nrows=num_panels, ncols=1, dpi=self.dpi, figsize=figsize
            )
            plt.tight_layout(pad=0, h_pad=2, rect=fbbox)
            axesh = [axesh] if num_panels == 1 else axesh
            if self.title not in ["", None]:
                self._title_obj = self._fig.suptitle(
                    self.title,
                    fontsize=TITLE_FONT_SIZE,
                    horizontalalignment="center",
                    verticalalignment="top",
                    multialignment="center",
                    y=1.0,
                )
            return axesh, fig_width, fig_height

        num_panels = len(self.panels)
        axesh, fig_width, fig_height = init_figure(num_panels, fbbox)
        self._axes_list = []
        top = right = -INF
        bottom = left = +INF
        if all(not panel.display_indep_axis for panel in self.panels):
            self.panels[-1]._display_indep_axis = True
        for panel, axish in zip(self.panels, axesh):
            disp_indep_axis = (num_panels == 1) or panel.display_indep_axis
            panel._draw(disp_indep_axis, self._indep_axis_dict, axish)
            left = min(left, panel._panel_bbox.xmin)
            bottom = min(bottom, panel._panel_bbox.ymin)
            right = max(right, panel._panel_bbox.xmax)
            top = max(top, panel._panel_bbox.ymax)
        if self._title_obj:
            title_bbox = self._bbox(self._title_obj)
            left = min(title_bbox.xmin, left)
            right = max(title_bbox.xmax, right)
        if fig_width and fig_height:
            xdelta_left = -left / fig_width
            ydelta_bot = -bottom / fig_height
            xdelta_right = 1 - ((right - fig_width) / fig_width)
            ydelta_top = (
                title_bbox.ymin / top
                if self._title_obj
                else 1 - ((top - fig_height) / fig_height)
            )
            fbbox = [xdelta_left, ydelta_bot, xdelta_right, ydelta_top]
            axesh, _, _ = init_figure(num_panels, fbbox)
            for panel, axish in zip(self.panels, axesh):
                disp_indep_axis = (num_panels == 1) or panel.display_indep_axis
                panel._draw(disp_indep_axis, self._indep_axis_dict, axish)

    def _fig_bbox(self):
        """Return bounding box of figure."""
        tleft = tbottom = +INF
        tright = ttop = -INF
        if self._title_obj:
            title_bbox = self._bbox(self._title_obj)
            tleft = title_bbox.xmin
            tright = title_bbox.xmax
            ttop = title_bbox.ymax
            tbottom = title_bbox.ymin
        left = min(tleft, min(pobj._left for pobj in self.panels))
        bottom = min(tbottom, min(pobj._bottom for pobj in self.panels))
        top = max(ttop, max(pobj._top for pobj in self.panels))
        right = max(tright, max(pobj._right for pobj in self.panels))
        fig_bbox = Bbox([[left, bottom], [right, top]])
        return fig_bbox

    def _fig_dims(self):
        """Get actual figure size, given or minimum calculated."""
        fig_width = self._fig_width or self._min_fig_width
        fig_height = self._fig_height or self._min_fig_height
        return fig_width, fig_height

    def _get_axes_list(self):
        self._create_figure()
        return self._axes_list

    def _get_complete(self):
        """Return True if figure is fully specified, otherwise returns False."""
        return (self.panels is not None) and len(self.panels)

    def _get_dpi(self):
        return self._dpi

    def _get_fig(self):
        self._create_figure()
        return self._fig

    def _get_fig_height(self):
        if self._complete and (self._fig_height is None):
            self._create_figure()
            self._fig_height = self._min_fig_height
        return self._fig_height

    def _get_fig_width(self):
        if self._complete and (self._fig_width is None):
            self._create_figure()
            self._fig_width = self._min_fig_width
        return self._fig_width

    def _get_global_xaxis(self):
        log_ex = pexdoc.exh.addex(
            ValueError,
            "Figure cannot be plotted with a logarithmic "
            "independent axis because panel *[panel_num]*, series "
            "*[series_num]* contains negative independent data points",
        )
        ticks_num_ex = pexdoc.exh.addex(
            RuntimeError, "Number of tick locations and number of tick labels mismatch"
        )
        glob_indep_var = []
        for panel_num, panel_obj in enumerate(self.panels):
            for series_num, series_obj in enumerate(panel_obj.series):
                log_ex(
                    bool(self.log_indep_axis and (min(series_obj.indep_var) < 0)),
                    edata=_MF("panel_num", panel_num, "series_num", series_num),
                )
                glob_indep_var = np.unique(
                    np.append(
                        glob_indep_var,
                        np.array(
                            [
                                peng.round_mantissa(element, 10)
                                for element in series_obj.indep_var
                            ]
                        ),
                    )
                )
        indep_axis_ticks = _intelligent_ticks(
            glob_indep_var,
            min(glob_indep_var),
            max(glob_indep_var),
            tight=True,
            log_axis=self.log_indep_axis,
            tick_list=(None if self._log_indep_axis else self._indep_axis_ticks),
        )
        ticks_num_ex(
            (self._indep_axis_tick_labels is not None)
            and (len(self._indep_axis_tick_labels) != len(indep_axis_ticks.labels))
        )
        return indep_axis_ticks

    def _get_indep_axis_scale(self):
        self._create_figure()
        return self._indep_var_div

    def _get_indep_axis_ticks(self):
        self._create_figure()
        return self._indep_axis_ticks

    def _get_indep_axis_tick_labels(self):
        self._create_figure()
        return self._indep_axis_tick_labels

    def _get_indep_var_label(self):
        return self._indep_var_label

    def _get_indep_var_units(self):
        return self._indep_var_units

    def _get_log_indep_axis(self):
        return self._log_indep_axis

    def _get_panels(self):
        return self._panels

    def _get_title(self):
        return self._title

    @pexdoc.pcontracts.contract(dpi="None|positive_real_num")
    def _set_dpi(self, dpi):
        self._dpi = float(dpi)

    @pexdoc.pcontracts.contract(fig_height="None|positive_real_num")
    def _set_fig_height(self, fig_height):
        if self._complete:
            self._create_figure()
            self._check_figure_spec(self.fig_width, fig_height)
        self._fig_height = fig_height
        self._need_redraw = True

    @pexdoc.pcontracts.contract(fig_width="None|positive_real_num")
    def _set_fig_width(self, fig_width):
        if self._complete:
            self._create_figure()
            self._check_figure_spec(fig_width, self.fig_height)
        self._fig_width = fig_width
        self._need_redraw = True

    @pexdoc.pcontracts.contract(indep_axis_ticks="None|increasing_real_numpy_vector")
    def _set_indep_axis_ticks(self, indep_axis_ticks):
        self._indep_axis_ticks = indep_axis_ticks
        self._need_redraw = True

    @pexdoc.pcontracts.contract(indep_axis_tick_labels="None|list(str)")
    def _set_indep_axis_tick_labels(self, indep_axis_tick_labels):
        if not self._log_indep_axis:
            self._indep_axis_tick_labels = indep_axis_tick_labels
            self._need_redraw = True
            self._create_figure()

    @pexdoc.pcontracts.contract(indep_var_label="None|str")
    def _set_indep_var_label(self, indep_var_label):
        self._indep_var_label = indep_var_label
        self._need_redraw = True

    @pexdoc.pcontracts.contract(indep_var_units="None|str")
    def _set_indep_var_units(self, indep_var_units):
        self._indep_var_units = indep_var_units
        self._need_redraw = True

    @pexdoc.pcontracts.contract(log_indep_axis="None|bool")
    def _set_log_indep_axis(self, log_indep_axis):
        self._log_indep_axis = log_indep_axis
        self._need_redraw = True

    @pexdoc.pcontracts.contract(title="None|str")
    def _set_title(self, title):
        self._title = title
        self._need_redraw = True

    def _set_panels(self, panels):
        self._panels = (
            (panels if isinstance(panels, list) else [panels])
            if panels is not None
            else panels
        )
        if self.panels is not None:
            self._validate_panels()
        self._need_redraw = True

    def _validate_panels(self):
        """Verify elements of panel list are of the right type and fully specified."""
        invalid_ex = pexdoc.exh.addai("panels")
        specified_ex = pexdoc.exh.addex(
            TypeError, "Panel *[panel_num]* is not fully specified"
        )
        for num, obj in enumerate(self.panels):
            invalid_ex(not isinstance(obj, Panel))
            specified_ex(not obj._complete, _F("panel_num", num))

    @pexdoc.pcontracts.contract(fname="file_name", ftype="None|str", compress=bool)
    def save(self, fname, ftype=None, compress=True):
        r"""
        Save the figure to a file.

        :param fname: File name
        :type  fname: `FileName <https://pexdoc.readthedocs.io/en/stable/
                      ptypes.html#filename>`_

        :param ftype: File type, either 'PNG' or 'EPS' (case insensitive). The
                      PNG format is a `raster
                      <https://en.wikipedia.org/wiki/Raster_graphics>`_ format
                      while the EPS format is a
                      `vector <https://en.wikipedia.org/wiki/
                      Vector_graphics>`_ format
        :type  ftype: string

        :param compress: Flag that indicates whether the file saved is to be
                         compressed (True) or not (False). Only relevant for
                         PNG file type
        :type  compress: boolean

        .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. pplot.figure.Figure.save

        :raises:
         * RuntimeError (Argument \`compress\` is not valid)

         * RuntimeError (Argument \`fname\` is not valid)

         * RuntimeError (Argument \`ftype\` is not valid)

         * RuntimeError (Could not determine file type)

         * RuntimeError (Figure object is not fully specified)

         * RuntimeError (Incongruent file type and file extension)

         * RuntimeError (Number of tick locations and number of tick labels
           mismatch)

         * RuntimeError (Unsupported file type: *[file_type]*)

         * ValueError (Figure cannot be plotted with a logarithmic independent
           axis because panel *[panel_num]*, series *[series_num]* contains
           negative independent data points)

        .. [[[end]]]
        """
        unsupported_ex = pexdoc.exh.addex(
            RuntimeError, "Unsupported file type: *[file_type]*"
        )
        no_ftype_ex = pexdoc.exh.addex(RuntimeError, "Could not determine file type")
        incongruent_ftype = pexdoc.exh.addex(
            RuntimeError, "Incongruent file type and file extension"
        )
        sup_ftypes = ["png", "eps", "pdf"]
        unsupported_ex(
            bool((ftype is not None) and (ftype.lower() not in sup_ftypes)),
            _F("file_type", ftype),
        )
        basename, extension = os.path.splitext(fname)
        extension = extension.lstrip(".")
        no_ftype_ex(bool((ftype is None) and (extension.lower() not in sup_ftypes)))
        incongruent_ftype(
            bool(
                (ftype is not None)
                and extension
                and (ftype.upper() != extension.upper())
            )
        )
        ftype = (ftype or extension).upper()
        extension = extension or ftype.lower()
        fname = "{0}.{1}".format(basename, extension)
        bbox = self._create_figure(raise_exception=True)
        dpi = self.dpi if ftype == "PNG" else None
        bbox = bbox if ftype == "PNG" else "tight"
        # Matplotlib seems to have a problem with ~/, expand it to $HOME
        fname = os.path.expanduser(fname)
        pmisc.make_dir(fname)
        self._fig_width, self._fig_height = self._fig_dims()
        self._fig.savefig(
            fname,
            dpi=dpi,
            bbox="tight",
            format=ftype,
            bbox_extra_artists=(self._title_obj,),
        )
        plt.close("all")
        if (ftype == "PNG") and compress:
            img = PIL.Image.open(fname)
            # Remove alpha channel
            img = img.convert("RGB")
            # Move to index image if possible (maximum number of colors used
            # has to be less that 256 as the palette is 8 bits)
            # getcolors returns None if the number of colors exceeds the
            # maxcolors argument
            ncolors = img.getcolors(maxcolors=256)
            if ncolors is not None:
                img = img.convert("P", palette=PIL.Image.ADAPTIVE)
            img.save(fname, quality=100, optimize=True)

    def show(self):
        """
        Display the figure.

        .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. pplot.figure.Figure.show

        :raises:
         * RuntimeError (Figure object is not fully specified)

         * RuntimeError (Number of tick locations and number of tick labels
           mismatch)

         * ValueError (Figure cannot be plotted with a logarithmic independent
           axis because panel *[panel_num]*, series *[series_num]* contains
           negative independent data points)

        .. [[[end]]]
        """
        self._create_figure(raise_exception=True)
        self._fig_width, self._fig_height = self._fig_dims()
        plt.show()

    # Managed attributes
    _complete = property(_get_complete)

    axes_list = property(_get_axes_list, doc="Matplotlib figure axes handle list")
    """
    Get Matplotlib figure axes handle list.

    :code:`None` is returned if figure not fully specified.  Useful if
    annotations or further customizations to the panel(s) are needed.  Each
    panel has an entry in the list, which is sorted in the order the panels are
    plotted (top to bottom). Each panel entry is a dictionary containing the
    following key-value pairs:

    * **number** (*integer*) -- panel number, panel 0 is the top-most panel

    * **primary** (*Matplotlib axis object*) -- axis handle for the primary
      axis, None if the figure has not primary axis

    * **secondary** (*Matplotlib axis object*) -- axis handle for the
      secondary axis, None if the figure has no secondary axis

    :type: list

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.axes_list

    :raises: (when retrieved)

     * RuntimeError (Number of tick locations and number of tick labels
       mismatch)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """

    dpi = property(_get_dpi, _set_dpi, doc="Figure dots per inch (DPI)")
    r"""
    Get or set the dots per inch (DPI) of the figure.

    :type: `PositiveRealNum <https://pexdoc.readthedocs.io/en/
           stable/ptypes.html#positiverealnum>`_ or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for pplot.figure.Figure.dpi

    :raises: (when assigned) RuntimeError (Argument \`dpi\` is not valid)

    .. [[[end]]]
    """

    fig = property(_get_fig, doc="Figure handle")
    """
    Get the Matplotlib figure handle.

    Useful if annotations or further customizations to the figure are needed.
    :code:`None` is returned if figure is not fully specified

    :type: Matplotlib figure handle or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for pplot.figure.Figure.fig

    :raises: (when retrieved)

     * RuntimeError (Number of tick locations and number of tick labels
       mismatch)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """

    fig_height = property(
        _get_fig_height, _set_fig_height, doc="height of the hard copy plot"
    )
    r"""
    Get or set the height (in inches) of the hard copy plot.

    :code:`None` is returned if figure is not fully specified.

    :type: `PositiveRealNum <https://pexdoc.readthedocs.io/en/
           stable/ptypes.html#positiverealnum>`_ or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.fig_height

    :raises: (when assigned)

     * RuntimeError (Argument \`fig_height\` is not valid)

     * RuntimeError (Figure size is too small: minimum width *[min_width]*,
       minimum height *[min_height]*)

     * RuntimeError (Number of tick locations and number of tick labels
       mismatch)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """

    fig_width = property(
        _get_fig_width, _set_fig_width, doc="Width of the hard copy plot"
    )
    r"""
    Get or set the width (in inches) of the hard copy plot.

    :code:`None` is returned if figure is not fully specified.

    :type: `PositiveRealNum <https://pexdoc.readthedocs.io/en/
           stable/ptypes.html#positiverealnum>`_ or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.fig_width

    :raises: (when assigned)

     * RuntimeError (Argument \`fig_width\` is not valid)

     * RuntimeError (Figure size is too small: minimum width *[min_width]*,
       minimum height *[min_height]*)

     * RuntimeError (Number of tick locations and number of tick labels
       mismatch)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """

    indep_axis_scale = property(_get_indep_axis_scale, doc="Independent axis scale")
    """
    Get the scale of the figure independent axis.

    :code:`None` is returned if figure is not fully specified.

    :type:  float or None if figure has no panels associated with it

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.indep_axis_scale

    :raises: (when retrieved)

     * RuntimeError (Number of tick locations and number of tick labels
       mismatch)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """

    indep_axis_ticks = property(
        _get_indep_axis_ticks,
        _set_indep_axis_ticks,
        doc="Independent axis tick locations",
    )
    r"""
    Get or set the independent axis (scaled) tick locations.

    :type: list

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.indep_axis_ticks

    :raises:
     * When assigned

       * RuntimeError (Argument \`indep_axis_ticks\` is not valid)

     * When retrieved

       * RuntimeError (Number of tick locations and number of tick labels
         mismatch)

       * ValueError (Figure cannot be plotted with a logarithmic
         independent axis because panel *[panel_num]*, series *[series_num]*
         contains negative independent data points)

    .. [[[end]]]
    """

    indep_axis_tick_labels = property(
        _get_indep_axis_tick_labels,
        _set_indep_axis_tick_labels,
        doc="Independent axis tick labels",
    )
    r"""
    Get or set the independent axis tick labels.

    Labels are ignored for figures with a logarithmic independent axis

    :type: list of strings

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.indep_axis_tick_labels

    :raises:
     * When assigned

       * RuntimeError (Argument \`indep_axis_tick_labels\` is not valid)

       * RuntimeError (Number of tick locations and number of tick labels
         mismatch)

       * ValueError (Figure cannot be plotted with a logarithmic
         independent axis because panel *[panel_num]*, series *[series_num]*
         contains negative independent data points)

     * When retrieved

       * RuntimeError (Number of tick locations and number of tick labels
         mismatch)

       * ValueError (Figure cannot be plotted with a logarithmic
         independent axis because panel *[panel_num]*, series *[series_num]*
         contains negative independent data points)

    .. [[[end]]]
    """

    indep_var_label = property(
        _get_indep_var_label, _set_indep_var_label, doc="Figure independent axis label"
    )
    r"""
    Get or set the figure independent variable label

    :type: string or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.indep_var_label

    :raises: (when assigned) RuntimeError (Argument \`indep_var_label\` is
     not valid)

    .. [[[end]]]
    """

    indep_var_units = property(
        _get_indep_var_units, _set_indep_var_units, doc="Figure independent axis units"
    )
    r"""
    Get or set the figure independent variable units.

    :type: string or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.indep_var_units

    :raises: (when assigned) RuntimeError (Argument \`indep_var_units\` is
     not valid)

    .. [[[end]]]
    """

    log_indep_axis = property(
        _get_log_indep_axis, _set_log_indep_axis, doc="Figure log_indep_axis"
    )
    r"""
    Get or set the figure logarithmic independent axis flag.

    This flag indicates whether the independent axis is linear (False) or
    logarithmic (True)

    :type: boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.log_indep_axis

    :raises: (when assigned) RuntimeError (Argument \`log_indep_axis\` is
     not valid)

    .. [[[end]]]
    """

    panels = property(_get_panels, _set_panels, doc="Figure panel(s)")
    r"""
    Get or set the figure panel(s).

    :code:`None` is returned if no panels have been specified

    :type: :py:class:`pplot.Panel`, list of
           :py:class:`pplot.panel` or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.panels

    :raises: (when assigned)

     * RuntimeError (Argument \`panels\` is not valid)

     * TypeError (Panel *[panel_num]* is not fully specified)

    .. [[[end]]]
    """

    title = property(_get_title, _set_title, doc="Figure title")
    r"""
    Get or set the figure title.

    :type: string or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.title

    :raises: (when assigned) RuntimeError (Argument \`title\` is not
     valid)

    .. [[[end]]]
    """
