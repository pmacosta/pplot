# trace_ex_plot_functions.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """Trace plot functions module exceptions."""
    mname = "functions"
    fname = "pplot"
    module_prefix = "pplot.{0}.".format(mname)
    callable_names = ("parameterized_color_space",)
    module_exclude_list = ["peng.functions"]
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print, module_exclude_list
    )


if __name__ == "__main__":
    trace_module(False)
