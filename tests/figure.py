# figure.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0411,C0413,E0611,E1129,F0401,R0201,W0212,W0621

# Standard library imports
from __future__ import print_function
import os
import sys
if sys.hexversion >= 0x03000000:
    import unittest.mock as mock
# PyPI imports
import numpy
import pytest
if sys.hexversion < 0x03000000:
    import mock
import pmisc
from pmisc import AI, AE, AROPROP, RE
import matplotlib
# Intra-package imports
import pplot
from .fixtures import compare_image_set
from .functions import comp_num
sys.path.append('..')
from tests.gen_ref_images import unittest_figure_images


###
# Global variables
###
FOBJ = pplot.Figure
MVER = int(matplotlib.__version__.split('.')[0])


###
# Test classes
###
class TestFigure(object):
    """ Tests for Figure class """
    # pylint: disable=R0903,R0904,W0232
    ### Private methods
    def test_complete(self, default_panel):
        """ Test _complete property behavior """
        obj = pplot.Figure(panels=None)
        assert not obj._complete
        obj.panels = default_panel
        assert obj._complete

    @pytest.mark.figure
    def test_complete_exceptions(self):
        """ Test _complete property exceptions """
        obj = pplot.Figure(panels=None)
        AE(obj.show, RE, 'Figure object is not fully specified')

    def test_iter(self, default_panel):
        """ Test __iter__ method behavior """
        ds1_obj = pplot.BasicSource(
            indep_var=numpy.array([100, 200, 300, 400]),
            dep_var=numpy.array([1, 2, 3, 4])
        )
        series1_obj = pplot.Series(
            data_source=ds1_obj, label='series 1', interp=None
        )
        panel2 = pplot.Panel(series=series1_obj)
        obj = pplot.Figure(panels=[default_panel, panel2])
        for num, panel in enumerate(obj):
            if num == 0:
                assert panel == default_panel
            if num == 1:
                assert panel == panel2

    def test_nonzero(self, default_panel):
        """ Test __nonzero__ method behavior """
        obj = pplot.Figure()
        assert not obj
        obj = pplot.Figure(panels=default_panel)
        assert obj
        obj = pplot.Figure(panels=2*[default_panel])
        assert obj

    def test_str(self, default_panel):
        """ Test __str__ method behavior """
        obj = pplot.Figure(panels=None)
        ret = (
            'Panels: None\n'
            'Independent variable label: not specified\n'
            'Independent variable units: not specified\n'
            'Logarithmic independent axis: False\n'
            'Title: not specified\n'
            'Figure width: None\n'
            'Figure height: None\n'
        )
        assert str(obj) == ret
        obj = pplot.Figure(
            panels=default_panel,
            indep_var_label='Input',
            indep_var_units='Amps',
            title='My graph'
        )
        ref = (
            'Panel 0:\n'
            '   Series 0:\n'
            '      Independent variable: [ 5.0, 6.0, 7.0, 8.0 ]\n'
            '      Dependent variable: [ 0.0, -10.0, 5.0, 4.0 ]\n'
            '      Label: test series\n'
            '      Color: k\n'
            '      Marker: o\n'
            '      Interpolation: CUBIC\n'
            '      Line style: -\n'
            '      Secondary axis: False\n'
            '   Primary axis label: Primary axis\n'
            '   Primary axis units: A\n'
            '   Secondary axis label: Secondary axis\n'
            '   Secondary axis units: B\n'
            '   Logarithmic dependent axis: False\n'
            '   Display independent axis: False\n'
            '   Legend properties:\n'
            '      cols: 1\n'
            '      pos: BEST\n'
            'Independent variable label: Input\n'
            'Independent variable units: Amps\n'
            'Logarithmic independent axis: False\n'
            'Title: My graph\n'
            'Figure width: (6\\.08|6\\.71|6\\.67|\\.74).*\n'
            'Figure height: (4.99|5.06).*\n'
        )
        actual = str(obj)
        ref_invariant = '\n'.join(ref.split('\n')[:-3])
        actual_invariant = '\n'.join(actual.split('\n')[:-3])
        assert ref_invariant == actual_invariant
        act_width = float(actual.split('\n')[-3][14:])
        act_height = float(actual.split('\n')[-2][15:])
        ref_widths = [6.08, 6.71, 6.67, 6.74, 6.75]
        ref_heights = [4.99, 5.06]
        if act_width not in ref_widths:
            assert False, '{0} not in {1}'.format(act_width, ref_widths)
        if act_height not in ref_heights:
            assert False, '{0} not in {1}'.format(act_height, ref_heights)

    ### Public methods
    def test_save(self, default_panel):
        """ Test save method behavior """
        obj = pplot.Figure(
            panels=default_panel
        )
        with pmisc.TmpFile() as fname:
            obj.save(fname=fname, ftype='PNG')
        with pmisc.TmpFile() as fname:
            obj.save(fname=fname, ftype='EPS')
        # Test extension handling
        # No exception
        fname = os.path.join(os.path.dirname(__file__), 'test_file1')
        obj.save(fname, ftype='PNG')
        fref = '{fname}.png'.format(fname=fname)
        assert os.path.exists(fref)
        with pmisc.ignored(OSError):
            os.remove(fref)
        # No exception but trailing period
        fname = os.path.join(os.path.dirname(__file__), 'test_file2.')
        obj.save(fname, ftype='EPS')
        fref = '{fname}.eps'.format(
            fname=os.path.join(os.path.dirname(__file__), 'test_file2')
        )
        assert os.path.exists(fref)
        with pmisc.ignored(OSError):
            os.remove(fref)
        # Extension given, overrides file format
        fname = os.path.join(os.path.dirname(__file__), 'test_file3.ext')
        obj.save(fname, ftype='EPS')
        fref = fname
        assert os.path.exists(fref)
        with pmisc.ignored(OSError):
            os.remove(fref)

    @pytest.mark.figure
    def test_save_exceptions(self, default_panel):
        """ Test save method exceptions """
        obj = pplot.Figure(panels=default_panel)
        for item in [3, 'test\0']:
            AI(obj.save, 'fname', fname=item)
        AI(obj.save, 'ftype', 'myfile', 5)
        AE(obj.save, RE, 'Unsupported file type: bmp', 'myfile', ftype='bmp')

    def test_show(self, default_panel, capsys):
        """ Test that show method behavior """
        def mock_show():
            print('show called')
        obj = pplot.Figure(panels=default_panel)
        with mock.patch('pplot.figure.plt.show', side_effect=mock_show):
            obj.show()
        out, _ = capsys.readouterr()
        assert out == 'show called\n'

    ### Properties
    def test_axes_list(self, default_panel):
        """ Test axes_list property behavior """
        obj = pplot.Figure(panels=None)
        assert obj.axes_list == list()
        obj = pplot.Figure(panels=default_panel)
        comp_list = list()
        for num, axis_dict in enumerate(obj.axes_list):
            if ((axis_dict['number'] == num) and
               ((axis_dict['primary'] is None) or
               (isinstance(axis_dict['primary'], matplotlib.axes.Axes))) and
               ((axis_dict['secondary'] is None) or
               (isinstance(axis_dict['secondary'], matplotlib.axes.Axes)))):
                comp_list.append(True)
        assert comp_list == len(obj.axes_list)*[True]

    def test_fig(self, default_panel):
        """ Test fig property behavior """
        obj = pplot.Figure(panels=None)
        assert obj.fig is None
        obj = pplot.Figure(panels=default_panel)
        assert isinstance(obj.fig, matplotlib.figure.Figure)

    def test_fig_width(self, default_panel):
        """ Test figure width attributes """
        obj = pplot.Figure(panels=None)
        assert obj.fig_width is None
        obj = pplot.Figure(panels=default_panel)
        comp_num(obj.fig_width, [6.08, 6.71] if MVER == 1 else [6.74, 6.75])
        obj.fig_width = 5
        assert obj.fig_width == 5

    @pytest.mark.figure
    def test_fig_width_exceptions(self, default_panel):
        """ Test figure width property exceptions """
        AI(FOBJ, 'fig_width', panels=default_panel, fig_width='a')

    def test_fig_height(self, default_panel):
        """ Test figure height property behavior """
        obj = pplot.Figure(panels=None)
        assert obj.fig_height is None
        obj = pplot.Figure(panels=default_panel)
        comp_num(obj.fig_height, 4.31 if MVER == 1 else 4.37)
        obj.fig_height = 5
        assert obj.fig_height == 5

    @pytest.mark.figure
    def test_fig_height_exceptions(self, default_panel):
        """ Test figure height property exceptions """
        AI(FOBJ, 'fig_height', panels=default_panel, fig_height='a')

    def test_indep_axis_scale(self, default_panel):
        """ Test indep_axis_scale property """
        obj = pplot.Figure(panels=None)
        assert obj.indep_axis_scale is None
        obj = pplot.Figure(panels=default_panel)
        assert obj.indep_axis_scale == 1

    def test_indep_axis_ticks(self, default_panel):
        """ Test indep_axis_ticks property behavior """
        obj = pplot.Figure(
            panels=default_panel,
            indep_axis_ticks=[1000, 2000, 3000, 3500]
        )
        assert obj.indep_axis_ticks == [1.0, 2.0, 3.0, 3.5]
        obj = pplot.Figure(
            panels=default_panel,
            indep_axis_ticks=numpy.array([1E6, 2E6, 3E6, 3.5E6])
        )
        assert obj.indep_axis_ticks == [1.0, 2.0, 3.0, 3.5]
        # Logarithmic independent axis tick marks
        # cannot be overridden
        obj = pplot.Figure(
            panels=default_panel,
            log_indep_axis=True,
            indep_axis_ticks=numpy.array([1E6, 2E6, 3E6, 3.5E6])
        )
        assert obj.indep_axis_ticks == [1.0, 10.0]

    @pytest.mark.figure
    def test_indep_axis_ticks_exceptions(self, default_panel):
        """ Test indep_axis_ticks exceptions """
        obj = pplot.Figure(panels=None)
        assert obj.indep_axis_ticks is None
        AI(FOBJ, 'indep_axis_ticks', default_panel, indep_axis_ticks=5)

    def test_indep_var_label(self, default_panel):
        """ Test indep_var_label property behavior """
        pplot.Figure(panels=default_panel, indep_var_label=None)
        pplot.Figure(panels=default_panel, indep_var_label='sec')
        obj = pplot.Figure(panels=default_panel, indep_var_label='test')
        assert obj.indep_var_label == 'test'

    @pytest.mark.figure
    def test_indep_var_label_exceptions(self, default_panel):
        """ Test indep_var_label property exceptions """
        AI(FOBJ, 'indep_var_label', default_panel, indep_var_label=5)

    def test_indep_var_units(self, default_panel):
        """ Test indep_var_units property behavior """
        pplot.Figure(panels=default_panel, indep_var_units=None)
        pplot.Figure(panels=default_panel, indep_var_units='sec')
        obj = pplot.Figure(panels=default_panel, indep_var_units='test')
        assert obj.indep_var_units == 'test'

    @pytest.mark.figure
    def test_indep_var_units_exceptions(self, default_panel):
        """ Test indep_var_units exceptions """
        AI(FOBJ, 'indep_var_units', default_panel, indep_var_units=5)

    def test_log_indep_axis(self, default_panel):
        """ Test log_indep_axis property behavior """
        obj = pplot.Figure(panels=default_panel, log_indep_axis=False)
        assert not obj.log_indep_axis
        obj = pplot.Figure(panels=default_panel, log_indep_axis=True)
        assert obj.log_indep_axis
        obj = pplot.Figure(panels=default_panel)
        assert not obj.log_indep_axis

    @pytest.mark.figure
    def test_log_indep_axis_exceptions(self, default_panel):
        """ Test log_indep_axis property exceptions """
        AI(FOBJ, 'log_indep_axis', default_panel, log_indep_axis=5)
        negative_data_source = pplot.BasicSource(
            indep_var=numpy.array([-5, 6, 7, 8]),
            dep_var=numpy.array([0.1, 10, 5, 4])
        )
        negative_series = pplot.Series(
            data_source=negative_data_source, label='negative data series'
        )
        negative_panel = pplot.Panel(series=negative_series)
        exmsg = (
            'Figure cannot be plotted with a logarithmic independent '
            'axis because panel 0, series 0 contains negative independent '
            'data points'
        )
        AE(FOBJ, ValueError, exmsg, negative_panel, log_indep_axis=True)

    def test_panels(self, default_panel):
        """ Test panel property behavior """
        pplot.Figure(panels=None)
        pplot.Figure(panels=default_panel)

    @pytest.mark.figure
    def test_panels_exceptions(self, default_panel):
        """ Test panel property exceptions """
        AI(FOBJ, 'panels', 5)
        exmsg = 'Panel 1 is not fully specified'
        panels = [default_panel, pplot.Panel(series=None)]
        AE(FOBJ, TypeError, exmsg, panels)

    def test_title(self, default_panel):
        """ Test title property behavior """
        pplot.Figure(panels=default_panel, title=None)
        pplot.Figure(panels=default_panel, title='sec')
        obj = pplot.Figure(panels=default_panel, title='test')
        assert obj.title == 'test'

    @pytest.mark.figure
    def test_title_exceptions(self, default_panel):
        """ Test title property exceptions """
        AI(FOBJ, 'title', default_panel, title=5)

    ### Miscellaneous
    @pytest.mark.figure
    def test_specified_figure_size_too_small_exceptions(self, default_panel):
        """ Test requested figure size is too small behavior """
        # Continuous integration image is 5.61in wide
        exmsg = (
            'Figure size is too small: minimum width [5.6[1]|6.2]*, '
            'minimum height 2.6[6|8]'
        )
        kwargs = dict(title='My graph', fig_width=0.1, fig_height=200)
        AE(FOBJ, RE, exmsg, default_panel, 'Input', 'Amps', **kwargs)
        kwargs = dict(title='My graph', fig_width=200, fig_height=0.1)
        AE(FOBJ, RE, exmsg, default_panel, 'Input', 'Amps', **kwargs)
        kwargs = dict(title='My graph', fig_width=0.1, fig_height=0.1)
        AE(FOBJ, RE, exmsg, default_panel, 'Input', 'Amps', **kwargs)

    @pytest.mark.figure
    def test_cannot_delete_attributes_exceptions(self, default_panel):
        """
        Test that del method raises an exception on all class attributes
        """
        obj = pplot.Figure(panels=default_panel)
        props = [
            'axes_list',
            'fig',
            'fig_height',
            'fig_width',
            'indep_axis_scale',
            'indep_var_label',
            'indep_var_units',
            'log_indep_axis',
            'panels',
            'title'
        ]
        for prop in props:
            AROPROP(obj, prop)

    def test_images(self, tmpdir):
        """ Compare images to verify correct plotting of figure """
        tmpdir.mkdir('test_images')
        images_dict_list = unittest_figure_images(
            mode='test', test_dir=str(tmpdir)
        )
        assert compare_image_set(tmpdir, images_dict_list, 'figure')
