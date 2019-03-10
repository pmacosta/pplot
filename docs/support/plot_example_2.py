# plot_example_2.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0413,R0205,R0903,W0235

import pplot


class MySource(pplot.DataSource, object):  # noqa
    def __init__(self):  # noqa
        super(MySource, self).__init__()

    def __str__(self):  # noqa
        return super(MySource, self).__str__()

    def _set_dep_var(self, dep_var):
        super(MySource, self)._set_dep_var(dep_var)

    def _set_indep_var(self, indep_var):
        super(MySource, self)._set_indep_var(indep_var)

    dep_var = property(pplot.DataSource._get_dep_var, _set_dep_var)

    indep_var = property(pplot.DataSource._get_indep_var, _set_indep_var)
