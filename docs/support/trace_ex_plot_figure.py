# trace_ex_plot_figure.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """Trace plot figure module exceptions."""
    mname = "figure"
    fname = "pplot"
    module_prefix = "pplot.{0}.Figure.".format(mname)
    callable_names = (
        "__init__",
        "show",
        "save",
        "axes_list",
        "fig",
        "fig_height",
        "fig_width",
        "indep_axis_scale",
        "indep_axis_ticks",
        "indep_axis_tick_labels",
        "indep_var_label",
        "indep_var_units",
        "log_indep_axis",
        "panels",
        "title",
    )
    module_exclude_list = ["peng.functions"]
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print, module_exclude_list
    )


if __name__ == "__main__":
    trace_module(False)
