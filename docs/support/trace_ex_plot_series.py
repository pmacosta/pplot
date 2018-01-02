# trace_ex_plot_series.py
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """ Trace plot series module exceptions """
    mname = 'series'
    fname = 'pplot'
    module_prefix = 'pplot.{0}.Series.'.format(mname)
    callable_names = (
       '__init__',
       'data_source',
       'label',
       'color',
       'marker',
       'interp',
       'line_style',
       'secondary_axis'
    )
    module_exclude_list = ['peng.functions']
    return docs.support.trace_support.run_trace(
        mname,
        fname,
        module_prefix,
        callable_names,
        no_print,
        module_exclude_list
    )


if __name__ == '__main__':
    trace_module(False)
