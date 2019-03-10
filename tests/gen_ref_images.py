#!/usr/bin/env python
# gen_ref_images.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0401,R0912,R0913,R0914,R0915,W0403

# Standard library imports
from __future__ import print_function
import glob
import itertools
import os
import sys

# PyPI imports
import numpy as np

# Intra-package imports
import pplot
from .fixtures import ref_panels, ref_series, ref_size_series, ref_source

###
# Global variables
###
# Relative figure size
SCALE = 2.5
DPI = 100
FHEIGHT = 3 * SCALE
FWIDTH = 4 * SCALE


###
# Functions
###
def create_axis_display_images(
    mode, test_dir, ref_panels_list, disp1, disp2, disp4, olist, verbose=True
):
    """Compare multi-panel images with independent axis shown in many or none."""
    mode, ref_dir, test_dir = setup_env(mode, test_dir)
    panel1_obj, panel2_obj, panel4_obj = ref_panels_list
    panel1_obj.display_indep_axis = disp1 == "yes"
    panel2_obj.display_indep_axis = disp2 == "yes"
    panel4_obj.display_indep_axis = disp4 == "yes"
    img_name = (
        "figure_multiple_indep_axis_panel1_"
        "{0}_panel2_{1}_panel3_{2}.png".format(disp1, disp2, disp4)
    )
    fname = def_file_names(mode, ref_dir, test_dir, img_name, olist, verbose)
    default_display = (disp1 == "no") and (disp2 == "no") and (disp4 == "no")
    fig_obj = pplot.Figure(
        panels=[panel1_obj, panel2_obj, panel4_obj],
        indep_var_label="Independent axis" if default_display else "",
        indep_var_units="",
        log_indep_axis=False,
        dpi=DPI,
        title=(
            "Multiple independent axis\n"
            "Panel 1 {0}, panel 2 {1}, panel 3 {2}".format(
                disp1, disp2, "yes by omission" if default_display else disp4
            )
        ),
    )
    fig_obj.save(fname)


def create_axis_type_display_images(
    mode, test_dir, ref_series_list, axis_type, series_in_axis, olist, verbose=True
):
    """Create panels with different type of axis types."""
    (
        series1_obj,
        series2_obj,
        series3_obj,
        series4_obj,
        series5_obj,
        series6_obj,
        series7_obj,
        series8_obj,
        series9_obj,
        _,
        _,
    ) = ref_series_list
    mode, ref_dir, test_dir = setup_env(mode, test_dir)
    img_name = "panel_{0}_axis_series_in_{1}_axis.png".format(axis_type, series_in_axis)
    if (axis_type != "filter") or (
        (axis_type == "filter") and (series_in_axis == "primary")
    ):
        fname = def_file_names(mode, ref_dir, test_dir, img_name, olist, verbose)
    if axis_type == "linear":
        if series_in_axis == "both":
            series_obj = [series1_obj, series2_obj, series3_obj, series4_obj]
        elif series_in_axis == "primary":
            series_obj = [series1_obj, series2_obj]
        elif series_in_axis == "secondary":
            series_obj = [series3_obj, series4_obj]
    elif axis_type == "log":
        if series_in_axis == "both":
            series_obj = [series1_obj, series5_obj]
        elif series_in_axis == "primary":
            series_obj = [series1_obj]
        elif series_in_axis == "secondary":
            series_obj = [series6_obj]
    if axis_type == "single":
        if series_in_axis == "both":
            series_obj = [series7_obj, series8_obj]
        elif series_in_axis == "primary":
            series_obj = [series7_obj]
        elif series_in_axis == "secondary":
            series_obj = [series8_obj]
    if axis_type == "filter":
        if series_in_axis == "both":
            pass
        elif series_in_axis == "primary":
            series_obj = [series9_obj]
        elif series_in_axis == "secondary":
            pass
    if (axis_type != "filter") or (
        (axis_type == "filter") and (series_in_axis == "primary")
    ):
        pflag = series_in_axis in ["primary", "both"]
        sflag = series_in_axis in ["secondary", "both"]
        panel_obj = pplot.Panel(
            series=series_obj,
            primary_axis_label="Primary axis" if pflag else None,
            primary_axis_units="-" if pflag else None,
            secondary_axis_label="Secondary axis" if sflag else None,
            secondary_axis_units="-" if sflag else None,
            # Hard-code it here to test series re-calculation
            # when set to True after
            log_dep_axis=False,
        )
        panel_obj.log_dep_axis = bool(axis_type == "log")
        fig_obj = pplot.Figure(
            panels=panel_obj,
            indep_var_label="Independent axis",
            indep_var_units="",
            log_indep_axis=(axis_type == "filter"),
            fig_width=FWIDTH,
            fig_height=FHEIGHT,
            dpi=DPI,
            title="Axis: {0}\nSeries in axis: {1}".format(axis_type, series_in_axis),
        )
        fig_obj.save(fname)


