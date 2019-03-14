# test_doccode.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,C0413,E1129,R0914,R0915,W0212,W0640

# Standard library imports
from __future__ import print_function
import glob
import os
import subprocess

# PyPI imports
import pmisc
import matplotlib as mpl

# Default to non-interactive PNG to avoid any
# matplotlib back-end misconfiguration
mpl.rcParams["backend"] = "Agg"

# Intra-package imports
from .fixtures import export_image


###
# Functions
###
def test_plot_doccode(capsys):
    """Test used in plot module."""
    # pylint: disable=E1103,R0204
    from tests.fixtures import compare_images

    script_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "support"
    )
    script_name = os.path.join(script_dir, "plot_example_1.py")
    output_file = os.path.join(script_dir, "test_image.png")
    proc = subprocess.Popen(
        ["python", script_name, output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout, stderr = proc.communicate()
    test_fname = output_file
    ref_fnames = glob.glob(os.path.join(script_dir, "plot_example_1_*.png"))
    result = []
    for ref_fname in ref_fnames:
        try:
            result.append(compare_images(ref_fname, test_fname))
        except IOError:
            print("Error comparing images")
            print("STDOUT: {0}".format(stdout))
            print("STDERR: {0}".format(stderr))
            raise
    if not any(result):
        print("Images do not match")
        print("STDOUT: {0}".format(stdout))
        print("STDERR: {0}".format(stderr))
        for num, ref_fname in enumerate(ref_fnames):
            print(
                "Reference image {0}: file://{1}".format(
                    num, os.path.realpath(ref_fname)
                )
            )
        print("Actual image: file://{0}".format(os.path.realpath(test_fname)))
        export_image(test_fname)
    assert result
    with pmisc.ignored(OSError):
        os.remove(test_fname)
    # Test ABC example
    import numpy as np
    import docs.support.plot_example_2

    obj = docs.support.plot_example_2.MySource()
    obj.indep_var = np.array([1, 2, 3])
    obj.dep_var = np.array([-1, 1, -1])
    assert obj.indep_var.tolist() == [1, 2, 3]
    assert obj.dep_var.tolist() == [-1, 1, -1]
    assert obj._complete
    #
    import docs.support.plot_example_3

    ivar, dvar = docs.support.plot_example_3.proc_func1(1e-12, np.array([1, 2]))
    dvar = dvar.tolist()
    assert ivar, dvar == (1, [0, 1])
    obj = docs.support.plot_example_3.create_csv_source()
    assert obj.indep_var.tolist() == [2, 3, 4]
    assert obj.dep_var.tolist() == [0, -30, 10]
    #
    import docs.support.plot_example_4

    obj = docs.support.plot_example_4.create_basic_source()
    assert obj.indep_var.tolist() == [2, 3]
    assert obj.dep_var.tolist() == [-10, 10]
    assert obj._complete
    #
    import docs.support.plot_example_5

    obj = docs.support.plot_example_5.create_csv_source()
    assert obj.indep_var.tolist() == [10, 11, 12, 13, 14]
    assert obj.dep_var.tolist() == [16, 6, 26, -4, 36]
    #
    import docs.support.plot_example_6

    docs.support.plot_example_6.panel_iterator_example(no_print=False)
    stdout, stderr = capsys.readouterr()
    ref = (
        "Series 1:\n"
        "Independent variable: [ 1.0, 2.0, 3.0, 4.0 ]\n"
        "Dependent variable: [ 1.0, -10.0, 10.0, 5.0 ]\n"
        "Label: Goals\n"
        "Color: k\n"
        "Marker: o\n"
        "Interpolation: CUBIC\n"
        "Line style: -\n"
        "Secondary axis: False\n"
        "\n"
        "Series 2:\n"
        "Independent variable: [ 100.0, 200.0, 300.0, 400.0 ]\n"
        "Dependent variable: [ 50.0, 75.0, 100.0, 125.0 ]\n"
        "Label: Saves\n"
        "Color: b\n"
        "Marker: None\n"
        "Interpolation: STRAIGHT\n"
        "Line style: --\n"
        "Secondary axis: False\n\n"
    )
    assert stdout == ref
