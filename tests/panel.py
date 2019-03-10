# panel.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0411,C0413,F0401,R0205,R0912,R0914,R0915,W0212,W0611

# Standard library imports
from __future__ import print_function
import sys

# PyPI imports
import numpy as np
from pmisc import AE, AI, APROP, AROPROP, RE
import peng
import pytest

# Intra-package imports
import pplot
from .fixtures import compare_image_set, ref_series

sys.path.append("..")
from tests.gen_ref_images import (
    DPI,
    FHEIGHT,
    FWIDTH,
    create_axis_type_display_images,
    create_simple_panel_image,
)


###
# Global variables
###
FOBJ = pplot.Panel

###
# Test classes
###
class TestPanel(object):
    # pylint: disable=C0103,R0201,R0904,W0232,W0621
    """Test for Panel class."""

    ### Private methods
    def test_complete(self, default_series):
        """Test _complete property behavior."""
        obj = pplot.Panel(series=None)
        assert not obj._complete
        obj.series = default_series
        assert obj._complete

    def test_intelligent_ticks(self):
        """Test _intelligent_tick method behavior."""
        # pylint: disable=E1103
        fut = pplot.functions._intelligent_ticks
        oprec = pplot.PRECISION
        pplot.PRECISION = 8
        # 0
        # Tight = True
        # One sample
        vector = np.array([35e-6])
        obj = fut(vector, min(vector), max(vector), tight=True)
        assert obj == (
            [31.5, 35, 38.5],
            ["31.5", "35.0", "38.5"],
            31.5,
            38.5,
            1e-6,
            r"$\mu$",
        )
        # print obj
        # 1
        # Scaling with more data samples after 1.0
        vector = np.array([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
        obj = fut(vector, min(vector), max(vector), tight=True)
        assert obj == (
            [0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6],
            ["0.8", "0.9", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6"],
            0.8,
            1.6,
            1,
            " ",
        )
        # print obj
        # 2
        # Regular, should not have any scaling
        vector = np.array([1, 2, 3, 4, 5, 6, 7])
        obj = fut(vector, min(vector), max(vector), tight=True)
        assert obj == (
            [1, 2, 3, 4, 5, 6, 7],
            ["1", "2", "3", "4", "5", "6", "7"],
            1,
            7,
            1,
            " ",
        )
        # print obj
        # 3
        # Regular, should not have any scaling
        vector = np.array([10, 20, 30, 40, 50, 60, 70])
        obj = fut(vector, min(vector), max(vector), tight=True)
        assert obj == (
            [10, 20, 30, 40, 50, 60, 70],
            ["10", "20", "30", "40", "50", "60", "70"],
            10,
            70,
            1,
            " ",
        )
        # print obj
        # 4
        # Scaling
        vector = np.array([1000, 2000, 3000, 4000, 5000, 6000, 7000])
        obj = fut(vector, min(vector), max(vector), tight=True)
        assert obj == (
            [1, 2, 3, 4, 5, 6, 7],
            ["1", "2", "3", "4", "5", "6", "7"],
            1,
            7,
            1e3,
            "k",
        )
        # print obj
        # 5
        # Scaling
        vector = np.array(
            [200e6, 300e6, 400e6, 500e6, 600e6, 700e6, 800e6, 900e6, 1000e6]
        )
        obj = fut(vector, min(vector), max(vector), tight=True)
        assert obj == (
            [200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0],
            ["200", "300", "400", "500", "600", "700", "800", "900", "1k"],
            200.0,
            1000.0,
            1e6,
            "M",
        )
        # print obj
        # 6
        # No tick marks to place all data points on grid, space uniformly
        vector = np.array(
            [105, 107.7, 215, 400.2, 600, 700, 800, 810, 820, 830, 840, 850, 900, 905]
        )
        obj = fut(vector, min(vector), max(vector), tight=True)
        assert peng.round_mantissa(np.array(obj[0]), 5).tolist() == [
            105.0,
            193.889,
            282.778,
            371.667,
            460.556,
            549.444,
            638.333,
            727.222,
            816.111,
            905.0,
        ]
        assert obj[1:] == (
            [
                "105.0",
                "193.9",
                "282.8",
                "371.7",
                "460.6",
                "549.4",
                "638.3",
                "727.2",
                "816.1",
                "905.0",
            ],
            105,
            905,
            1,
            " ",
        )
        # print obj
        # 7
        # Ticks marks where some data points can be on grid
        vector = np.array([10, 20, 30, 40, 41, 50, 60, 62, 70, 75.5, 80])
        obj = fut(vector, min(vector), max(vector), tight=True)
        assert obj == (
            [10, 20, 30, 40, 50, 60, 70, 80],
            ["10", "20", "30", "40", "50", "60", "70", "80"],
            10,
            80,
            1,
            " ",
        )
        # print obj
        # 8
        # Tight = False
        # One sample
        vector = np.array([1e-9])
        obj = fut(vector, min(vector), max(vector), tight=False)
        assert obj == ([0.9, 1, 1.1], ["0.9", "1.0", "1.1"], 0.9, 1.1, 1e-9, "n")
        # print obj
        # 9
        # Scaling with more data samples after 1.0
        vector = np.array([0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6])
        obj = fut(vector, min(vector), max(vector), tight=False)
        assert obj == (
            [0.7, 0.8, 0.9, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7],
            [
                "0.7",
                "0.8",
                "0.9",
                "1.0",
                "1.1",
                "1.2",
                "1.3",
                "1.4",
                "1.5",
                "1.6",
                "1.7",
            ],
            0.7,
            1.7,
            1,
            " ",
        )
        # print obj
        # 10
        # Scaling with more data samples before 1.0
        vector = np.array([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1])
        obj = fut(vector, min(vector), max(vector), tight=False)
        assert obj == (
            [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.1, 1.2],
            [
                "0.2",
                "0.3",
                "0.4",
                "0.5",
                "0.6",
                "0.7",
                "0.8",
                "0.9",
                "1.0",
                "1.1",
                "1.2",
            ],
            0.2,
            1.2,
            1,
            " ",
        )
        # print obj
        # 11
        # Regular, with some overshoot
        vector = np.array([1, 2, 3, 4, 5, 6, 7])
        obj = fut(vector, min(vector), 7.5, tight=False)
        assert obj == (
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            ["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            0,
            8,
            1,
            " ",
        )
        # print obj
        # 12
        # Regular, with some undershoot
        vector = np.array([1, 2, 3, 4, 5, 6, 7])
        obj = fut(vector, 0.1, max(vector), tight=False)
        assert obj == (
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            ["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            0,
            8,
            1,
            " ",
        )
        # print obj
        # 13
        # Regular, with large overshoot
        vector = np.array([1, 2, 3, 4, 5, 6, 7])
        obj = fut(vector, min(vector), 20, tight=False)
        assert obj == (
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            ["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            0,
            8,
            1,
            " ",
        )
        # print obj
        # 14
        # Regular, with large undershoot
        vector = np.array([1, 2, 3, 4, 5, 6, 7])
        obj = fut(vector, -10, max(vector), tight=False)
        assert obj == (
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            ["0", "1", "2", "3", "4", "5", "6", "7", "8"],
            0,
            8,
            1,
            " ",
        )
        # print obj
        # 15
        # Scaling, minimum as reference
        vector = 1e9 + (np.array([10, 20, 30, 40, 50, 60, 70, 80]) * 1e3)
        obj = fut(vector, min(vector), max(vector), tight=True)
        assert obj == (
            [1.00001, 1.00002, 1.00003, 1.00004, 1.00005, 1.00006, 1.00007, 1.00008],
            [
                "1.00001",
                "1.00002",
                "1.00003",
                "1.00004",
                "1.00005",
                "1.00006",
                "1.00007",
                "1.00008",
            ],
            1.00001,
            1.00008,
            1e9,
            "G",
        )
        # print obj
        # # 16
        # # Scaling, delta as reference
        # # No example where the axis delta between minimum and maximum would
        # # result in fewer characters that either the minimum or maximum being
        # # used as a delta were found. Code left because as constructed it
        # # does not affect coverage metrics and in the event that for some
        # # corner cases the delta does produce fewer characters
        # vector = np.array(
        #     [
        #         10.1e6, 20e6, 30e6, 40e6, 50e6, 60e6,
        #         70e6, 80e6, 90e6, 100e6, 20.22e9
        #     ]
        # )
        # obj = fut(vector, min(vector), max(vector), tight=True)
        # print(peng.round_mantissa(np.array(obj[0]), 7).tolist())
        # assert peng.round_mantissa(np.array(obj[0]), 7).tolist() == [
        #     0.0101, 2.2556444, 4.5011889, 6.7467333, 8.9922778, 11.237822,
        #     13.483367, 15.728911, 17.974456, 20.22
        # ]
        # assert obj[1:] == (
        #     [
        #         '0.01', '2.26', '4.50', '6.75', '8.99',
        #         '11.24', '13.48', '15.73', '17.97', '20.22'
        #     ],
        #     0.0101,
        #     20.220,
        #     1e9,
        #     'G'
        # )
        # print obj
        # 17
        # Scaling, maximum as reference
        vector = np.array([0.7, 0.8, 0.9, 1.1, 1.2, 1.3, 1.4, 1.5]) * 1e12
        obj = fut(vector, min(vector), max(vector), tight=True)
        assert obj == (
            [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
            ["0.7", "0.8", "0.9", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5"],
            0.7,
            1.5,
            1e12,
            "T",
        )
        # print obj
        # 18
        # Log axis
        # Tight False
        vector = np.array([2e3, 3e4, 4e5, 5e6, 6e7])
        obj = fut(vector, min(vector), max(vector), tight=True, log_axis=True)
        assert obj == (
            [1, 10, 100, 1000, 10000, 100000],
            ["1", "10", "100", "1k", "10k", "100k"],
            1,
            100000,
            1000,
            "k",
        )
        # 19
        # Tight True
        # Left side
        vector = np.array([2e3, 3e4, 4e5, 5e6, 6e7])
        obj = fut(vector, 500, max(vector), tight=False, log_axis=True)
        assert obj == (
            [1, 10, 100, 1000, 10000, 100000],
            ["1", "10", "100", "1k", "10k", "100k"],
            1,
            100000,
            1000,
            "k",
        )
        # print obj
        # 20
        # Right side
        vector = np.array([2e3, 3e4, 4e5, 5e6, 6e7])
        obj = fut(vector, min(vector), 1e9, tight=False, log_axis=True)
        assert obj == (
            [1, 10, 100, 1000, 10000, 100000],
            ["1", "10", "100", "1k", "10k", "100k"],
            1,
            100000,
            1000,
            "k",
        )
        # print obj
        # 21
        # Both
        # Right side
        vector = np.array([2e3, 3e4, 4e5, 5e6, 6e7])
        obj = fut(vector, 500, 1e9, tight=False, log_axis=True)
        assert obj == (
            [1, 10, 100, 1000, 10000, 100000],
            ["1", "10", "100", "1k", "10k", "100k"],
            1,
            100000,
            1000,
            "k",
        )
        # print obj
        # 22
        # User-override
        vector = np.array([2e3, 3e4, 4e5, 5e6, 6e7])
        user_vector = np.array([1e6, 2e6, 5e6])
        obj = fut(vector, 500, 1e9, tight=False, log_axis=False, tick_list=user_vector)
        assert obj == ([1.0, 2.0, 5.0], ["1", "2", "5"], 1.0, 5.0, 1000000, "M")
        pplot.PRECISION = oprec
        # print obj
        # 23
        # User-override: numbers between 0 and 1 and higher than 1 in
        # absolute values
        vector = np.array(
            [
                0.84159584,
                0.88231522,
                0.9230346,
                0.96375399,
                1.00447337,
                1.04519276,
                1.08591214,
                1.12663153,
                1.16735091,
                1.2080703,
                1.24878968,
                1.28950906,
            ]
        )
        user_vector = np.array(
            [
                0.842,
                0.882,
                0.923,
                0.964,
                1.004,
                1.044,
                1.086,
                1.127,
                1.167,
                1.208,
                1.249,
                1.289,
            ]
        )
        obj = fut(
            vector,
            min(vector),
            max(vector),
            tight=False,
            log_axis=False,
            tick_list=user_vector,
        )
        assert obj == (
            [
                0.842,
                0.882,
                0.923,
                0.964,
                1.004,
                1.044,
                1.086,
                1.127,
                1.167,
                1.208,
                1.249,
                1.289,
            ],
            [
                "0.84",
                "0.88",
                "0.92",
                "0.96",
                "1.00",
                "1.04",
                "1.09",
                "1.13",
                "1.17",
                "1.21",
                "1.25",
                "1.29",
            ],
            0.842,
            1.289,
            1,
            " ",
        )

    def test_legend_position_validation(self):
        """Test _legend_position_validation method."""
        assert pplot.panel._legend_position_validation(5)
        assert pplot.panel._legend_position_validation("x")
        items = [
            None,
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
        for item in items:
            assert not pplot.panel._legend_position_validation(item)

    def test_iter(self):
        """Test __iter__ method behavior."""
        ds1_obj = pplot.BasicSource(
            indep_var=np.array([100, 200, 300, 400]), dep_var=np.array([1, 2, 3, 4])
        )
        ds2_obj = pplot.BasicSource(
            indep_var=np.array([300, 400, 500, 600, 700]),
            dep_var=np.array([3, 4, 5, 6, 7]),
        )
        ds3_obj = pplot.BasicSource(
            indep_var=np.array([100, 200, 300]), dep_var=np.array([20, 40, 50])
        )
        series1_obj = pplot.Series(data_source=ds1_obj, label="series 1", interp=None)
        series2_obj = pplot.Series(data_source=ds2_obj, label="series 2", interp=None)
        series3_obj = pplot.Series(
            data_source=ds3_obj, label="series 3", interp=None, secondary_axis=True
        )
        panel_obj = pplot.Panel(series=[series1_obj, series2_obj, series3_obj])
        for num, series in enumerate(panel_obj):
            if num == 0:
                assert series == series1_obj
            if num == 1:
                assert series == series2_obj
            if num == 2:
                assert series == series3_obj

    def test_nonzero(self, default_series):
        """Test __nonzero__ method behavior."""
        obj = pplot.Panel()
        assert not obj
        obj.series = default_series
        assert obj

    def test_str(self, default_series):
        """Test __str__ method behavior."""
        obj = pplot.Panel(series=None)
        ret = (
            "Series: None\n"
            "Primary axis label: not specified\n"
            "Primary axis units: not specified\n"
            "Secondary axis label: not specified\n"
            "Secondary axis units: not specified\n"
            "Logarithmic dependent axis: False\n"
            "Display independent axis: False\n"
            "Legend properties:\n"
            "   cols: 1\n"
            "   pos: BEST"
        )
        assert str(obj) == ret
        obj = pplot.Panel(
            series=default_series,
            primary_axis_label="Output",
            primary_axis_units="Volts",
            secondary_axis_label="Input",
            secondary_axis_units="Watts",
            display_indep_axis=True,
        )
        ret = (
            "Series 0:\n"
            "   Independent variable: [ 5.0, 6.0, 7.0, 8.0 ]\n"
            "   Dependent variable: [ 0.0, -10.0, 5.0, 4.0 ]\n"
            "   Label: test series\n"
            "   Color: k\n"
            "   Marker: o\n"
            "   Interpolation: CUBIC\n"
            "   Line style: -\n"
            "   Secondary axis: False\n"
            "Primary axis label: Output\n"
            "Primary axis units: Volts\n"
            "Secondary axis label: Input\n"
            "Secondary axis units: Watts\n"
            "Logarithmic dependent axis: False\n"
            "Display independent axis: True\n"
            "Legend properties:\n"
            "   cols: 1\n"
            "   pos: BEST"
        )
        assert str(obj) == ret

    ### Properties
    def test_log_dep_axis(self, default_series):
        """Test log_dep_axis attribute."""
        non_negative_data_source = pplot.BasicSource(
            indep_var=np.array([5, 6, 7, 8]), dep_var=np.array([0.1, 10, 5, 4])
        )
        non_negative_series = pplot.Series(
            data_source=non_negative_data_source, label="non-negative data series"
        )
        obj = pplot.Panel(series=default_series, log_dep_axis=False)
        assert not obj.log_dep_axis
        obj = pplot.Panel(series=non_negative_series, log_dep_axis=True)
        assert obj.log_dep_axis
        obj = pplot.Panel(series=default_series)
        assert not obj.log_dep_axis

    @pytest.mark.panel
    def test_log_dep_axis_exceptions(self, default_series):
        """Test log_dep_axis property exceptions."""
        AI(FOBJ, "log_dep_axis", default_series, log_dep_axis=5)
        exmsg = (
            "Series item 0 cannot be plotted in a logarithmic axis because "
            "it contains negative data points"
        )
        AE(FOBJ, ValueError, exmsg, default_series, log_dep_axis=True)
        # Trigger execution of self._series function to
        # pick up exceptions there
        obj = pplot.Panel(series=default_series)
        msg = (
            "Series item 0 cannot be plotted in a logarithmic axis "
            "because it contains negative data points"
        )
        APROP(obj, "log_dep_axis", True, ValueError, msg)

    def test_display_indep_axis(self, default_series):
        """Test display_indep_axis attribute."""
        items = [False, True]
        for item in items:
            obj = pplot.Panel(series=default_series, display_indep_axis=item)
            assert obj.display_indep_axis == item
        obj = pplot.Panel(series=default_series)
        assert not obj.display_indep_axis

    @pytest.mark.panel
    def test_display_indep_axis_exceptions(self, default_series):
        """Test display_indep_axis property exceptions."""
        AI(FOBJ, "display_indep_axis", default_series, display_indep_axis=5)

    def test_legend_props(self, default_series):
        """Test legend_props attribute."""
        obj = pplot.Panel(series=default_series, legend_props={"pos": "upper left"})
        assert obj.legend_props == {"pos": "UPPER LEFT", "cols": 1}
        obj = pplot.Panel(series=default_series, legend_props={"cols": 3})
        assert obj.legend_props == {"pos": "BEST", "cols": 3}
        obj = pplot.Panel(series=default_series)
        assert obj.legend_props == {"pos": "BEST", "cols": 1}

    @pytest.mark.panel
    def test_legend_props_exceptions(self, default_series):
        """Test legend_props property exceptions."""
        AI(FOBJ, "legend_props", default_series, legend_props=5)
        exmsg = "Illegal legend property `not_a_valid_prop`"
        lprops = {"not_a_valid_prop": 5}
        AE(FOBJ, ValueError, exmsg, default_series, legend_props=lprops)
        exmsg = (
            "Legend property `pos` is not one of ['BEST', 'UPPER RIGHT', "
            "'UPPER LEFT', 'LOWER LEFT', 'LOWER RIGHT', 'RIGHT', "
            "'CENTER LEFT', 'CENTER RIGHT', 'LOWER CENTER', 'UPPER CENTER', "
            "'CENTER'] (case insensitive)"
        )
        AE(FOBJ, TypeError, exmsg, default_series, legend_props={"pos": 5})
        exmsg = "Legend property `cols` is not valid"
        AE(FOBJ, RE, exmsg, default_series, legend_props={"cols": -1})

    def test_primary_axis_label(self, default_series):
        """Test panel_primary_axis attribute."""
        # This assignment should not raise an exception
        pplot.Panel(series=default_series, primary_axis_label=None)
        obj = pplot.Panel(series=default_series, primary_axis_label="test")
        assert obj.primary_axis_label == "test"

    @pytest.mark.panel
    def test_primary_axis_label_exceptions(self, default_series):
        """Test panel_primary_axis property exceptions."""
        AI(FOBJ, "primary_axis_label", default_series, primary_axis_label=5)

    def test_primary_axis_ticks(self, default_source, default_series):
        """Test primary_axis_ticks property behavior."""
        obj = pplot.Panel(series=None)
        assert obj.primary_axis_ticks is None
        obj = pplot.Panel(
            series=default_series, primary_axis_ticks=[1000, 2000, 3000, 3500]
        )
        assert obj.primary_axis_ticks == [1.0, 2.0, 3.0, 3.5]
        obj = pplot.Panel(
            series=default_series, primary_axis_ticks=[1e6, 4e6, 8e6, 9e6]
        )
        assert obj.primary_axis_ticks == [1.0, 4.0, 8.0, 9.0]
        obj = pplot.Panel(
            series=pplot.Series(
                data_source=default_source, label="test series", secondary_axis=True
            ),
            primary_axis_ticks=[1000, 2000, 3000, 3500],
        )
        assert obj.primary_axis_ticks is None
        # Logarithmic independent axis tick marks
        # cannot be overridden
        obj = pplot.Panel(
            series=pplot.Series(
                data_source=pplot.BasicSource(
                    indep_var=np.array([1e9, 20e9]), dep_var=np.array([3, 5])
                ),
                interp="STRAIGHT",
                label="test series",
            ),
            primary_axis_ticks=[1000, 2000, 3000, 3500],
            log_dep_axis=True,
        )
        assert obj.primary_axis_ticks == [1.0, 10.0]

    @pytest.mark.panel
    def test_primary_axis_ticks_exceptions(self, default_series):
        """Test primary_axis_ticks property exceptions."""
        AI(FOBJ, "primary_axis_ticks", default_series, primary_axis_ticks=5)

    def test_primary_axis_units(self, default_series):
        """Test panel_primary_axis attribute."""
        pplot.Panel(series=default_series, primary_axis_units=None)
        obj = pplot.Panel(series=default_series, primary_axis_units="test")
        assert obj.primary_axis_units == "test"

    @pytest.mark.panel
    def test_primary_axis_units_exceptions(self, default_series):
        """Test panel_primary_axis property exceptions."""
        AI(FOBJ, "primary_axis_units", default_series, primary_axis_units=5)

    def test_secondary_axis_label(self, default_series):
        """Test panel_secondary_axis attribute."""
        pplot.Panel(series=default_series, secondary_axis_label=None)
        obj = pplot.Panel(series=default_series, secondary_axis_label="test")
        assert obj.secondary_axis_label == "test"

    @pytest.mark.panel
    def test_secondary_axis_label_exceptions(self, default_series):
        """Test panel_secondary_axis property exceptions."""
        kwargs = dict(secondary_axis_label=5)
        AI(FOBJ, "secondary_axis_label", default_series, **kwargs)

    def test_secondary_axis_ticks(self, default_source, default_series):
        """Test secondary_axis_ticks attribute behavior."""
        obj = pplot.Panel(series=None)
        assert obj.secondary_axis_ticks is None
        series_obj = pplot.Series(
            data_source=default_source, label="test series", secondary_axis=True
        )
        obj = pplot.Panel(
            series=series_obj, secondary_axis_ticks=[1000, 2000, 3000, 3500]
        )
        assert obj.secondary_axis_ticks == [1.0, 2.0, 3.0, 3.5]
        obj = pplot.Panel(series=series_obj, secondary_axis_ticks=[1e6, 4e6, 8e6, 9e6])
        assert obj.secondary_axis_ticks == [1.0, 4.0, 8.0, 9.0]
        obj = pplot.Panel(
            series=default_series, secondary_axis_ticks=[1000, 2000, 3000, 3500]
        )
        assert obj.secondary_axis_ticks is None
        # Logarithmic independent axis tick marks
        # cannot be overridden
        obj = pplot.Panel(
            series=pplot.Series(
                data_source=pplot.BasicSource(
                    indep_var=np.array([1e9, 20e9]), dep_var=np.array([3, 5])
                ),
                interp="STRAIGHT",
                label="test series",
                secondary_axis=True,
            ),
            secondary_axis_ticks=[1000, 2000, 3000, 3500],
            log_dep_axis=True,
        )
        assert obj.secondary_axis_ticks == [1.0, 10.0]

    @pytest.mark.panel
    def test_secondary_axis_ticks_exceptions(self, default_series):
        """Test secondary_axis_ticks property exceptions."""
        kwargs = dict(secondary_axis_ticks=5)
        AI(FOBJ, "secondary_axis_ticks", default_series, **kwargs)

    def test_secondary_axis_units(self, default_series):
        """Test panel_secondary_axis attribute."""
        pplot.Panel(series=default_series, secondary_axis_units=None)
        obj = pplot.Panel(series=default_series, secondary_axis_units="test")
        assert obj.secondary_axis_units == "test"

    @pytest.mark.panel
    def test_secondary_axis_units_exceptions(self, default_series):
        """Test panel_secondary_axis property exceptions."""
        kwargs = dict(secondary_axis_units=5)
        AI(FOBJ, "secondary_axis_units", default_series, **kwargs)

    ### Miscellaneous
    def test_series(self):
        """Test panel dependent axis calculation."""
        ds1_obj = pplot.BasicSource(
            indep_var=np.array([100, 200, 300, 400]), dep_var=np.array([1, 2, 3, 4])
        )
        ds2_obj = pplot.BasicSource(
            indep_var=np.array([300, 400, 500, 600, 700]),
            dep_var=np.array([3, 4, 5, 6, 7]),
        )
        ds3_obj = pplot.BasicSource(
            indep_var=np.array([100, 200, 300]), dep_var=np.array([20, 40, 50])
        )
        ds4_obj = pplot.BasicSource(
            indep_var=np.array([100, 200, 300]), dep_var=np.array([10, 25, 35])
        )
        ds5_obj = pplot.BasicSource(
            indep_var=np.array([100, 200, 300, 400]), dep_var=np.array([10, 20, 30, 40])
        )
        ds6_obj = pplot.BasicSource(
            indep_var=np.array([100, 200, 300, 400]),
            dep_var=np.array([20, 30, 40, 100]),
        )
        ds7_obj = pplot.BasicSource(
            indep_var=np.array([100, 200, 300, 400]), dep_var=np.array([20, 30, 40, 50])
        )
        ds8_obj = pplot.BasicSource(indep_var=np.array([100]), dep_var=np.array([20]))
        series1_obj = pplot.Series(data_source=ds1_obj, label="series 1", interp=None)
        series2_obj = pplot.Series(data_source=ds2_obj, label="series 2", interp=None)
        series3_obj = pplot.Series(
            data_source=ds3_obj, label="series 3", interp=None, secondary_axis=True
        )
        series4_obj = pplot.Series(
            data_source=ds4_obj, label="series 4", interp=None, secondary_axis=True
        )
        series5_obj = pplot.Series(
            data_source=ds5_obj, label="series 5", interp=None, secondary_axis=True
        )
        series6_obj = pplot.Series(
            data_source=ds6_obj, label="series 6", interp=None, secondary_axis=True
        )
        series7_obj = pplot.Series(data_source=ds7_obj, label="series 7", interp=None)
        series8_obj = pplot.Series(data_source=ds8_obj, label="series 8", interp=None)
        # 0-8: Linear primary and secondary axis, with multiple series on both
        panel_obj = pplot.Panel(
            series=[series1_obj, series2_obj, series3_obj, series4_obj]
        )
        assert (panel_obj._has_prim_axis, panel_obj._has_sec_axis) == (True, True)
        assert panel_obj._primary_dep_var_locs == [
            0,
            0.8,
            1.6,
            2.4,
            3.2,
            4.0,
            4.8,
            5.6,
            6.4,
            7.2,
            8.0,
        ]
        assert panel_obj._primary_dep_var_labels == [
            "0.0",
            "0.8",
            "1.6",
            "2.4",
            "3.2",
            "4.0",
            "4.8",
            "5.6",
            "6.4",
            "7.2",
            "8.0",
        ]
        assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (
            0,
            8,
        )
        assert (
            panel_obj._primary_dep_var_div,
            panel_obj._primary_dep_var_unit_scale,
        ) == (1, " ")
        assert panel_obj._secondary_dep_var_locs == [
            5,
            10,
            15,
            20,
            25,
            30,
            35,
            40,
            45,
            50,
            55,
        ]
        assert panel_obj._secondary_dep_var_labels == [
            "5",
            "10",
            "15",
            "20",
            "25",
            "30",
            "35",
            "40",
            "45",
            "50",
            "55",
        ]
        assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (
            5,
            55,
        )
        assert (
            panel_obj._secondary_dep_var_div,
            panel_obj._secondary_dep_var_unit_scale,
        ) == (1, " ")
        # 9-17: Linear primary axis with multiple series
        panel_obj = pplot.Panel(series=[series1_obj, series2_obj])
        assert (panel_obj._has_prim_axis, panel_obj._has_sec_axis) == (True, False)
        assert panel_obj._primary_dep_var_locs == [0, 1, 2, 3, 4, 5, 6, 7, 8]
        assert panel_obj._primary_dep_var_labels == [
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
        ]
        assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (
            0,
            8,
        )
        assert (
            panel_obj._primary_dep_var_div,
            panel_obj._primary_dep_var_unit_scale,
        ) == (1, " ")
        assert panel_obj._secondary_dep_var_locs is None
        assert panel_obj._secondary_dep_var_labels is None
        assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (
            None,
            None,
        )
        assert (
            panel_obj._secondary_dep_var_div,
            panel_obj._secondary_dep_var_unit_scale,
        ) == (None, None)
        # 18-26: Linear secondary axis with multiple series on both
        panel_obj = pplot.Panel(series=[series3_obj, series4_obj])
        assert (panel_obj._has_prim_axis, panel_obj._has_sec_axis) == (False, True)
        assert panel_obj._primary_dep_var_locs is None
        assert panel_obj._primary_dep_var_labels is None
        assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (
            None,
            None,
        )
        assert (
            panel_obj._primary_dep_var_div,
            panel_obj._primary_dep_var_unit_scale,
        ) == (None, None)
        assert panel_obj._secondary_dep_var_locs == [
            5,
            10,
            15,
            20,
            25,
            30,
            35,
            40,
            45,
            50,
            55,
        ]
        assert panel_obj._secondary_dep_var_labels == [
            "5",
            "10",
            "15",
            "20",
            "25",
            "30",
            "35",
            "40",
            "45",
            "50",
            "55",
        ]
        assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (
            5,
            55,
        )
        assert (
            panel_obj._secondary_dep_var_div,
            panel_obj._secondary_dep_var_unit_scale,
        ) == (1, " ")
        # 27-35: Logarithmic primary and secondary axis,
        # with multiple series on both
        panel_obj = pplot.Panel(series=[series1_obj, series5_obj], log_dep_axis=True)
        assert (panel_obj._has_prim_axis, panel_obj._has_sec_axis) == (True, True)
        assert panel_obj._primary_dep_var_locs == [0.9, 1, 10, 100]
        assert panel_obj._primary_dep_var_labels == ["", "1", "10", "100"]
        assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (
            0.9,
            100,
        )
        assert (
            panel_obj._primary_dep_var_div,
            panel_obj._primary_dep_var_unit_scale,
        ) == (1, " ")
        assert panel_obj._secondary_dep_var_locs == [0.9, 1, 10, 100]
        assert panel_obj._secondary_dep_var_labels == ["", "1", "10", "100"]
        assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (
            0.9,
            100,
        )
        assert (
            panel_obj._secondary_dep_var_div,
            panel_obj._secondary_dep_var_unit_scale,
        ) == (1, " ")
        # 36-44: Logarithmic primary axis (bottom point at decade edge)
        panel_obj = pplot.Panel(series=[series1_obj], log_dep_axis=True)
        assert (panel_obj._has_prim_axis, panel_obj._has_sec_axis) == (True, False)
        assert panel_obj._primary_dep_var_locs == [0.9, 1, 10]
        assert panel_obj._primary_dep_var_labels == ["", "1", "10"]
        assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (
            0.9,
            10,
        )
        assert (
            panel_obj._primary_dep_var_div,
            panel_obj._primary_dep_var_unit_scale,
        ) == (1, " ")
        assert panel_obj._secondary_dep_var_locs is None
        assert panel_obj._secondary_dep_var_labels is None
        assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (
            None,
            None,
        )
        assert (
            panel_obj._secondary_dep_var_div,
            panel_obj._secondary_dep_var_unit_scale,
        ) == (None, None)
        # 45-53: Logarithmic secondary axis (top point at decade edge)
        panel_obj = pplot.Panel(series=[series6_obj], log_dep_axis=True)
        assert (panel_obj._has_prim_axis, panel_obj._has_sec_axis) == (False, True)
        assert panel_obj._primary_dep_var_locs is None
        assert panel_obj._primary_dep_var_labels is None
        assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (
            None,
            None,
        )
        assert (
            panel_obj._primary_dep_var_div,
            panel_obj._primary_dep_var_unit_scale,
        ) == (None, None)
        assert panel_obj._secondary_dep_var_locs == [10, 100, 110]
        assert panel_obj._secondary_dep_var_labels == ["10", "100", ""]
        assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (
            10,
            110,
        )
        assert (
            panel_obj._secondary_dep_var_div,
            panel_obj._secondary_dep_var_unit_scale,
        ) == (1, " ")
        # 54-62: Logarithmic secondary axis (points not at decade edge)
        panel_obj = pplot.Panel(series=[series7_obj], log_dep_axis=True)
        assert (panel_obj._has_prim_axis, panel_obj._has_sec_axis) == (True, False)
        assert panel_obj._primary_dep_var_locs == [10, 100]
        assert panel_obj._primary_dep_var_labels == ["10", "100"]
        assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (
            10,
            100,
        )
        assert (
            panel_obj._primary_dep_var_div,
            panel_obj._primary_dep_var_unit_scale,
        ) == (1, " ")
        assert panel_obj._secondary_dep_var_locs is None
        assert panel_obj._secondary_dep_var_labels is None
        assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (
            None,
            None,
        )
        assert (
            panel_obj._secondary_dep_var_div,
            panel_obj._secondary_dep_var_unit_scale,
        ) == (None, None)
        # 63-71: Logarithmic secondary axis (1 point)
        panel_obj = pplot.Panel(series=[series8_obj], log_dep_axis=True)
        assert (panel_obj._has_prim_axis, panel_obj._has_sec_axis) == (True, False)
        assert panel_obj._primary_dep_var_locs == [18, 20, 22]
        assert panel_obj._primary_dep_var_labels == ["18", "20", "22"]
        assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (
            18,
            22,
        )
        assert (
            panel_obj._primary_dep_var_div,
            panel_obj._primary_dep_var_unit_scale,
        ) == (1, " ")
        assert panel_obj._secondary_dep_var_locs is None
        assert panel_obj._secondary_dep_var_labels is None
        assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (
            None,
            None,
        )
        assert (
            panel_obj._secondary_dep_var_div,
            panel_obj._secondary_dep_var_unit_scale,
        ) == (None, None)
        # 72-80: Linear secondary axis (1 point)
        panel_obj = pplot.Panel(series=[series8_obj], log_dep_axis=False)
        assert (panel_obj._has_prim_axis, panel_obj._has_sec_axis) == (True, False)
        assert panel_obj._primary_dep_var_locs == [18, 20, 22]
        assert panel_obj._primary_dep_var_labels == ["18", "20", "22"]
        assert (panel_obj._primary_dep_var_min, panel_obj._primary_dep_var_max) == (
            18,
            22,
        )
        assert (
            panel_obj._primary_dep_var_div,
            panel_obj._primary_dep_var_unit_scale,
        ) == (1, " ")
        assert panel_obj._secondary_dep_var_locs is None
        assert panel_obj._secondary_dep_var_labels is None
        assert (panel_obj._secondary_dep_var_min, panel_obj._secondary_dep_var_max) == (
            None,
            None,
        )
        assert (
            panel_obj._secondary_dep_var_div,
            panel_obj._secondary_dep_var_unit_scale,
        ) == (None, None)

    def test_scale_series(self, default_series):
        """Test series scaling calculation."""
        source_obj = pplot.BasicSource(
            indep_var=np.array([5, 6, 7, 8]), dep_var=np.array([4.2, 8, 10, 4])
        )
        series_obj = pplot.Series(
            data_source=source_obj, label="test", secondary_axis=True
        )
        panel1_obj = pplot.Panel(series=series_obj)
        panel2_obj = pplot.Panel(series=[default_series, series_obj])
        obj = pplot.Panel(series=default_series)
        obj._scale_dep_var(2, None)
        assert (abs(obj.series[0].scaled_dep_var - [0, -5, 2.5, 2]) < 1e-10).all()
        obj._scale_dep_var(2, 5)
        assert (abs(obj.series[0].scaled_dep_var - [0, -5, 2.5, 2]) < 1e-10).all()
        panel1_obj._scale_dep_var(None, 2)
        assert (abs(panel1_obj.series[0].scaled_dep_var - [2.1, 4, 5, 2]) < 1e-10).all()
        panel2_obj._scale_dep_var(4, 5)
        tobj = panel2_obj.series
        assert (
            (abs(tobj[0].scaled_dep_var - [0, -2.5, 1.25, 1]) < 1e-10).all(),
            (abs(tobj[1].scaled_dep_var - [0.84, 1.6, 2, 0.8]) < 1e-10).all(),
        ) == (True, True)
        assert panel1_obj.primary_axis_scale is None
        assert panel1_obj.secondary_axis_scale == 1
        assert panel2_obj.primary_axis_scale == 1
        assert panel2_obj.secondary_axis_scale == 1

    @pytest.mark.panel
    def test_cannot_delete_attributes_exceptions(self, default_series):
        """Test that del method raises an exception on all class attributes."""
        props = [
            "series",
            "primary_axis_label",
            "secondary_axis_label",
            "primary_axis_units",
            "secondary_axis_units",
            "log_dep_axis",
            "legend_props",
            "primary_axis_scale",
            "secondary_axis_scale",
        ]
        obj = pplot.Panel(series=default_series)
        for prop in props:
            AROPROP(obj, prop)

    ### Functional
    @pytest.mark.parametrize("axis_type", ["single", "linear", "log", "filter"])
    @pytest.mark.parametrize("series_in_axis", ["primary", "secondary", "both"])
    def test_axis_type_display(self, axis_type, series_in_axis, tmpdir, ref_series):
        """Compare images to verify correct plotting of panel."""
        isize = (int(DPI * FWIDTH), int(DPI * FHEIGHT))
        tmpdir.mkdir("test_images")
        mode = "test"
        test_dir = str(tmpdir)
        olist = []
        create_axis_type_display_images(
            mode, test_dir, ref_series, axis_type, series_in_axis, olist, False
        )
        assert compare_image_set(tmpdir, olist, "panel", isize=isize)

    def test_basic_panel(self, tmpdir, ref_series):
        """Test simple panel drawing."""
        isize = (int(DPI * FWIDTH), int(DPI * FHEIGHT))
        tmpdir.mkdir("test_images")
        mode = "test"
        test_dir = str(tmpdir)
        olist = []
        create_simple_panel_image(mode, test_dir, ref_series, olist, False)
        assert compare_image_set(tmpdir, olist, "panel", isize=isize)
