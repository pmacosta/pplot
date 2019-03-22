# pkgdata.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import os


###
# Global variables
###
VERSION_INFO = (1, 1, 4, "final", 0)
SUPPORTED_INTERPS = ["2.7", "3.5", "3.6", "3.7"]
COPYRIGHT_START = 2013
PKG_DESC = (
    "This module can be used to create high-quality, presentation-ready X-Y graphs"
    "quickly and easily"
)
PKG_LONG_DESC = os.linesep.join(
    [
        "This module can be used to create high-quality, presentation-ready X-Y graphs "
        "quickly and easily",
        "",
        "***************",
        "Class hierarchy",
        "***************",
        "",
        "The properties of the graph (figure in Matplotlib parlance) are defined in an "
        "object of the :py:class:`pplot.Figure` class.",
        "",
        "Each figure can have one or more panels, whose properties are defined by "
        "objects of the :py:class:`pplot.Panel` class. Panels are arranged vertically "
        "in the figure and share the same independent axis.  The limits of the "
        "independent axis of the figure result from the union of the limits of the "
        "independent axis of all the panels. The independent axis is shown by default "
        "in the bottom-most panel although it can be configured to be in any panel or "
        "panels.",
        "",
        "Each panel can have one or more data series, whose properties are defined by "
        "objects of the :py:class:`pplot.Series` class. A series can be associated "
        "with either the primary or secondary dependent axis of the panel. The limits "
        "of the primary and secondary dependent axis of the panel result from the "
        "union of the primary and secondary dependent data points of all the series "
        "associated with each axis. The primary axis is shown on the left of the "
        "panel and the secondary axis is shown on the right of the panel. Axes can be "
        "linear or logarithmic.",
        "",
        "The data for a series is defined by a source. Two data sources are provided: "
        "the :py:class:`pplot.BasicSource` class provides basic data validation "
        "and minimum/maximum independent variable range bounding. The "
        ":py:class:`pplot.CsvSource` class builds upon the functionality of the "
        ":py:class:`pplot.BasicSource` class and offers a simple way of accessing "
        "data from a comma-separated values (CSV) file.  Other data sources can be "
        "programmed by inheriting from the :py:class:`pplot.functions.DataSource` "
        "abstract base class (ABC). The custom data source needs to implement the "
        "following methods: :code:`__str__`, :code:`_set_indep_var` and "
        ":code:`_set_dep_var`. The latter two methods set the contents of the "
        "independent variable (an increasing real Numpy vector) and the dependent "
        "variable (a real Numpy vector) of the source, respectively.",
        "",
        ".. [REMOVE START]",
        ".. figure:: ./support/Class_hierarchy_example.png",
        "   :scale: 100%",
        "",
        "**Figure 1:** Example diagram of the class hierarchy of a figure. In "
        "this particular example the figure consists of 3 panels. Panel 1 has a "
        "series whose data comes from a basic source, panel 2 has three series, two "
        "of which come from comma-separated values (CSV) files and one that comes "
        "from a basic source. Panel 3 has one series whose data comes from a basic "
        "source.",
        "",
        ".. [REMOVE STOP]",
        "",
        "***************",
        "Axes tick marks",
        "***************",
        "",
        "Axes tick marks are selected so as to create the most readable graph. Two "
        "global variables control the actual number of ticks, "
        ":py:data:`pplot.constants.MIN_TICKS` and "
        ":py:data:`pplot.constants.SUGGESTED_MAX_TICKS`. "
        "In general the number of ticks are between these two bounds; one or two more "
        "ticks can be present if a data series uses interpolation and the interpolated "
        "curve goes above (below) the largest (smallest) data point. Tick spacing is "
        'chosen so as to have the most number of data points "on grid". Engineering '
        "notation (i.e. 1K = 1000, 1m = 0.001, etc.) is used for the axis tick marks.",
        "",
        "*******",
        "Example",
        "*******",
        "",
        ".. literalinclude:: ./support/plot_example_1.py",
        "    :language: python",
        "    :tab-width: 4",
        "    :lines: 1,6-115",
        "",
        "|",
        "",
        ".. [REMOVE START]",
        ".. csv-table:: data.csv file",
        "   :file: ./support/data.csv",
        "   :header-rows: 1",
        "",
        "|",
        "",
        ".. figure:: ./support/plot_example_1.png",
        "   :scale: 100%",
        "",
        "**Figure 2:** plot_example_1.png generated by plot_example_1.py",
        "",
        "|",
        "",
        ".. [REMOVE STOP]",
        "",
    ]
)
PKG_PIPELINE_ID = 8
PKG_SUBMODULES = [
    "basic_source",
    "constants",
    "csv_source",
    "figure",
    "functions",
    "panel",
    "ptypes",
    "series",
]


###
# Functions
###
def _make_version(major, minor, micro, level, serial):
    """Generate version string from tuple (almost entirely from coveragepy)."""
    level_dict = {"alpha": "a", "beta": "b", "candidate": "rc", "final": ""}
    if level not in level_dict:
        raise RuntimeError("Invalid release level")
    version = "{0:d}.{1:d}".format(major, minor)
    if micro:
        version += ".{0:d}".format(micro)
    if level != "final":
        version += "{0}{1:d}".format(level_dict[level], serial)
    return version


__version__ = _make_version(*VERSION_INFO)
