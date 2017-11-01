# figure.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,R0201,R0914,R0915,W0105,W0212

# Standard library imports
from __future__ import print_function
from functools import partial
import math
import os
import sys
import warnings
# PyPI imports
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.transforms import Bbox
import pmisc
import pexdoc.exh
import pexdoc.pcontracts
import peng
# Intra-package imports
from .panel import Panel
from .constants import TITLE_FONT_SIZE
from .functions import _F, _MF, _intelligent_ticks


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
import trace_ex_plot_figure
exobj_plot = trace_ex_plot_figure.trace_module(no_print=True)
]]]
[[[end]]]
"""


###
# Global variables
###
INF = sys.float_info.max
SPACER = 0.2 # in inches
PANEL_SEP = 10*SPACER


###
# Functions
###
def _get_text(obj):
    return obj.get_text().strip()


def _lmax(*args):
    return _lmm(max, 0, *args)


def _lmin(*args):
    return _lmm(min, INF, *args)


def _lmm(fpointer, limit, *args):
    ret = [item for item in pmisc.flatten_list(args) if item is not None]
    return fpointer(ret) if ret else limit


###
# Class
###
class Figure(object):
    r"""
    Generates presentation-quality plots

    :param panels: One or more data panels
    :type  panels: :py:class:`pplot.Panel` *or list of*
                   :py:class:`pplot.Panel` *or None*

    :param indep_var_label: Independent variable label
    :type  indep_var_label: string

    :param indep_var_units: Independent variable units
    :type  indep_var_units: string

    :param indep_axis_ticks: Independent axis tick marks. If not None
                             overrides automatically generated tick marks if
                             the axis type is linear. If None automatically
                             generated tick marks are used for the independent
                             axis
    :type  indep_axis_ticks: list, Numpy vector or None

    :param indep_axis_tick_labels: Independent axis tick labels. If not None
                                   overrides ticks automatically generated
                                   or as given by the **indep_axis_ticks**
                                   argument
    :type  indep_axis_tick_labels: list of strings or None

    :param fig_width: Hard copy plot width in inches. If None the width is
                      automatically calculated so that there is no horizontal
                      overlap between any two text elements in the figure
    :type  fig_width: `PositiveRealNum <http://pexdoc.readthedocs.io/en/
                      stable/ptypes.html#positiverealnum>`_ or None

    :param fig_height: Hard copy plot height in inches. If None the height is
                       automatically calculated so that there is no vertical
                       overlap between any two text elements in the figure
    :type  fig_height: `PositiveRealNum <http://pexdoc.readthedocs.io/en/
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

     * RuntimeError (Argument \`indep_axis_ticks\` is not valid)

     * RuntimeError (Argument \`indep_var_label\` is not valid)

     * RuntimeError (Argument \`indep_axis_tick_labels\` is not valid)

     * RuntimeError (Argument \`indep_var_units\` is not valid)

     * RuntimeError (Argument \`log_indep_axis\` is not valid)

     * RuntimeError (Argument \`panels\` is not valid)

     * RuntimeError (Argument \`title\` is not valid)

     * RuntimeError (Figure object is not fully specified)

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
    def __init__(self, panels=None, indep_var_label='', indep_var_units='',
        indep_axis_tick_labels=None, indep_axis_ticks=None, fig_width=None,
        fig_height=None, title='', log_indep_axis=False, dpi=100.0):
        pexdoc.exh.addai(
            'indep_axis_ticks',
            (indep_axis_ticks is not None) and (
                (not isinstance(indep_axis_ticks, list)) and
                (not isinstance(indep_axis_ticks, numpy.ndarray))
            )
        )
        pexdoc.exh.addai(
            'indep_axis_tick_labels',
            (indep_axis_tick_labels is not None) and
            ((not isinstance(indep_axis_tick_labels, list)) or
            (isinstance(indep_axis_tick_labels, list) and
            (indep_axis_ticks is not None) and
            (len(indep_axis_tick_labels) != len(indep_axis_ticks))))
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
        self._prev_indep_axis_ticks = None
        self._axes_list = []
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


    def __bool__(self): # pragma: no cover
        """
        Returns :code:`True` if the figure has at least a panel associated with
        it, :code:`False` otherwise

        .. note:: This method applies to Python 3.x
        """
        self._create_figure()
        return self._panels is not None

    def __iter__(self):
        r"""
        Returns an iterator over the panel object(s) in the figure.
        For example:

        .. =[=cog
        .. import pmisc
        .. pmisc.incfile('plot_example_7.py', cog.out)
        .. =]=
        .. code-block:: python

            # plot_example_7.py
            from __future__ import print_function
            import numpy, pplot

            def figure_iterator_example(no_print):
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
        """
        self._create_figure()
        return iter(self._panels)

    def __nonzero__(self):  # pragma: no cover
        """
        Returns :code:`True` if the figure has at least a panel associated with
        it, :code:`False` otherwise

        .. note:: This method applies to Python 2.x
        """
        self._create_figure()
        return self._panels is not None

    def __str__(self):
        r"""
        Prints figure information. For example:

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
        ret = ''
        if (self.panels is None) or (len(self.panels) == 0):
            ret += 'Panels: None\n'
        else:
            for num, element in enumerate(self.panels):
                ret += 'Panel {0}:\n'.format(num)
                temp = str(element).split('\n')
                temp = [3*' '+line for line in temp]
                ret += '\n'.join(temp)
                ret += '\n'
        ret += 'Independent variable label: {0}\n'.format(
            self.indep_var_label
            if self.indep_var_label not in ['', None] else
            'not specified'
        )
        ret += 'Independent variable units: {0}\n'.format(
            self.indep_var_units
            if self.indep_var_units not in ['', None] else
            'not specified'
        )
        ret += 'Logarithmic independent axis: {0}\n'.format(
            self.log_indep_axis
        )
        ret += 'Title: {0}\n'.format(
            self.title if self.title not in ['', None] else 'not specified'
        )
        ret += 'Figure width: {0}\n'.format(fig_width)
        ret += 'Figure height: {0}\n'.format(fig_height)
        return ret

    def _axis_box_dim(self, axis, axis_type='x'):
        """ Returns minimum axis box size given label width """
        xaxis = axis_type.lower() == 'x'
        sep = (1.5 if xaxis else 0.5)*SPACER
        dim = 'width' if xaxis else 'height'
        locs = self._indep_axis_ticks if xaxis else axis.get_ticklocs()
        tlabels = axis.get_ticklabels()
        tlabels = [label for label in tlabels if _get_text(label)]
        if not tlabels:
            # X axis in a panel that is configured to not display the
            # independent axis, for example
            return
        bboxes = [self._bbox(label) for label in tlabels]
        mult = 3 if axis.log_axis else 1
        label_half_dim = [(getattr(bbox, dim)+mult*sep)/2.0 for bbox in bboxes]
        min_label_half_dim = max(label_half_dim)*(len(label_half_dim)-1)
        if axis.log_axis:
            return min_label_half_dim
        tick_diffs = numpy.diff(numpy.array(locs))
        curr_label, prev_label = label_half_dim[1:], label_half_dim[:-1]
        sep_dim = [curr+prev for curr, prev in zip(curr_label, prev_label)]
        dpu = max(sep_dim/tick_diffs)
        axis_box_dim = (locs[-1]-locs[0])*dpu
        return axis_box_dim

    def _axis_side_dim(self, axis, axis_type='indep', axis_box_edge=0):
        """ Returns minimum space required by axis label and tick marks """
        indep = axis_type.lower() == 'indep'
        primary = axis_type.lower() == 'primary'
        sign = +1 if indep or primary else -1
        func = _lmin if indep or primary else _lmax
        dim = 'ymin' if indep else ('xmin' if primary else 'xmax')
        label = _get_text(axis.get_label())
        label_dim = getattr(self._bbox(axis.get_label()), dim) if label else 0
        tick_bbox = self._axis_ticks_bbox(axis)
        tick_edge = func([getattr(bbox, dim) for bbox in tick_bbox])
        tick_dim = sign*(axis_box_edge-tick_edge) if tick_bbox else 0
        edge = tick_edge if tick_bbox else axis_box_edge
        label_plus_padding = sign*(edge-label_dim) if label else 0
        return label_plus_padding, tick_dim

    def _axis_ticks_bbox(self, axis):
        """ Get bounding box of non-empty axis ticks """
        return [
            self._bbox(tick)
            for tick in axis.get_ticklabels() if _get_text(tick)
        ]

    def _axis_ticks_dim(self, axis, dim):
        """ Returns requested dimension of non-empty axis tick labels """
        return [getattr(item, dim) for item in self._axis_ticks_bbox(axis)]

    def _axis_ticks_xmax(self, axis):
        """ Returns xmax dimension of ticks bounding box """
        return self._axis_ticks_dim(axis, 'xmax')

    def _axis_ticks_xmin(self, axis):
        """ Returns xmin dimension of ticks bounding box """
        return self._axis_ticks_dim(axis, 'xmin')

    def _axis_ticks_ymax(self, axis):
        """ Returns ymax dimension of ticks bounding box """
        return self._axis_ticks_dim(axis, 'ymax')

    def _axis_ticks_ymin(self, axis):
        """ Returns ymin dimension of ticks bounding box """
        return self._axis_ticks_dim(axis, 'ymin')

    def _bbox(self, obj):
        """ Returns bounding box of an object """
        renderer = self._fig.canvas.get_renderer()
        return obj.get_window_extent(renderer=renderer).transformed(
            self._fig.dpi_scale_trans.inverted()
        )

    def _calculate_figure_bbox(self):
        """ Returns bounding box of figure """
        top = self._fig_top()
        bottom = self._fig_bottom()
        right = max(self._panel_edge(obj, 'right') for obj in self._axes_list)
        left = min(self._panel_edge(obj, 'left') for obj in self._axes_list)
        fig_bbox = Bbox([[left, bottom], [right, top]])
        return fig_bbox

    def _calculate_min_figure_size(self):
        """ Calculates minimum panel and figure size """
        dround = lambda x: math.floor(x)/self.dpi
        title_height = title_width = 0
        top_panel = self._axes_list[0]
        axes = (top_panel['primary'], top_panel['secondary'])
        axes = [axis for axis in axes if axis and axis.get_title().strip()]
        if axes:
            axis = axes[0] # There should be only one
            title_obj = axis.title
            title_bbox = self._bbox(title_obj)
            label_bbox = self._bbox(axis.yaxis.get_ticklabels()[-1])
            title_pad = title_bbox.ymin-label_bbox.ymax
            title_height = (title_bbox.height+title_pad)*self.dpi
            title_width = title_bbox.width*self.dpi
        adicts = self._axes_list
        panels_width = max(self._min_panel(adict, 'x') for adict in adicts)
        panels_height = max(self._min_panel(adict, 'y') for adict in adicts)
        self._min_fig_width = dround(max(title_width, panels_width))
        npanels = len(self._axes_list)
        self._min_fig_height = dround(
            npanels*(panels_height+PANEL_SEP)-PANEL_SEP+title_height
        )

    def _check_figure_spec(self, fig_width=None, fig_height=None):
        """ Validates given figure size against minimum dimension """
        small_ex = pexdoc.exh.addex(
            RuntimeError,
            'Figure size is too small: minimum width *[min_width]*, '
            'minimum height *[min_height]*'
        )
        small_ex(
            bool(
                (fig_width and (fig_width < self._min_fig_width)) or
                (fig_height and (fig_height < self._min_fig_height))
            ),
            [
                _F('min_width', self._min_fig_width),
                _F('min_height', self._min_fig_height)
            ]
        )

    def _create_figure(self, raise_exception=False):
        """ Create and resize figure """
        specified_ex = pexdoc.exh.addex(
            RuntimeError, 'Figure object is not fully specified'
        )
        specified_ex(raise_exception and (not self._complete))
        if not self._complete:
            return
        if self._need_redraw:
            self._size_given = (
                (self._fig_width is not None) and (self._fig_height is not None)
            )
            # First _draw call is to calculate approximate figure size, (until
            # matplotlib actually draws the figure, all the bounding boxes of
            # the elements in the figure are null boxes. The second _draw call
            # is to draw figure with either the calculated minimum dimensions
            # or the user-given dimensions, provided they are equal or greater
            # than the minimum dimensions
            self._draw()
            #self._draw()
            bbox = self._calculate_figure_bbox()
            #self._min_fig_width = math.floor(self.dpi*bbox.width)/self.dpi
            #self._min_fig_height = math.floor(self.dpi*bbox.height)/self.dpi
            fig_width, fig_height = self._fig_dims()
            self._fig.set_size_inches(fig_width, fig_height, forward=True)
            self._need_redraw = False
            # From https://github.com/matplotlib/matplotlib/issues/7984:
            # When the Figure is drawn, its Axes are sorted based on zorder with a
            # stable sort, and then drawn in that order. Then within each Axes,
            # artists are sorted based on zorder. Therefore you can't interleave
            # the drawing orders of artists from one Axes with those from another.
        else:
            bbox = self._calculate_figure_bbox()
        fig_width, fig_height = self._fig_dims()
        # Get figure pixel size exact
        width = int(round(fig_width*self._dpi))
        lwidth = int(round(width/2.0))
        rwidth = width-lwidth
        height = int(round(fig_height*self._dpi))
        bheight = int(round(height/2.0))
        theight = height-bheight
        bbox_xcenter = bbox.xmin+0.5*bbox.width
        bbox_ycenter = bbox.ymin+0.5*bbox.height
        bbox = Bbox(
            [
                [
                    bbox_xcenter-(lwidth/self._dpi),
                    bbox_ycenter-(bheight/self._dpi)
                ],
                [
                    bbox_xcenter+(rwidth/self._dpi),
                    bbox_ycenter+(theight/self._dpi)
                ]
            ]
        )
        return bbox

    def _draw(self):
        # pylint: disable=C0326,W0612
        log_ex = pexdoc.exh.addex(
            ValueError,
            'Figure cannot be plotted with a logarithmic '
            'independent axis because panel *[panel_num]*, series '
            '*[series_num]* contains negative independent data points'
        )
        ticks_num_ex = pexdoc.exh.addex(
            RuntimeError,
            'Number of tick locations and number of tick labels mismatch'
        )
        num_panels = len(self.panels)
        # Restore scaling
        if self._indep_var_div is not None:
            for panel_obj in self.panels:
                panel_obj._scale_indep_var(1/float(self._indep_var_div))
            self._indep_var_div = 1.0
            self._indep_axis_ticks = self._prev_indep_axis_ticks
        # Find union of the independent variable data set of all panels
        indep_axis_ticks = self._get_global_xaxis()
        self._indep_var_div = indep_axis_ticks.div
        self._prev_indep_axis_ticks = self._indep_axis_ticks
        self._indep_axis_ticks = indep_axis_ticks.locs
        # Scale all panel series
        for panel_obj in self.panels:
            panel_obj._scale_indep_var(self._indep_var_div)
        # Draw panels
        self._indep_axis_tick_labels = (
            self._indep_axis_tick_labels or indep_axis_ticks.labels
        )
        indep_axis_dict = {
            'log_indep':self.log_indep_axis,
            'indep_var_min':indep_axis_ticks.min,
            'indep_var_max':indep_axis_ticks.max,
            'indep_var_locs':indep_axis_ticks.locs,
            'indep_var_labels':self._indep_axis_tick_labels,
            'indep_axis_label':self.indep_var_label,
            'indep_axis_units':self.indep_var_units,
            'indep_axis_unit_scale':indep_axis_ticks.unit_scale
        }
        # Create required number of panels
        self._fig, axes = self._draw_panels(indep_axis_dict)
        if self.title not in [None, '']:
            top_panel = self._axes_list[0]
            axes = top_panel['primary'] or top_panel['secondary']
            axes.set_title(
                self.title,
                horizontalalignment='center',
                verticalalignment='bottom',
                multialignment='center',
                fontsize=TITLE_FONT_SIZE
            )
        # Draw figure otherwise some bounding boxes return NaN
        FigureCanvasAgg(self._fig).draw()
        self._calculate_min_figure_size()

    def _draw_panels(self, indep_axis_dict):
        num_panels = len(self.panels)
        fig_width, fig_height = self._fig_dims()
        figsize = (fig_width, fig_height) if fig_width and fig_height else None
        plt.close('all')
        self._fig = plt.figure(dpi=self.dpi, figsize=figsize)
        axes = [plt.subplot(num_panels, 1, num+1) for num in range(num_panels)]
        keys = ['number', 'primary', 'secondary']
        axes = []
        self._axes_list = []
        for num, panel_obj in enumerate(self.panels):
            axis = plt.subplot(num_panels, 1, num+1)
            disp_indep_axis = (num_panels == 1) or panel_obj.display_indep_axis
            panel_dict = panel_obj._draw(
                axis, indep_axis_dict, disp_indep_axis
            )
            if panel_dict['primary'] and panel_dict['secondary'] and fig_width:
                delta = self._panel_right_adjust(panel_dict)/fig_width
                fbbox = [0, 0, 1-delta, 1]
                if delta:
                    plt.delaxes(axis)
                    axis = plt.subplot(num_panels, 1, num+1)
                    panel_dict = panel_obj._draw(
                        axis, indep_axis_dict, disp_indep_axis, fbbox
                    )
            axes.append(axis)
            panel_dict['number'] = num
            self._axes_list.append(
                dict((item, panel_dict[item]) for item in keys)
            )
        return self._fig, axes

    def _fig_bottom(self):
        panel = self._axes_list[-1]
        axes = [self._axes_list[0]['primary'], self._axes_list[0]['secondary']]
        axes = [axis for axis in axes if axis]
        yaxes = [axis.yaxis for axis in axes]
        yaxes_label = [axis for axis in yaxes if self._label_text(axis)]
        ylabels = [axis.get_label() for axis in yaxes_label]
        xaxis = (panel['primary'] or panel['secondary']).xaxis
        xlabel = self._label_text(xaxis)
        xtick_bot = _lmin(self._axis_ticks_ymin(xaxis))
        ytick_bot = _lmin([self._axis_ticks_ymin(axis) for axis in yaxes])
        xlabel_bot = self._bbox(xaxis.get_label()).ymin if xlabel else INF
        ylabel_bot = _lmin([self._bbox(ylabel).ymin for ylabel in ylabels])
        return min(xtick_bot, xlabel_bot, ytick_bot, ylabel_bot)

    def _fig_dims(self):
        """ Get actual figure size, given or minimum calculated """
        fig_width = self._fig_width or self._min_fig_width
        fig_height = self._fig_height or self._min_fig_height
        return fig_width, fig_height

    def _fig_top(self):
        panel = self._axes_list[0]
        axes = [panel['primary'], panel['secondary']]
        axes = [axis for axis in axes if axis]
        yaxes = [axis.yaxis for axis in axes]
        axes_title = [axis for axis in axes if axis.get_title().strip()]
        yaxes_label = [axis for axis in yaxes if self._label_text(axis)]
        ylabels = [axis.get_label() for axis in yaxes_label]
        title_top = _lmax([self._bbox(axis.title).ymax for axis in axes_title])
        ytick_top = _lmax([self._axis_ticks_ymax(axis) for axis in yaxes])
        ylabel_top = _lmax([self._bbox(ylabel).ymax for ylabel in ylabels])
        return max(title_top, ytick_top, ylabel_top)

    def _get_axes_list(self):
        self._create_figure()
        return self._axes_list

    def _get_complete(self):
        """
        Returns True if figure is fully specified, otherwise returns False
        """
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
            'Figure cannot be plotted with a logarithmic '
            'independent axis because panel *[panel_num]*, series '
            '*[series_num]* contains negative independent data points'
        )
        ticks_num_ex = pexdoc.exh.addex(
            RuntimeError,
            'Number of tick locations and number of tick labels mismatch'
        )
        glob_indep_var = []
        for panel_num, panel_obj in enumerate(self.panels):
            for series_num, series_obj in enumerate(panel_obj.series):
                log_ex(
                    bool(
                        self.log_indep_axis and
                        (min(series_obj.indep_var) < 0)
                    ),
                    edata=_MF(
                        'panel_num', panel_num, 'series_num', series_num
                    )
                )
                glob_indep_var = numpy.unique(
                    numpy.append(
                        glob_indep_var,
                        numpy.array(
                            [
                                peng.round_mantissa(element, 10)
                                for element in series_obj.indep_var
                            ]
                        )
                    )
                )
        indep_axis_ticks = _intelligent_ticks(
            glob_indep_var,
            min(glob_indep_var),
            max(glob_indep_var),
            tight=True,
            log_axis=self.log_indep_axis,
            tick_list=(
                None if self._log_indep_axis else self._indep_axis_ticks
            )
        )
        ticks_num_ex(
            (self._indep_axis_tick_labels is not None) and
            (
                len(self._indep_axis_tick_labels)
                !=
                len(indep_axis_ticks.labels)
            )
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

    def _label_text(self, axis):
        """ Returns axis label text """
        return _get_text(axis.get_label())

    def _label_bbox(self, axes, prop):
        """ Returns bounding box of non-empty axis labels """
        lobj = [(axis.get_label(), self._label_text(axis)) for axis in axes]
        bboxes = [self._bbox(bbox) for bbox, label in lobj if label]
        return [getattr(bbox, prop) for bbox in bboxes]

    def _min_panel(self, adict, axis_type):
        """ Returns minimum panel width panel """
        prim_dep_axis, sec_dep_axis = adict['primary'], adict['secondary']
        axis_type = axis_type.lower()
        xaxis = axis_type == 'x'
        min_prop = 'xmin' if xaxis else 'ymin'
        max_prop = 'xmax' if xaxis else 'ymax'
        dim_prop = 'width' if xaxis else 'height'
        saxis = 'xaxis' if xaxis else 'yaxis'
        _axis_box_dim = partial(self._axis_box_dim, axis_type=axis_type)
        ###
        # Overhang refers to axis label or first or last tick mark label
        # extending past axis "box". Note that first or last label may
        # not be at the edges of the box, since some labels can be set
        # to empty string ('')
        ###
        own_first_overhang = own_last_overhang = 0
        axes = [axis for axis in [prim_dep_axis, sec_dep_axis] if axis]
        daxes = [getattr(axis, saxis) for axis in axes]
        axis_box_dim = _lmax([_axis_box_dim(axis) for axis in daxes])
        # Minimum panel width/height is 1 inch, in pathological cases, for
        # example where all panels are configured not to show the
        # independent axis
        axis_box_dim = axis_box_dim or 5*SPACER
        indep_axis = [
            item.get_xaxis() for item in axes if item.display_indep_axis
        ]
        own_label_overhang = 0
        spines_bboxes_list = [
            [self._bbox(axis.spines['left']), self._bbox(axis.spines['right'])]
            if xaxis else
            [self._bbox(axis.spines['bottom']), self._bbox(axis.spines['top'])]
            for axis in axes
        ]
        axes = [getattr(axis, 'get_{0}'.format(saxis))() for axis in axes]
        for axis, spines_bboxes in zip(axes, spines_bboxes_list):
            own_first_mid = getattr(spines_bboxes[0], min_prop)
            own_last_mid = getattr(spines_bboxes[-1], max_prop)
            tick_label_bboxes = self._axis_ticks_bbox(axis)
            if not tick_label_bboxes:
                continue
            first_bbox = tick_label_bboxes[0]
            last_bbox = tick_label_bboxes[-1]
            label_bbox = self._bbox(axis.get_label())
            label_dim = getattr(label_bbox, dim_prop)
            ilabel_overhang = max(0, (label_dim-axis_box_dim)/2.0)
            own_label_overhang = max(own_label_overhang, ilabel_overhang)
            iown_first_overhang = own_first_mid-getattr(first_bbox, min_prop)
            own_first_overhang = max(own_first_overhang, iown_first_overhang)
            iown_last_overhang = getattr(last_bbox, max_prop)-own_last_mid
            own_last_overhang = max(own_last_overhang, iown_last_overhang)
        own_start_overhang = _lmax(own_first_overhang, own_label_overhang)
        own_stop_overhang = _lmax(own_last_overhang, own_label_overhang)
        left_label_plus_pad, left_tick_dim = self._axis_side_dim(
            prim_dep_axis.yaxis, 'primary', own_first_mid
        ) if xaxis and prim_dep_axis else (0, 0)
        right_label_plus_pad, right_tick_dim = self._axis_side_dim(
            sec_dep_axis.yaxis, 'secondary', own_last_mid
        ) if xaxis and sec_dep_axis else (0, 0)
        kwargs = dict(axis_type='indep', axis_box_edge=own_first_mid)
        for axis in indep_axis if not xaxis else []:
            ilabel_plus_pad, itick_dim = self._axis_side_dim(axis, **kwargs)
            left_label_plus_pad = max(left_label_plus_pad, ilabel_plus_pad)
            left_tick_dim = max(left_tick_dim, itick_dim)
        ret = (
            left_label_plus_pad+
            max(left_tick_dim, own_start_overhang)+
            axis_box_dim+
            max(right_tick_dim, own_stop_overhang)+
            right_label_plus_pad
        )*self.dpi
        return ret

    def _panel_edge(self, adict, stype):
        left = stype.lower() == 'left'
        fmm = _lmin if left else _lmax
        prop = 'xmin' if left else 'xmax'
        func = self._axis_ticks_xmin if left else self._axis_ticks_xmax
        axes = [adict['primary'], adict['secondary']]
        axes = [axis for axis in axes if axis]
        title_objs = [axis.title for axis in axes if _get_text(axis.title)]
        title_bboxes = [self._bbox(title_obj) for title_obj in title_objs]
        title_edge = fmm([getattr(bbox, prop) for bbox in title_bboxes])
        xaxes = [axis.xaxis for axis in axes]
        xtick_edge = fmm([func(xaxis) for xaxis in xaxes])
        xlabel_edge = fmm(self._label_bbox(xaxes, prop))
        spines = [[axis.spines['bottom'], axis.spines['top']] for axis in axes]
        spines = [spine[0 if left else -1] for spine in spines]
        spines_bboxes = [self._bbox(spine) for spine in spines]
        spine_edge = fmm([getattr(bbox, prop) for bbox in spines_bboxes])
        axis = adict['primary' if left else 'secondary']
        yaxis = axis.yaxis if axis else None
        ytick_edge = fmm(self._axis_ticks_dim(yaxis, prop)) if yaxis else None
        ylabel_edge = fmm(self._label_bbox([yaxis], prop)) if yaxis else None
        return fmm(
            title_edge,
            spine_edge,
            xtick_edge,
            xlabel_edge,
            ytick_edge,
            ylabel_edge
        )

    def _panel_right_adjust(self, adict):
        prop = 'xmax'
        axes = [adict['primary']]
        title_objs = [axis.title for axis in axes if _get_text(axis.title)]
        title_bboxes = [self._bbox(title_obj) for title_obj in title_objs]
        title_edge = _lmax([bbox.xmax for bbox in title_bboxes])
        xaxes = [axis.xaxis for axis in axes]
        xtick_edge = _lmax([self._axis_ticks_xmax(xaxis) for xaxis in xaxes])
        xlabel_edge = _lmax(self._label_bbox(xaxes, prop))
        spines = [axis.spines['right'] for axis in axes]
        spines_bboxes = [self._bbox(spine) for spine in spines]
        spine_edge = _lmax([bbox.xmax for bbox in spines_bboxes])
        x_edge = _lmax(title_edge, spine_edge, xtick_edge, xlabel_edge)
        renderer = self._fig.canvas.get_renderer()
        yaxis = adict['secondary'].yaxis
        y_edge = yaxis.get_tightbbox(renderer=renderer).transformed(
            self._fig.dpi_scale_trans.inverted()
        ).xmax
        return _lmax(0, y_edge-x_edge)

    @pexdoc.pcontracts.contract(dpi='None|positive_real_num')
    def _set_dpi(self, dpi):
        self._dpi = float(dpi)

    @pexdoc.pcontracts.contract(fig_height='None|positive_real_num')
    def _set_fig_height(self, fig_height):
        if self._complete:
            self._create_figure()
            self._check_figure_spec(self.fig_width, fig_height)
        self._fig_height = fig_height
        self._need_redraw = True

    @pexdoc.pcontracts.contract(fig_width='None|positive_real_num')
    def _set_fig_width(self, fig_width):
        if self._complete:
            self._create_figure()
            self._check_figure_spec(fig_width, self.fig_height)
        self._fig_width = fig_width
        self._need_redraw = True

    @pexdoc.pcontracts.contract(
        indep_axis_ticks='None|increasing_real_numpy_vector'
    )
    def _set_indep_axis_ticks(self, indep_axis_ticks):
        self._indep_axis_ticks = indep_axis_ticks
        self._need_redraw = True

    @pexdoc.pcontracts.contract(indep_axis_tick_labels='None|list(str)')
    def _set_indep_axis_tick_labels(self, indep_axis_tick_labels):
        self._indep_axis_tick_labels = indep_axis_tick_labels
        self._need_redraw = True
        self._create_figure()

    @pexdoc.pcontracts.contract(indep_var_label='None|str')
    def _set_indep_var_label(self, indep_var_label):
        self._indep_var_label = indep_var_label
        self._need_redraw = True

    @pexdoc.pcontracts.contract(indep_var_units='None|str')
    def _set_indep_var_units(self, indep_var_units):
        self._indep_var_units = indep_var_units
        self._need_redraw = True

    @pexdoc.pcontracts.contract(log_indep_axis='None|bool')
    def _set_log_indep_axis(self, log_indep_axis):
        self._log_indep_axis = log_indep_axis
        self._need_redraw = True

    @pexdoc.pcontracts.contract(title='None|str')
    def _set_title(self, title):
        self._title = title
        self._need_redraw = True

    def _set_panels(self, panels):
        self._panels = (
            (panels if isinstance(panels, list) else [panels])
            if panels is not None else
            panels
        )
        if self.panels is not None:
            self._validate_panels()
        self._need_redraw = True

    def _validate_panels(self):
        """
        Verifies that elements of panel list are of the right type and
        fully specified
        """
        invalid_ex = pexdoc.exh.addai('panels')
        specified_ex = pexdoc.exh.addex(
            TypeError, 'Panel *[panel_num]* is not fully specified'
        )
        for num, obj in enumerate(self.panels):
            invalid_ex(not isinstance(obj, Panel))
            specified_ex(not obj._complete, _F('panel_num', num))

    @pexdoc.pcontracts.contract(fname='file_name', ftype=str)
    def save(self, fname, ftype='PNG'):
        r"""
        Saves the figure to a file

        :param fname: File name
        :type  fname: `FileName <http://pexdoc.readthedocs.io/en/stable/
                      ptypes.html#filename>`_

        :param ftype: File type, either 'PNG' or 'EPS' (case insensitive). The
                      PNG format is a `raster
                      <https://en.wikipedia.org/wiki/Raster_graphics>`_ format
                      while the EPS format is a
                      `vector <https://en.wikipedia.org/wiki/
                      Vector_graphics>`_ format
        :type  ftype: string

        .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. pplot.figure.Figure.save

        :raises:
         * RuntimeError (Argument \`fname\` is not valid)

         * RuntimeError (Argument \`ftype\` is not valid)

         * RuntimeError (Figure object is not fully specified)

         * RuntimeError (Unsupported file type: *[file_type]*)

        .. [[[end]]]
        """
        unsupported_ex = pexdoc.exh.addex(
            RuntimeError, 'Unsupported file type: *[file_type]*'
        )
        unsupported_ex(
            ftype.lower() not in ['png', 'eps'], _F('file_type', ftype)
        )
        _, extension = os.path.splitext(fname)
        if (not extension) or (extension == '.'):
            fname = '{file_name}.{extension}'.format(
                file_name=fname.rstrip('.'),
                extension=ftype.lower()
            )
        bbox = self._create_figure(raise_exception=True)
        dpi = self.dpi if ftype == 'PNG' else None
        bbox = bbox if ftype == 'PNG' else 'tight'
        # Matplotlib seems to have a problem with ~/, expand it to $HOME
        fname = os.path.expanduser(fname)
        pmisc.make_dir(fname)
        self._fig_width, self._fig_height = self._fig_dims()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            #self._fig.savefig(
            #    fname, dpi=dpi, bbox_inches=bbox, format=ftype, pad_inches=0
            #)
            self._fig.savefig(
                fname, dpi=dpi, format=ftype, pad_inches=0
            )
        plt.close('all')

    def show(self):
        """
        Displays the figure

        .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. pplot.figure.Figure.show

        :raises:
         * RuntimeError (Figure object is not fully specified)

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

    axes_list = property(
        _get_axes_list, doc='Matplotlib figure axes handle list'
    )
    """
    Gets the Matplotlib figure axes handle list or :code:`None` if figure is
    not fully specified. Useful if annotations or further customizations to
    the panel(s) are needed. Each panel has an entry in the list, which is
    sorted in the order the panels are plotted (top to bottom). Each panel
    entry is a dictionary containing the following key-value pairs:

    * **number** (*integer*) -- panel number, panel 0 is the top-most panel

    * **primary** (*Matplotlib axis object*) -- axis handle for the primary
      axis, None if the figure has not primary axis

    * **secondary** (*Matplotlib axis object*) -- axis handle for the
      secondary axis, None if the figure has no secondary axis

    :type: list
    """

    dpi = property(
        _get_dpi, _set_dpi, doc='Figure dots per inch (DPI)'
    )
    r"""
    Gets or sets the dots per inch (DPI) of the figure

    :type: `PositiveRealNum <http://pexdoc.readthedocs.io/en/
           stable/ptypes.html#positiverealnum>`_ or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.dpi

    :raises: (when assigned) RuntimeError (Argument \`dpi\` is not
     valid)

    .. [[[end]]]
    """

    fig = property(_get_fig, doc='Figure handle')
    """
    Gets the Matplotlib figure handle. Useful if annotations or further
    customizations to the figure are needed. :code:`None` if figure is not
    fully specified

    :type: Matplotlib figure handle or None
    """

    fig_height = property(
        _get_fig_height, _set_fig_height, doc='height of the hard copy plot'
    )
    r"""
    Gets or sets the height (in inches) of the hard copy plot, :code:`None` if
    figure is not fully specified.

    :type: `PositiveRealNum <http://pexdoc.readthedocs.io/en/
           stable/ptypes.html#positiverealnum>`_ or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.fig_height

    :raises: (when assigned) RuntimeError (Argument \`fig_height\` is not
     valid)

    .. [[[end]]]
    """

    fig_width = property(
        _get_fig_width, _set_fig_width, doc='Width of the hard copy plot'
    )
    r"""
    Gets or sets the width (in inches) of the hard copy plot, :code:`None` if
    figure is not fully specified

    :type: `PositiveRealNum <http://pexdoc.readthedocs.io/en/
           stable/ptypes.html#positiverealnum>`_ or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.fig_width

    :raises: (when assigned) RuntimeError (Argument \`fig_width\` is not
     valid)

    .. [[[end]]]
    """

    indep_axis_scale = property(
        _get_indep_axis_scale, doc='Independent axis scale'
    )
    """
    Gets the scale of the figure independent axis, :code:`None` if figure is
    not fully specified

    :type:  float or None if figure has no panels associated with it
    """

    indep_axis_ticks = property(
        _get_indep_axis_ticks,
        _set_indep_axis_ticks,
        doc='Independent axis tick locations'
    )
    r"""
    Gets or sets the independent axis (scaled) tick locations, :code:`None` if
    figure is not fully specified

    :type: list

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.indep_axis_ticks

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_axis_ticks\` is not valid)

    .. [[[end]]]
    """

    indep_axis_tick_labels = property(
        _get_indep_axis_tick_labels,
        _set_indep_axis_tick_labels,
        doc='Independent axis tick labels'
    )
    r"""
    Gets or sets the independent axis tick labels

    :type: list of strings

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.indep_axis_tick_labels

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_var_tick_labels\` is not valid)

     * RuntimeError (Number of tick locations and number of tick labels
       mismatch)

    .. [[[end]]]
    """

    indep_var_label = property(
        _get_indep_var_label,
        _set_indep_var_label,
        doc='Figure independent axis label'
    )
    r"""
    Gets or sets the figure independent variable label

    :type: string or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.indep_var_label

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_var_label\` is not valid)

     * RuntimeError (Figure object is not fully specified)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """

    indep_var_units = property(
        _get_indep_var_units,
        _set_indep_var_units,
        doc='Figure independent axis units'
    )
    r"""
    Gets or sets the figure independent variable units

    :type: string or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.indep_var_units

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_var_units\` is not valid)

     * RuntimeError (Figure object is not fully specified)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """

    log_indep_axis = property(
        _get_log_indep_axis, _set_log_indep_axis, doc='Figure log_indep_axis'
    )
    r"""
    Gets or sets the figure logarithmic independent axis flag; indicates
    whether the independent axis is linear (False) or logarithmic (True)

    :type: boolean

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.log_indep_axis

    :raises: (when assigned)

     * RuntimeError (Argument \`log_indep_axis\` is not valid)

     * RuntimeError (Figure object is not fully specified)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """

    panels = property(_get_panels, _set_panels, doc='Figure panel(s)')
    r"""
    Gets or sets the figure panel(s), :code:`None` if no panels have been
    specified

    :type: :py:class:`pplot.Panel`, list of
           :py:class:`pplot.panel` or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.panels

    :raises: (when assigned)

     * RuntimeError (Argument \`fig_height\` is not valid)

     * RuntimeError (Argument \`fig_width\` is not valid)

     * RuntimeError (Argument \`panels\` is not valid)

     * RuntimeError (Figure object is not fully specified)

     * RuntimeError (Figure size is too small: minimum width *[min_width]*,
       minimum height *[min_height]*)

     * TypeError (Panel *[panel_num]* is not fully specified)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """

    title = property(_get_title, _set_title, doc='Figure title')
    r"""
    Gets or sets the figure title

    :type: string or None

    .. [[[cog cog.out(exobj_plot.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. pplot.figure.Figure.title

    :raises: (when assigned)

     * RuntimeError (Argument \`title\` is not valid)

     * RuntimeError (Figure object is not fully specified)

     * ValueError (Figure cannot be plotted with a logarithmic independent
       axis because panel *[panel_num]*, series *[series_num]* contains
       negative independent data points)

    .. [[[end]]]
    """
