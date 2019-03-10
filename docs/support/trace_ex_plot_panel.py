# trace_ex_plot_panel.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """Trace plot panel module exceptions."""
    mname = "panel"
    fname = "pplot"
    module_prefix = "pplot.{0}.Panel.".format(mname)
    callable_names = (
        "__init__",
        "series",
        "primary_axis_label",
        "secondary_axis_label",
        "primary_axis_units",
        "secondary_axis_units",
        "log_axis",
        "legend_props",
        "show_indep_axis",
    )
    module_exclude_list = ["peng.functions"]
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print, module_exclude_list
    )


if __name__ == "__main__":
    trace_module(False)
