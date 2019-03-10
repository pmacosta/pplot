# figure.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0411,C0413,E0611,E1129,F0401
# pylint: disable=R0201,R0205,R0913,R0914,W0104,W0212,W0611,W0621

# Standard library imports
from __future__ import print_function
import os
import sys

if sys.hexversion >= 0x03000000:
    import unittest.mock as mock
# PyPI imports
import numpy as np
import pytest

if sys.hexversion < 0x03000000:
    import mock
import pmisc
from pmisc import AI, AE, AROPROP, GET_EXMSG, RE
import matplotlib as mpl

# Intra-package imports
import pplot
from .fixtures import compare_image_set, ref_panels, ref_size_series
from .functions import comp_num, PseudoTmpFile

sys.path.append("..")
from tests.gen_ref_images import (
    create_axis_display_images,
    create_basic_figure_image,
    create_sizing_image,
)


###
# Global variables
###
DPI = 100
FOBJ = pplot.Figure
MVER = int(mpl.__version__.split(".")[0])


###
# Test classes
###
class TestFigure(object):
    """Test for Figure class."""

    # pylint: disable=R0903,R0904,W0232
    ### Private methods
    def test_complete(self, default_panel):
        """Test _complete property behavior."""
        obj = pplot.Figure(panels=None)
        assert not obj._complete
        obj.panels = default_panel
        assert obj._complete

    @pytest.mark.figure
    def test_complete_exceptions(self):
        """Test _complete property exceptions."""
        obj = pplot.Figure(panels=None)
        AE(obj.show, RE, "Figure object is not fully specified")

    def test_iter(self, default_panel):
        """Test __iter__ method behavior."""
        ds1_obj = pplot.BasicSource(
            indep_var=np.array([100, 200, 300, 400]), dep_var=np.array([1, 2, 3, 4])
        )
        series1_obj = pplot.Series(data_source=ds1_obj, label="series 1", interp=None)
        panel2 = pplot.Panel(series=series1_obj)
        obj = pplot.Figure(panels=[default_panel, panel2])
        for num, panel in enumerate(obj):
            if num == 0:
                assert panel == default_panel
            if num == 1:
                assert panel == panel2

    def test_nonzero(self, default_panel):
        """Test __nonzero__ method behavior."""
        obj = pplot.Figure()
        assert not obj
        obj = pplot.Figure(panels=default_panel)
        assert obj
        obj = pplot.Figure(panels=2 * [default_panel])
        assert obj

    def test_str(self, default_panel):
        """Test __str__ method behavior."""
        obj = pplot.Figure(panels=None)
        ret = (
            "Panels: None\n"
            "Independent variable label: not specified\n"
            "Independent variable units: not specified\n"
            "Logarithmic independent axis: False\n"
            "Title: not specified\n"
            "Figure width: None\n"
            "Figure height: None\n"
        )
        assert str(obj) == ret
        obj = pplot.Figure(
            panels=default_panel,
            indep_var_label="Input",
            indep_var_units="Amps",
            title="My graph",
        )
        ref = (
            "Panel 0:\n"
            "   Series 0:\n"
            "      Independent variable: [ 5.0, 6.0, 7.0, 8.0 ]\n"
            "      Dependent variable: [ 0.0, -10.0, 5.0, 4.0 ]\n"
            "      Label: test series\n"
            "      Color: k\n"
            "      Marker: o\n"
            "      Interpolation: CUBIC\n"
            "      Line style: -\n"
            "      Secondary axis: False\n"
            "   Primary axis label: Primary axis\n"
            "   Primary axis units: A\n"
            "   Secondary axis label: Secondary axis\n"
            "   Secondary axis units: B\n"
            "   Logarithmic dependent axis: False\n"
            "   Display independent axis: True\n"
            "   Legend properties:\n"
            "      cols: 1\n"
            "      pos: BEST\n"
            "Independent variable label: Input\n"
            "Independent variable units: Amps\n"
            "Logarithmic independent axis: False\n"
            "Title: My graph\n"
            "Figure width: (6\\.08|6\\.55|6\\.71|6\\.67|\\.74).*\n"
            "Figure height: (3\\.61|3\\.89||4\\.99|5\\.06|5\\.29).*\n"
        )
        actual = str(obj)
        ref_invariant = "\n".join(ref.split("\n")[:-3])
        actual_invariant = "\n".join(actual.split("\n")[:-3])
        assert ref_invariant == actual_invariant
        act_width = float(actual.split("\n")[-3][14:])
        act_height = float(actual.split("\n")[-2][15:])
        ref_widths = [6.08, 6.4, 6.54, 6.55, 6.71, 6.67, 6.74, 6.75]
        ref_heights = [3.71, 3.84, 4.8, 4.905, 4.9125, 4.99, 5.06, 5.29]
        comp_num(act_width, ref_widths)
        comp_num(act_height, ref_heights)

    @pytest.mark.figure
    def test_str_exceptions(self, default_panel, negative_panel):
        """Test figure __str__ method exceptions."""
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        obj = pplot.Figure(log_indep_axis=True)
        obj.panels = negative_panel
        with pytest.raises(ValueError) as excinfo:
            str(obj)
        assert GET_EXMSG(excinfo) == exmsg
        exmsg = "Number of tick locations and number of tick labels mismatch"
        obj = pplot.Figure()
        # Order of assignment of indep_axis_tick_labels and panels is important
        # in order to raise desired exception when save method is called
        obj.indep_axis_tick_labels = []
        obj.panels = default_panel
        with pytest.raises(RuntimeError) as excinfo:
            str(obj)
        assert GET_EXMSG(excinfo) == exmsg

    ### Public methods
    def test_save(self, default_panel):
        """Test save method behavior."""
        obj = pplot.Figure(panels=default_panel)
        with PseudoTmpFile(ext="png") as fname:
            obj.save(fname=fname, ftype="PNG")
        with PseudoTmpFile(ext="eps") as fname:
            obj.save(fname=fname, ftype="EPS")
        with PseudoTmpFile(ext="pdf") as fname:
            obj.save(fname=fname, ftype="PDF")
        # Test extension handling
        # No exception
        fname = os.path.join(os.path.dirname(__file__), "test_file1")
        with PseudoTmpFile(fname=fname) as fname:
            obj.save(fname, ftype="PNG")
            fref = "{fname}.png".format(fname=fname)
            assert os.path.exists(fref)
        # No exception but trailing period
        fname = os.path.join(os.path.dirname(__file__), "test_file2.")
        with PseudoTmpFile(fname=fname) as fname:
            obj.save(fname, ftype="EPS")
            fref = "{fname}.eps".format(
                fname=os.path.join(os.path.dirname(__file__), "test_file2")
            )
            assert os.path.exists(fref)

    @pytest.mark.figure
    def test_save_exceptions(self, default_panel, negative_panel):
        """Test save method exceptions."""
        obj = pplot.Figure(panels=default_panel)
        for item in [3, "test\0"]:
            AI(obj.save, "fname", fname=item)
        AI(obj.save, "ftype", "myfile", 5)
        AE(obj.save, RE, "Unsupported file type: bmp", "myfile", "bmp")
        AE(obj.save, RE, "Could not determine file type", "myfile")
        exmsg = "Incongruent file type and file extension"
        AE(obj.save, RE, exmsg, "myfile.png", "pdf")
        obj = pplot.Figure(panels=None)
        exmsg = "Figure object is not fully specified"
        AE(obj.save, RE, exmsg, "myfile.png")
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        obj = pplot.Figure(log_indep_axis=True)
        obj.panels = negative_panel
        AE(obj.save, ValueError, exmsg, "myfile.png")
        exmsg = "Number of tick locations and number of tick labels mismatch"
        obj = pplot.Figure()
        # Order of assignment of indep_axis_tick_labels and panels is important
        # in order to raise desired exception when save method is called
        obj.indep_axis_tick_labels = []
        obj.panels = default_panel
        AE(obj.save, RE, exmsg, "myfile.png")

    def test_show(self, default_panel, capsys):  # noqa:D202
        """Test that show method behavior."""

        def mock_show():
            print("show called")

        obj = pplot.Figure(panels=default_panel)
        with mock.patch("pplot.figure.plt.show", side_effect=mock_show):
            obj.show()
        out, _ = capsys.readouterr()
        assert out == "show called\n"

    @pytest.mark.figure
    def test_show_exceptions(self, default_panel, negative_panel):
        """Test show method exceptions."""
        obj = pplot.Figure(panels=None)
        exmsg = "Figure object is not fully specified"
        AE(obj.show, RE, exmsg)
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        obj = pplot.Figure(log_indep_axis=True)
        obj.panels = negative_panel
        AE(obj.show, ValueError, exmsg)
        exmsg = "Number of tick locations and number of tick labels mismatch"
        obj = pplot.Figure()
        # Order of assignment of indep_axis_tick_labels and panels is important
        # in order to raise desired exception when save method is called
        obj.indep_axis_tick_labels = []
        obj.panels = default_panel
        AE(obj.show, RE, exmsg)

    ### Properties
    def test_axes_list(self, default_panel):
        """Test axes_list property behavior."""
        obj = pplot.Figure(panels=None)
        assert obj.axes_list == list()
        obj = pplot.Figure(panels=default_panel)
        comp_list = list()
        for num, axis_dict in enumerate(obj.axes_list):
            if (
                (axis_dict["number"] == num)
                and (
                    (axis_dict["primary"] is None)
                    or (isinstance(axis_dict["primary"], mpl.axes.Axes))
                )
                and (
                    (axis_dict["secondary"] is None)
                    or (isinstance(axis_dict["secondary"], mpl.axes.Axes))
                )
            ):
                comp_list.append(True)
        assert comp_list == len(obj.axes_list) * [True]

    @pytest.mark.figure
    def test_axes_list_exceptions(self, default_panel, negative_panel):
        """Test figure axes_list property exceptions."""
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        obj = pplot.Figure(log_indep_axis=True)
        obj.panels = negative_panel
        with pytest.raises(ValueError) as excinfo:
            obj.axes_list
        assert GET_EXMSG(excinfo) == exmsg
        exmsg = "Number of tick locations and number of tick labels mismatch"
        obj = pplot.Figure()
        # Order of assignment of indep_axis_tick_labels and panels is important
        # in order to raise desired exception when save method is called
        obj.indep_axis_tick_labels = []
        obj.panels = default_panel
        with pytest.raises(RuntimeError) as excinfo:
            obj.axes_list
        assert GET_EXMSG(excinfo) == exmsg

    def test_fig(self, default_panel):
        """Test fig property behavior."""
        obj = pplot.Figure(panels=None)
        assert obj.fig is None
        obj = pplot.Figure(panels=default_panel)
        assert isinstance(obj.fig, mpl.figure.Figure)

    @pytest.mark.figure
    def test_fig_exceptions(self, default_panel, negative_panel):
        """Test figure fig property exceptions."""
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        obj = pplot.Figure(log_indep_axis=True)
        obj.panels = negative_panel
        with pytest.raises(ValueError) as excinfo:
            obj.fig
        assert GET_EXMSG(excinfo) == exmsg
        exmsg = "Number of tick locations and number of tick labels mismatch"
        obj = pplot.Figure()
        # Order of assignment of indep_axis_tick_labels and panels is important
        # in order to raise desired exception when save method is called
        obj.indep_axis_tick_labels = []
        obj.panels = default_panel
        with pytest.raises(RuntimeError) as excinfo:
            obj.fig
        assert GET_EXMSG(excinfo) == exmsg

    def test_fig_width(self, default_panel):
        """Test figure width attributes."""
        obj = pplot.Figure(panels=None)
        assert obj.fig_width is None
        obj = pplot.Figure(panels=default_panel)
        comp_num(
            obj.fig_width, [6.08, 6.71] if MVER == 1 else [6.4, 6.54, 6.55, 6.74, 6.75]
        )
        obj.fig_width = 7
        assert obj.fig_width == 7

    @pytest.mark.figure
    def test_fig_width_exceptions(self, default_panel, negative_panel):
        """Test figure width property exceptions."""
        AI(FOBJ, "fig_width", panels=default_panel, fig_width="a")
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        obj = pplot.Figure(log_indep_axis=True)
        obj.panels = negative_panel
        with pytest.raises(ValueError) as excinfo:
            obj.fig_width = 10
        assert GET_EXMSG(excinfo) == exmsg
        exmsg = "Number of tick locations and number of tick labels mismatch"
        obj = pplot.Figure()
        # Order of assignment of indep_axis_tick_labels and panels is important
        # in order to raise desired exception when save method is called
        obj.indep_axis_tick_labels = []
        obj.panels = default_panel
        with pytest.raises(RuntimeError) as excinfo:
            obj.fig_width = 10
        assert GET_EXMSG(excinfo) == exmsg

    def test_fig_height(self, default_panel):
        """Test figure height property behavior."""
        obj = pplot.Figure(panels=None)
        assert obj.fig_height is None
        obj = pplot.Figure(panels=default_panel)
        comp_num(obj.fig_height, 4.31 if MVER == 1 else [3.6])
        obj.fig_height = 5
        assert obj.fig_height == 5

    @pytest.mark.figure
    def test_fig_height_exceptions(self, default_panel, negative_panel):
        """Test figure height property exceptions."""
        AI(FOBJ, "fig_height", panels=default_panel, fig_height="a")
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        obj = pplot.Figure(log_indep_axis=True)
        obj.panels = negative_panel
        with pytest.raises(ValueError) as excinfo:
            obj.fig_height = 10
        assert GET_EXMSG(excinfo) == exmsg
        exmsg = "Number of tick locations and number of tick labels mismatch"
        obj = pplot.Figure()
        # Order of assignment of indep_axis_tick_labels and panels is important
        # in order to raise desired exception when save method is called
        obj.indep_axis_tick_labels = []
        obj.panels = default_panel
        with pytest.raises(RuntimeError) as excinfo:
            obj.fig_height = 10
        assert GET_EXMSG(excinfo) == exmsg

    def test_indep_axis_scale(self, default_panel):
        """Test indep_axis_scale property."""
        obj = pplot.Figure(panels=None)
        assert obj.indep_axis_scale is None
        obj = pplot.Figure(panels=default_panel)
        assert obj.indep_axis_scale == 1

    @pytest.mark.figure
    def test_indep_axis_scale_exceptions(self, default_panel, negative_panel):  # noqa
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        obj = pplot.Figure(log_indep_axis=True)
        obj.panels = negative_panel
        with pytest.raises(ValueError) as excinfo:
            obj.indep_axis_scale
        assert GET_EXMSG(excinfo) == exmsg
        exmsg = "Number of tick locations and number of tick labels mismatch"
        obj = pplot.Figure()
        # Order of assignment of indep_axis_tick_labels and panels is important
        # in order to raise desired exception when save method is called
        obj.indep_axis_tick_labels = []
        obj.panels = default_panel
        with pytest.raises(RuntimeError) as excinfo:
            obj.indep_axis_scale
        assert GET_EXMSG(excinfo) == exmsg

    def test_indep_axis_ticks(self, default_panel):
        """Test indep_axis_ticks property behavior."""
        obj = pplot.Figure(
            panels=default_panel, indep_axis_ticks=np.array([1000, 2000, 3000, 3500])
        )
        assert (obj.indep_axis_ticks == np.array([1.0, 2.0, 3.0, 3.5])).all()
        obj = pplot.Figure(
            panels=default_panel, indep_axis_ticks=np.array([1e6, 2e6, 3e6, 3.5e6])
        )
        assert obj.indep_axis_ticks == [1.0, 2.0, 3.0, 3.5]
        # Logarithmic independent axis tick marks
        # cannot be overridden
        obj = pplot.Figure(
            panels=default_panel,
            log_indep_axis=True,
            indep_axis_ticks=np.array([1e6, 2e6, 3e6, 3.5e6]),
        )
        assert obj.indep_axis_ticks == [1.0, 10.0]

    @pytest.mark.figure
    def test_indep_axis_ticks_exceptions(self, default_panel, negative_panel):
        """Test indep_axis_ticks exceptions."""
        obj = pplot.Figure(panels=None)
        assert obj.indep_axis_ticks is None
        AI(FOBJ, "indep_axis_ticks", default_panel, indep_axis_ticks=5)
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        obj = pplot.Figure(log_indep_axis=True)
        obj.panels = negative_panel
        with pytest.raises(ValueError) as excinfo:
            obj.indep_axis_ticks
        assert GET_EXMSG(excinfo) == exmsg
        exmsg = "Number of tick locations and number of tick labels mismatch"
        obj = pplot.Figure()
        # Order of assignment of indep_axis_tick_labels and panels is
        # important in order to raise desired exception when save method is
        # called
        obj.indep_axis_tick_labels = []
        obj.panels = default_panel
        with pytest.raises(RuntimeError) as excinfo:
            obj.indep_axis_ticks
        assert GET_EXMSG(excinfo) == exmsg

    def test_indep_axis_tick_labels(self, default_panel):
        """Test indep_axis_tick_labels property behavior."""
        obj = pplot.Figure(
            panels=default_panel,
            indep_axis_ticks=np.array([1000, 2000, 3000, 3500]),
            indep_axis_tick_labels=["a", "b", "c", "d"],
        )
        assert obj.indep_axis_tick_labels == ["a", "b", "c", "d"]
        obj = pplot.Figure(
            panels=default_panel, indep_axis_ticks=np.array([1000, 2000, 3000, 3500])
        )
        assert obj.indep_axis_tick_labels == ["1.0", "2.0", "3.0", "3.5"]

    @pytest.mark.figure
    def test_indep_axis_tick_labels_exceptions(self, default_panel, negative_panel):
        """Test indep_axis_tick_labels property exceptions."""
        AI(
            FOBJ,
            "indep_axis_tick_labels",
            panels=default_panel,
            indep_axis_tick_labels="a",
        )
        AI(
            FOBJ,
            "indep_axis_tick_labels",
            panels=default_panel,
            indep_axis_tick_labels=[1, 2, 3],
        )
        exmsg = "Number of tick locations and number of tick labels mismatch"
        AE(FOBJ, RE, exmsg, panels=default_panel, indep_axis_tick_labels=[])
        AE(FOBJ, RE, exmsg, panels=default_panel, indep_axis_tick_labels=["a"])
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        obj = pplot.Figure(log_indep_axis=True)
        obj.panels = negative_panel
        with pytest.raises(ValueError) as excinfo:
            obj.indep_axis_tick_labels
        assert GET_EXMSG(excinfo) == exmsg
        exmsg = "Number of tick locations and number of tick labels mismatch"
        for flag in [True, False]:
            obj = pplot.Figure()
            # Order of assignment of indep_axis_tick_labels and panels is
            # important in order to raise desired exception when save method is
            # called
            obj.indep_axis_tick_labels = []
            obj.panels = default_panel
            if flag:
                with pytest.raises(RuntimeError) as excinfo:
                    obj.indep_axis_tick_labels
            else:
                with pytest.raises(RuntimeError) as excinfo:
                    obj.indep_axis_tick_labels = ["1", "2", "3"]
            assert GET_EXMSG(excinfo) == exmsg

    def test_indep_var_label(self, default_panel):
        """Test indep_var_label property behavior."""
        pplot.Figure(panels=default_panel, indep_var_label=None)
        pplot.Figure(panels=default_panel, indep_var_label="sec")
        obj = pplot.Figure(panels=default_panel, indep_var_label="test")
        assert obj.indep_var_label == "test"

    @pytest.mark.figure
    def test_indep_var_label_exceptions(self, default_panel):
        """Test indep_var_label property exceptions."""
        AI(FOBJ, "indep_var_label", default_panel, indep_var_label=5)

    def test_indep_var_units(self, default_panel):
        """Test indep_var_units property behavior."""
        pplot.Figure(panels=default_panel, indep_var_units=None)
        pplot.Figure(panels=default_panel, indep_var_units="sec")
        obj = pplot.Figure(panels=default_panel, indep_var_units="test")
        assert obj.indep_var_units == "test"

    @pytest.mark.figure
    def test_indep_var_units_exceptions(self, default_panel):
        """Test indep_var_units exceptions."""
        AI(FOBJ, "indep_var_units", default_panel, indep_var_units=5)

    def test_log_indep_axis(self, default_panel):
        """Test log_indep_axis property behavior."""
        obj = pplot.Figure(panels=default_panel, log_indep_axis=False)
        assert not obj.log_indep_axis
        obj = pplot.Figure(panels=default_panel, log_indep_axis=True)
        assert obj.log_indep_axis
        obj = pplot.Figure(panels=default_panel)
        assert not obj.log_indep_axis

    @pytest.mark.figure
    def test_log_indep_axis_exceptions(self, default_panel, negative_panel):
        """Test log_indep_axis property exceptions."""
        AI(FOBJ, "log_indep_axis", default_panel, log_indep_axis=5)
        exmsg = (
            "Figure cannot be plotted with a logarithmic independent "
            "axis because panel 0, series 0 contains negative independent "
            "data points"
        )
        AE(FOBJ, ValueError, exmsg, negative_panel, log_indep_axis=True)

    def test_panels(self, default_panel):
        """Test panel property behavior."""
        pplot.Figure(panels=None)
        pplot.Figure(panels=default_panel)

    @pytest.mark.figure
    def test_panels_exceptions(self, default_panel):
        """Test panel property exceptions."""
        AI(FOBJ, "panels", 5)
        exmsg = "Panel 1 is not fully specified"
        panels = [default_panel, pplot.Panel(series=None)]
        AE(FOBJ, TypeError, exmsg, panels)

    def test_title(self, default_panel):
        """Test title property behavior."""
        pplot.Figure(panels=default_panel, title=None)
        pplot.Figure(panels=default_panel, title="sec")
        obj = pplot.Figure(panels=default_panel, title="test")
        assert obj.title == "test"

    @pytest.mark.figure
    def test_title_exceptions(self, default_panel):
        """Test title property exceptions."""
        AI(FOBJ, "title", default_panel, title=5)

    ### Miscellaneous
    @pytest.mark.figure
    def test_specified_figure_size_too_small_exceptions(self, default_panel):
        """Test requested figure size is too small behavior."""
        # Continuous integration image is 5.61in wide
        exmsg = (
            "Figure size is too small: minimum width [6.55|6.54]*, "
            "minimum height [3.84].*"
        )
        kwargs = dict(title="My graph", fig_width=0.1, fig_height=200)
        AE(FOBJ, RE, exmsg, default_panel, "Input", "Amps", **kwargs)
        kwargs = dict(title="My graph", fig_width=200, fig_height=0.1)
        AE(FOBJ, RE, exmsg, default_panel, "Input", "Amps", **kwargs)
        kwargs = dict(title="My graph", fig_width=0.1, fig_height=0.1)
        AE(FOBJ, RE, exmsg, default_panel, "Input", "Amps", **kwargs)

    @pytest.mark.figure
    def test_cannot_delete_attributes_exceptions(self, default_panel):
        """Test that del method raises an exception on all class attributes."""
        obj = pplot.Figure(panels=default_panel)
        props = [
            "axes_list",
            "fig",
            "fig_height",
            "fig_width",
            "indep_axis_scale",
            "indep_var_label",
            "indep_var_units",
            "log_indep_axis",
            "panels",
            "title",
        ]
        for prop in props:
            AROPROP(obj, prop)

    ### Functional
    @pytest.mark.parametrize("display_indep_axis1", ["no", "yes"])
    @pytest.mark.parametrize("display_indep_axis2", ["no", "yes"])
    @pytest.mark.parametrize("display_indep_axis4", ["no", "yes"])
    def test_axis_display(
        self,
        display_indep_axis1,
        display_indep_axis2,
        display_indep_axis4,
        tmpdir,
        ref_panels,
    ):
        """Compare multi-panel images with independent axis shown in many or none."""
        tmpdir.mkdir("test_images")
        olist = []
        mode = "test"
        test_dir = str(tmpdir)
        create_axis_display_images(
            mode,
            test_dir,
            ref_panels,
            display_indep_axis1,
            display_indep_axis2,
            display_indep_axis4,
            olist,
            False,
        )
        assert compare_image_set(tmpdir, olist, "figure")

    def test_basic_figure(self, tmpdir):
        """Test figure without anything but tick marks and series without given size."""
        tmpdir.mkdir("test_images")
        olist = []
        mode = "test"
        test_dir = str(tmpdir)
        create_basic_figure_image(mode, test_dir, olist, False)
        assert compare_image_set(tmpdir, olist, "figure")

    @pytest.mark.parametrize("tlength", ["short", "long", "no"])
    @pytest.mark.parametrize("ilength", ["short", "long", "no"])
    @pytest.mark.parametrize("itype", ["linear", "log"])
    @pytest.mark.parametrize("plength", ["short", "long", "no"])
    @pytest.mark.parametrize("slength", ["short", "long", "no"])
    def test_min_sizing(
        self, tlength, ilength, itype, plength, slength, tmpdir, ref_size_series
    ):
        """Compare multi-panel images with independent axis shown in many or none."""
        tmpdir.mkdir("test_images")
        olist = []
        mode = "test"
        test_dir = str(tmpdir)
        create_sizing_image(
            mode,
            test_dir,
            ref_size_series,
            tlength,
            ilength,
            itype,
            plength,
            slength,
            olist,
            False,
        )
        assert compare_image_set(tmpdir, olist, "figure")
