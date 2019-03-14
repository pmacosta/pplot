# fixtures.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0411,E0611,R0903,R0914,W0621

# Standard library imports
from __future__ import print_function
import math
import os
import shutil
import warnings

# PyPI imports
from imageio import imread
import numpy as np
from PIL import Image
import pytest

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    import scipy

# Intra-package imports
import pplot


###
# Global variables
###
IMGTOL = 1e-3

###
# Fixtures
###
def compare_images(ref_fname, act_fname, no_print=True, isize=None):
    """Compare two images by calculating Manhattan and Zero norms."""
    # Source: http://stackoverflow.com/questions/189943/
    # how-can-i-quantify-difference-between-two-images
    ref_img = Image.open(ref_fname)
    act_img = Image.open(act_fname)
    if (ref_img.size != act_img.size) or ((isize and (act_img.size != isize))):
        m_norm, z_norm = 2 * [2 * IMGTOL]
    else:
        # Element-wise for Scipy arrays
        ref_img = imread(ref_fname).astype(float)
        act_img = imread(act_fname).astype(float)
        diff = ref_img - act_img
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning)
            # Manhattan norm
            m_norm = scipy.sum(np.abs(diff))
            # Zero norm
            z_norm = scipy.linalg.norm(diff.ravel(), 0)
    result = bool((m_norm < IMGTOL) and (z_norm < IMGTOL))
    if not no_print:
        print(
            "Image 1: {0}, Image 2: {1} -> ({2}, {3}) [{4}]".format(
                ref_fname, act_fname, m_norm, z_norm, result
            )
        )
    return result


def compare_image_set(tmpdir, images_dict_list, section, isize=None):
    """Compare image sets."""
    subdir = "test_images_{0}".format(section)
    tmpdir.mkdir(subdir)
    global_result = True
    for images_dict in images_dict_list:
        ref_file_name_list = images_dict["ref_fname"]
        test_file_name = images_dict["test_fname"]
        msg = ["", "Reference images:"]
        for ref_file_name in ref_file_name_list:
            img_size = Image.open(ref_file_name).size
            msg += [
                "   file://{0} {1}".format(os.path.realpath(ref_file_name), img_size)
            ]
        img_size = Image.open(test_file_name).size
        if isize:
            msg += ["Extra size data: {0}".format(isize)]
        msg += [
            "Actual image:",
            "   file://{0} {1}".format(os.path.realpath(test_file_name), img_size),
        ]
        partial_result = []
        for ref_file_name in ref_file_name_list:
            partial_result.append(
                compare_images(ref_file_name, test_file_name, isize=isize)
            )
        result = any(partial_result)
        global_result = global_result and result
        if not result:
            msg += ["Images do not match"]
            print(os.linesep.join(msg))
            export_image(test_file_name)
    if global_result:
        try:
            tmpdir.remove(subdir)
        except OSError:  # pragma: no cover
            pass
    return global_result


@pytest.fixture
def default_source():
    """Provide a default source to be used in testing the pplot.Series class."""
    return pplot.BasicSource(
        indep_var=np.array([5, 6, 7, 8]), dep_var=np.array([0, -10, 5, 4])
    )


@pytest.fixture
def default_series(default_source):
    """Provide a default series object to be used in testing the pplot.Panel class."""
    return pplot.Series(data_source=default_source, label="test series")


@pytest.fixture
def default_panel(default_series):
    """Provide a default panel object to be used in testing the pplot.Figure class."""
    return pplot.Panel(
        series=default_series,
        primary_axis_label="Primary axis",
        primary_axis_units="A",
        secondary_axis_label="Secondary axis",
        secondary_axis_units="B",
    )


def export_image(fname):
    tdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    artifact_dir = os.environ.get("ARTIFACTS_DIR", os.path.join(tdir, "artifacts"))
    if not os.path.exists(artifact_dir):
        os.makedirs(artifact_dir)
    src = fname
    dst = os.path.join(artifact_dir, os.path.basename(fname))
    print("Copying image to {0}".format(dst))
    shutil.copyfile(src, dst)


@pytest.fixture
def negative_panel():
    """Provide panel with series with negative data for testing pplot.Figure class."""
    negative_data_source = pplot.BasicSource(
        indep_var=np.array([-5, 6, 7, 8]), dep_var=np.array([0.1, 10, 5, 4])
    )
    negative_series = pplot.Series(
        data_source=negative_data_source, label="negative data series"
    )
    return pplot.Panel(series=negative_series)


@pytest.fixture
def ref_panels():
    """Provide panels to be used in the Figure.test_axis_display unit test."""
    ds1_obj = pplot.BasicSource(
        indep_var=np.array([100, 200, 300, 400]), dep_var=np.array([1, 2, 3, 4])
    )
    ds2_obj = pplot.BasicSource(
        indep_var=np.array([300, 400, 500, 600, 700]), dep_var=np.array([3, 4, 5, 6, 7])
    )
    ds4_obj = pplot.BasicSource(
        indep_var=np.array([50, 100, 500, 1000, 1100]),
        dep_var=np.array([1.2e3, 100, 1, 300, 20]),
    )
    series1_obj = pplot.Series(
        data_source=ds1_obj,
        label="series 1",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="k",
    )
    series2_obj = pplot.Series(
        data_source=ds2_obj,
        label="series 2",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="b",
        secondary_axis=True,
    )
    series4_obj = pplot.Series(
        data_source=ds4_obj,
        label="series 3",
        marker="+",
        interp="CUBIC",
        line_style="-",
        color="r",
    )
    panel1_obj = pplot.Panel(
        series=series1_obj,
        # Test branch with no label in figure size calculation code
        primary_axis_label="",
        primary_axis_units="",
        secondary_axis_label="Secondary axis #1",
        secondary_axis_units="-",
        log_dep_axis=False,
    )
    panel2_obj = pplot.Panel(
        series=series2_obj,
        primary_axis_label="Primary axis #2",
        primary_axis_units="-",
        secondary_axis_label="Secondary axis #2",
        secondary_axis_units="-",
        log_dep_axis=False,
    )
    panel4_obj = pplot.Panel(
        series=series4_obj,
        primary_axis_label="Primary axis #3",
        primary_axis_units="-",
        secondary_axis_label="Secondary axis #3",
        secondary_axis_units="-",
        log_dep_axis=False,
    )
    return [panel1_obj, panel2_obj, panel4_obj]


