# __init__.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,C0411

# PyPI imports
from pexdoc.ptypes import real_num, positive_real_num, offset_range, function
from peng.ptypes import real_numpy_vector, increasing_real_numpy_vector

# Intra-package imports
from .basic_source import BasicSource
from .csv_source import CsvSource
from .series import Series
from .panel import Panel
from .figure import Figure
from .functions import parameterized_color_space, DataSource
from pplot.ptypes import interpolation_option, line_style_option, color_space_option
from .constants import (
    AXIS_LABEL_FONT_SIZE,
    AXIS_TICKS_FONT_SIZE,
    LEGEND_SCALE,
    LINE_WIDTH,
    MARKER_SIZE,
    MIN_TICKS,
    PRECISION,
    SUGGESTED_MAX_TICKS,
    TITLE_FONT_SIZE,
)
