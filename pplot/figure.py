# figure.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,R0201,R0914,R0915,W0105,W0212

# Standard library imports
from __future__ import print_function
import math
import os
import sys
# import warnings
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
        self._axes_list = []
        self._scaling_done = False
        self._indep_axis_dict = None
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

    def _calculate_min_figure_size(self):
        """ Calculates minimum panel and figure size """
        dround = lambda x: math.floor(x)/self.dpi
        min_width = (
            max(panel._left_overhang for panel in self.panels)+
            max(panel._min_spine_bbox.width for panel in self.panels)+
            max(panel._right_overhang for panel in self.panels)
        )
        self._min_fig_width = dround(min_width*self.dpi)
        npanels = len(self.panels)
        self._min_fig_height = dround(
            sum([panel._min_bbox.height*self.dpi for panel in self.panels])+
            ((npanels-1)*PANEL_SEP)
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
            return Bbox([[0, 0], [0, 0]])
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
            self._draw()
            bbox = self._fig_bbox()
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
            bbox = self._fig_bbox()
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
                'log_indep':self.log_indep_axis,
                'indep_var_min':indep_axis_ticks.min,
                'indep_var_max':indep_axis_ticks.max,
                'indep_var_locs':indep_axis_ticks.locs,
                'indep_var_labels':self._indep_axis_tick_labels,
                'indep_axis_label':self.indep_var_label,
                'indep_axis_units':self.indep_var_units,
                'indep_axis_unit_scale':indep_axis_ticks.unit_scale
            }
            self._scaling_done = True
        # Create required number of panels
        self._draw_panels(self._indep_axis_dict)
        # Draw figure otherwise some bounding boxes return NaN
        FigureCanvasAgg(self._fig).draw()
        self._calculate_min_figure_size()

    def _draw_panels(self, indep_axis_dict, fbbox=None):
        def init_figure(num_panels, fbbox=None):
            fig_width, fig_height = self._fig_dims()
            figsize = (fig_width, fig_height) if fig_width and fig_height else None
            plt.close('all')
            self._fig, axesh = plt.subplots(
                nrows=num_panels, ncols=1, dpi=self.dpi, figsize=figsize
            )
            plt.tight_layout(rect=fbbox, pad=0, h_pad=2)
            axesh = [axesh] if num_panels == 1 else axesh
            return axesh, fig_width, fig_height
        num_panels = len(self.panels)
        axesh, fig_width, fig_height = init_figure(num_panels, fbbox)
        self._axes_list = []
        top = right = -INF
        bottom = left = +INF
        if all(not panel.display_indep_axis for panel in self.panels):
            self.panels[-1].display_indep_axis = True
        for num, (panel, axish) in enumerate(zip(self.panels, axesh)):
            title = self.title if not num else None
            disp_indep_axis = (num_panels == 1) or panel.display_indep_axis
            panel._draw(disp_indep_axis, indep_axis_dict, title, axish)
            left = min(left, panel._panel_bbox.xmin)
            bottom = min(bottom, panel._panel_bbox.ymin)
            right = max(right, panel._panel_bbox.xmax)
            top = max(top, panel._panel_bbox.ymax)
        if fig_width and fig_height:
            xdelta_left = -left/fig_width
            ydelta_bot = -bottom/fig_height
            xdelta_right = (right-fig_width)/fig_width
            ydelta_top = (top-fig_height)/fig_height
            fbbox = [
                0+xdelta_left, 0+ydelta_bot, 1-xdelta_right, 1-ydelta_top
            ]
            axesh, _, _ = init_figure(num_panels, fbbox)
            for num, (panel, axish) in enumerate(zip(self.panels, axesh)):
                title = self.title if not num else None
                disp_indep_axis = (num_panels == 1) or panel.display_indep_axis
                panel._draw(disp_indep_axis, indep_axis_dict, title, axish)

    def _fig_bbox(self):
        """ Returns bounding box of figure """
        left = min(pobj._left for pobj in self.panels)
        bottom = min(pobj._bottom for pobj in self.panels)
        top = max(pobj._top for pobj in self.panels)
        right = max(pobj._right for pobj in self.panels)
        fig_bbox = Bbox([[left, bottom], [right, top]])
        return fig_bbox

    def _fig_dims(self):
        """ Get actual figure size, given or minimum calculated """
        fig_width = self._fig_width or self._min_fig_width
        fig_height = self._fig_height or self._min_fig_height
        return fig_width, fig_height

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
        #with warnings.catch_warnings():
        #    warnings.simplefilter('ignore')
        #    self._fig.savefig(
        #        fname, dpi=dpi, bbox_inches=bbox, format=ftype, pad_inches=0
        #    )
        self._fig.savefig(
            fname, dpi=dpi, bbox='tight', format=ftype
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
