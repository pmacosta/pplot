# plot_example_7.py
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410,C0413

from __future__ import print_function
import numpy, pplot

def figure_iterator_example(no_print):
    source1 = pplot.BasicSource(
        indep_var=numpy.array([1, 2, 3, 4]),
        dep_var=numpy.array([1, -10, 10, 5])
    )
    source2 = pplot.BasicSource(
        indep_var=numpy.array([100, 200, 300, 400]),
        dep_var=numpy.array([50, 75, 100, 125])
    )
    series1 = pplot.Series(
        data_source=source1,
        label='Goals'
    )
    series2 = pplot.Series(
        data_source=source2,
        label='Saves',
        color='b',
        marker=None,
        interp='STRAIGHT',
        line_style='--'
    )
    panel1 = pplot.Panel(
        series=series1,
        primary_axis_label='Average',
        primary_axis_units='A',
        display_indep_axis=False
    )
    panel2 = pplot.Panel(
        series=series2,
        primary_axis_label='Standard deviation',
        primary_axis_units=r'$\sqrt{{A}}$',
        display_indep_axis=True
    )
    figure = pplot.Figure(
        panels=[panel1, panel2],
        indep_var_label='Time',
        indep_var_units='sec',
        title='Sample Figure'
    )
    if not no_print:
        for num, panel in enumerate(figure):
            print('Panel {0}:'.format(num+1))
            print(panel)
            print('')
        figure = None
    return figure