def create_basic_figure_image(mode, test_dir, olist, verbose=True):
    """Create figure without anything but tick marks and series without given size."""
    mode, ref_dir, test_dir = setup_env(mode, test_dir)
    img_name = "figure_basic.png"
    fname = def_file_names(mode, ref_dir, test_dir, img_name, olist, verbose)
    source_obj = pplot.BasicSource(
        np.array(list(range(1, 6))), np.array([1, 2, 3, 10, 4])
    )
    series_obj = pplot.Series(source_obj, label="")
    panel_obj = pplot.Panel(series_obj)
    figure_obj = pplot.Figure(panel_obj, dpi=DPI)
    figure_obj.save(fname)


def create_marker_line_type_image(
    mode, test_dir, ref_src, marker, interp, line_style, olist, verbose=True
):
    """Create figure testing different marker and series line style options."""
    mode, ref_dir, test_dir = setup_env(mode, test_dir)
    line_style_desc = {"-": "solid", "--": "dashed", "-.": "dash-dot", ":": "dot"}
    img_name = "series_marker_{0}_interp_{1}_line_style_{2}.png".format(
        "true" if marker else "false",
        interp.lower(),
        "none" if not line_style else line_style_desc[line_style],
    )
    fname = def_file_names(mode, ref_dir, test_dir, img_name, olist, verbose=verbose)
    series_obj = pplot.Series(
        data_source=ref_src,
        label="test series",
        marker="o" if marker else None,
        interp=interp,
        line_style=line_style,
    )
    panel_obj = pplot.Panel(
        series=series_obj, primary_axis_label="Dependent axis", primary_axis_units="-"
    )
    fig_obj = pplot.Figure(
        panels=panel_obj,
        indep_var_label="Independent axis",
        indep_var_units="",
        log_indep_axis=False,
        fig_width=FWIDTH,
        fig_height=FHEIGHT,
        dpi=DPI,
        title="marker: {0}\ninterp: {1}\nline_style: {2}".format(
            marker, interp, line_style
        ),
    )
    fig_obj.save(fname)


def create_simple_panel_image(mode, test_dir, ref_series_list, olist, verbose=True):
    """Create panel with many series but no labels, should not print legend panel."""
    _, _, _, _, _, _, _, _, _, seriesa_obj, seriesb_obj = ref_series_list
    mode, ref_dir, test_dir = setup_env(mode, test_dir)
    img_name = "panel_no_legend.png"
    fname = def_file_names(mode, ref_dir, test_dir, img_name, olist, verbose)
    series_obj = [seriesa_obj, seriesb_obj]
    panel_obj = pplot.Panel(
        series=series_obj,
        primary_axis_label="Primary axis",
        primary_axis_units="-",
        secondary_axis_label="Secondary axis",
        secondary_axis_units="-",
        log_dep_axis=True,
    )
    fig_obj = pplot.Figure(
        panels=panel_obj,
        indep_var_label="Independent axis",
        indep_var_units="",
        log_indep_axis=False,
        fig_width=FWIDTH,
        fig_height=FHEIGHT,
        dpi=DPI,
        title="Panel no legend",
    )
    fig_obj.save(fname)


def create_sizing_image(
    mode,
    test_dir,
    series_list,
    tlength,
    ilength,
    itype,
    plength,
    slength,
    olist,
    verbose=True,
):
    """Create figure to test minimum image size algorithm."""
    mode, ref_dir, test_dir = setup_env(mode, test_dir)
    series1_obj, series2_obj, series3_obj = series_list
    img_name = "size_title_{0}_indep_{1}_{2}_prim_{3}_sec_{4}.png".format(
        tlength, ilength, itype, plength, slength
    )
    fname = def_file_names(mode, ref_dir, test_dir, img_name, olist, verbose)
    panel1_obj = pplot.Panel(series=series1_obj)
    ltext = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin in"
    vartext = lambda x, y: None if x == "no" else (y if x == "short" else ltext)
    panel2_obj = pplot.Panel(
        series=(
            [series2_obj, series3_obj]
            if (plength != "no") and (slength != "no")
            else (series2_obj if plength != "no" else series3_obj)
        ),
        primary_axis_label=vartext(plength, "Primary axis"),
        secondary_axis_label=vartext(slength, "Secondary axis"),
        log_dep_axis=False,
    )
    fig_obj = pplot.Figure(
        panels=[panel1_obj, panel2_obj],
        indep_var_label=vartext(ilength, "Independent axis"),
        log_indep_axis=itype == "log",
        title=vartext(tlength, "Title"),
    )
    fig_obj.save(fname)