@pytest.fixture
def ref_size_series():
    """Series to be used to test figure minimum sizing algorithm."""
    ds1_obj = pplot.BasicSource(
        indep_var=np.array([100, 200, 300, 400]), dep_var=np.array([1, 2, 3, 4])
    )
    ds2_obj = pplot.BasicSource(
        indep_var=np.array([300, 400, 500, 600, 700]), dep_var=np.array([3, 4, 5, 6, 7])
    )
    ds3_obj = pplot.BasicSource(
        indep_var=np.array([100, 200, 300]), dep_var=np.array([20, 40, 50])
    )
    series1_obj = pplot.Series(
        data_source=ds1_obj,
        label="series 1",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="k",
    )
    series2_obj = pplot.Series(
        data_source=ds2_obj,
        label="series 2",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="b",
    )
    series3_obj = pplot.Series(
        data_source=ds3_obj,
        label="series 3",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="g",
        secondary_axis=True,
    )
    return [series1_obj, series2_obj, series3_obj]


@pytest.fixture
def ref_series():
    """Series to be used in the Figure.test_axis_display unit test."""
    ds1_obj = pplot.BasicSource(
        indep_var=np.array([100, 200, 300, 400]), dep_var=np.array([1, 2, 3, 4])
    )
    ds2_obj = pplot.BasicSource(
        indep_var=np.array([300, 400, 500, 600, 700]), dep_var=np.array([3, 4, 5, 6, 7])
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
        indep_var=np.array([100, 200, 300, 400]), dep_var=np.array([20, 30, 40, 100])
    )
    ds7_obj = pplot.BasicSource(indep_var=np.array([200]), dep_var=np.array([50]))
    ds8_obj = pplot.BasicSource(indep_var=np.array([200]), dep_var=np.array([20]))
    indep_var = 1e3 * np.array(
        [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            20,
            30,
            40,
            50,
            60,
            70,
            80,
            90,
            100,
            200,
            300,
            400,
            500,
            600,
            700,
            800,
            900,
            1000,
        ]
    )
    dep_var = np.array(
        [
            20
            * math.log10(
                math.sqrt(
                    abs(1 / (1 + ((1j * 2 * math.pi * freq) / (2 * math.pi * 1e4))))
                )
            )
            for freq in indep_var
        ]
    )
    ds9_obj = pplot.BasicSource(indep_var=indep_var, dep_var=dep_var)
    series1_obj = pplot.Series(
        data_source=ds1_obj,
        label="series 1",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="k",
    )
    series2_obj = pplot.Series(
        data_source=ds2_obj,
        label="series 2",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="b",
    )
    series3_obj = pplot.Series(
        data_source=ds3_obj,
        label="series 3",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="g",
        secondary_axis=True,
    )
    series4_obj = pplot.Series(
        data_source=ds4_obj,
        label="series 4",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="r",
        secondary_axis=True,
    )
    series5_obj = pplot.Series(
        data_source=ds5_obj,
        label="series 5",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="m",
        secondary_axis=True,
    )
    series6_obj = pplot.Series(
        data_source=ds6_obj,
        label="series 6",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="c",
        secondary_axis=True,
    )
    series7_obj = pplot.Series(
        data_source=ds7_obj,
        label="series 7",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="y",
    )
    series8_obj = pplot.Series(
        data_source=ds8_obj,
        label="series 8",
        marker="o",
        interp="STRAIGHT",
        line_style="--",
        color="k",
        secondary_axis=True,
    )
    series9_obj = pplot.Series(
        data_source=ds9_obj,
        label="series 9",
        marker=None,
        interp="CUBIC",
        line_style="-",
        color="k",
    )
    seriesa_obj = pplot.Series(
        data_source=ds1_obj,
        label="",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="k",
    )
    seriesb_obj = pplot.Series(
        data_source=ds5_obj,
        label="",
        marker="o",
        interp="STRAIGHT",
        line_style="-",
        color="m",
        secondary_axis=True,
    )
    return [
        series1_obj,
        series2_obj,
        series3_obj,
        series4_obj,
        series5_obj,
        series6_obj,
        series7_obj,
        series8_obj,
        series9_obj,
        seriesa_obj,
        seriesb_obj,
    ]


@pytest.fixture
def ref_source():
    """Provide sources to be used in the Series.test_image unit test."""
    src = pplot.BasicSource(
        indep_var=np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        dep_var=np.array([0.9, 2.5, 3, 3.5, 5.9, 6.6, 7.1, 7.9, 9.9, 10.5]),
    )
    return src
