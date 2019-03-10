# plot_example_4.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410,C0413

import numpy as np
import pplot


def create_basic_source():
    obj = pplot.BasicSource(
        indep_var=np.array([1, 2, 3, 4]),
        dep_var=np.array([1, -10, 10, 5]),
        indep_min=2,
        indep_max=3,
    )
    return obj