def def_file_names(mode, ref_dir, test_dir, img_name, olist, verbose=True):
    """Generate image file names."""
    test_fname = os.path.realpath(os.path.join(test_dir, img_name))
    if mode == "ref":
        ref_fname = os.path.realpath(os.path.join(ref_dir, img_name))
    else:
        # Support incomplete sets of reference images to reduce size
        # of source tar ball
        fdirs = glob.glob(ref_dir.format("*"))
        temp_ref_fname = [
            os.path.realpath(os.path.join(fdir, img_name)) for fdir in fdirs
        ]
        ref_fname = [item for item in temp_ref_fname if os.path.exists(item)]
    olist.append({"ref_fname": ref_fname, "test_fname": test_fname})
    if verbose:
        print("Generating image {0}".format(ref_fname if mode == "ref" else test_fname))
    return ref_fname if mode == "ref" else test_fname


def setup_env(mode, test_dir):
    """Define directories."""
    mode = "ref" if mode is None else mode.lower()
    ref_dir = (
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "support",
            "ref_images{0}".format("_{0}" if mode == "test" else ""),
        )
        if (mode == "test") or (not test_dir)
        else test_dir
    )
    test_dir = (
        os.path.abspath(os.path.join(".", os.path.abspath(os.sep), "test_images"))
        if test_dir is None
        else test_dir
    )
    return mode, ref_dir, test_dir


def unittest_series_images(mode=None, test_dir=None, _timeit=False):
    """Images for Series() class."""
    marker_list = [False, True]
    interp_list = ["STRAIGHT", "STEP", "CUBIC", "LINREG"]
    line_style_list = [None, "-", "--", "-.", ":"]
    master_list = [marker_list, interp_list, line_style_list]
    comb_list = itertools.product(*master_list)
    olist = []
    for marker, interp, line_style in comb_list:
        create_marker_line_type_image(
            mode, test_dir, ref_source(), marker, interp, line_style, olist, True
        )
        if _timeit:
            break
    return olist


def unittest_panel_images(mode=None, test_dir=None):
    """Images for Panel() class."""
    axis_type_list = ["single", "linear", "log", "filter"]
    series_in_axis_list = ["primary", "secondary", "both"]
    master_list = [axis_type_list, series_in_axis_list]
    comb_list = itertools.product(*master_list)
    olist = []
    ref_series_list = ref_series()
    for axis_type, series_in_axis in comb_list:
        create_axis_type_display_images(
            mode, test_dir, ref_series_list, axis_type, series_in_axis, olist
        )
    create_simple_panel_image(mode, test_dir, ref_series_list, olist)
    return olist


def unittest_sizing_images(mode=None, test_dir=None):
    """Images for minimum figure size."""
    title_list = ["short", "long", "no"]
    indep_axis_list = ["short", "long", "no"]
    indep_axis_type_list = ["linear", "log"]
    prim_dep_axis_list = ["short", "long", "no"]
    sec_dep_axis_list = ["short", "long", "no"]
    master_list = [
        title_list,
        indep_axis_list,
        indep_axis_type_list,
        prim_dep_axis_list,
        sec_dep_axis_list,
    ]
    comb_list = itertools.product(*master_list)
    olist = []
    print("")
    for tlength, ilength, itype, plength, slength in comb_list:
        create_sizing_image(
            mode,
            test_dir,
            ref_size_series(),
            tlength,
            ilength,
            itype,
            plength,
            slength,
            olist,
            True,
        )


def unittest_figure_images(mode=None, test_dir=None):
    """Images for Figure() class."""
    disp1_list = ["no", "yes"]
    disp2_list = ["no", "yes"]
    disp4_list = ["no", "yes"]
    master_list = [disp1_list, disp2_list, disp4_list]
    comb_list = itertools.product(*master_list)
    olist = []
    ref_panels_list = ref_panels()
    for disp1, disp2, disp4 in comb_list:
        create_axis_display_images(
            mode, test_dir, ref_panels_list, disp1, disp2, disp4, olist
        )
    create_basic_figure_image(mode, test_dir, olist)
    return olist


def main(argv):
    """Generate images."""
    if argv:
        unittest_series_images(mode="ref")
        unittest_panel_images(mode="ref")
        unittest_figure_images(mode="ref")
        unittest_sizing_images(mode="ref")
    else:
        unittest_series_images(mode="ref", test_dir=argv[0])
        unittest_panel_images(mode="ref", test_dir=argv[0])
        unittest_figure_images(mode="ref", test_dir=argv[0])
        unittest_sizing_images(mode="ref", test_dir=argv[0])


if __name__ == "__main__":
    main(sys.argv[1:])
