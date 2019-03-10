# functions.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E1129,R0201,R0205,R0903,R1710,W0621

# Standard library imports
import os
import platform
import uuid

# PyPI imports
from pmisc import ignored, AE, AI, GET_EXMSG
import pytest

# Intra-package imports
import pplot


###
# Global variables
###
FOBJ = pplot.parameterized_color_space


###
# Helper functions
###
def comp_num(act, ref, prec=1e-10):
    """Test number equality within a given precision."""
    ref_list = ref if isinstance(ref, list) else [ref]
    if not any(abs(act - item) < prec for item in ref_list):
        assert False, "{0} not in {1}".format(act, ref_list)


class PseudoTmpFile(object):  # noqa
    def __init__(self, fname="", ext=""):  # noqa
        fname = fname or "test_file_{0}".format(uuid.uuid4())
        ext = "." + (ext.lstrip(".")) if ext else ext
        self._fname = "{0}{1}".format(fname, ext)
        if platform.system().lower() == "windows":
            self._fname = self._fname.replace(os.sep, "/")

    def __enter__(self):  # noqa
        return self._fname

    def __exit__(self, exc_type, exc_value, exc_tb):  # noqa
        with ignored(OSError):
            os.remove(self._fname)
        if exc_type is not None:
            return False


###
# Test classes
###
class TestDataSource(object):
    """Test for DataSource abstract base class."""

    # pylint: disable=E0110,R0912,W0223
    def test_compliance(self):  # noqa
        class Test1(pplot.DataSource):
            pass

        class Test2(pplot.DataSource):
            def __str__(self):
                pass

        class Test3(pplot.DataSource):
            def __str__(self):
                pass

            def _set_dep_var(self, dep_var):
                pass

        class Test4(pplot.DataSource):
            def __str__(self):
                pass

            def _set_dep_var(self, dep_var):
                pass

            def _set_indep_var(self, indep_var):
                pass

        class Test5(pplot.DataSource):
            def __str__(self):
                pass

            def _set_dep_var(self, dep_var):
                pass

            def _set_indep_var(self, indep_var):
                pass

            dep_var = property(None, _set_dep_var)

        class Test6(pplot.DataSource):
            def __str__(self):
                pass

            def _set_dep_var(self, dep_var):
                pass

            def _set_indep_var(self, indep_var):
                pass

            dep_var = property(None, _set_dep_var)
            indep_var = property(None, _set_indep_var)

        with pytest.raises(TypeError) as excinfo:
            Test1()
        assert GET_EXMSG(excinfo) == (
            "Can't instantiate abstract class Test1 with abstract methods "
            "__str__, _set_dep_var, _set_indep_var, dep_var, indep_var"
        )
        with pytest.raises(TypeError) as excinfo:
            Test2()
        assert GET_EXMSG(excinfo) == (
            "Can't instantiate abstract class Test2 with abstract methods "
            "_set_dep_var, _set_indep_var, dep_var, indep_var"
        )
        with pytest.raises(TypeError) as excinfo:
            Test3()
        assert GET_EXMSG(excinfo) == (
            "Can't instantiate abstract class Test3 with abstract methods "
            "_set_indep_var, dep_var, indep_var"
        )
        with pytest.raises(TypeError) as excinfo:
            Test4()
        assert GET_EXMSG(excinfo) == (
            "Can't instantiate abstract class Test4 with abstract methods "
            "dep_var, indep_var"
        )
        with pytest.raises(TypeError) as excinfo:
            Test5()
        assert GET_EXMSG(excinfo) == (
            "Can't instantiate abstract class " "Test5 with abstract methods indep_var"
        )
        # This statement should raise no exception
        Test6()


class TestParameterizedColorSpace(object):
    """Test for parameterized_color_space function."""

    # pylint: disable=W0232
    def test_param_list(self):
        """Test param_list arguments behavior."""
        pplot.parameterized_color_space([0, 1, 2, 3.3])

    @pytest.mark.functions
    def test_param_list_exceptions(self):
        """Test param_list argument exceptions."""
        items = ["a", ["a", None, False]]
        for item in items:
            AI(FOBJ, "param_list", param_list=item)
        AE(FOBJ, TypeError, "Argument `param_list` is empty", param_list=[])

    @pytest.mark.functions
    def test_offset_exceptions(self):
        """Test offset argument exceptions."""
        for item in ["a", -0.1]:
            AI(FOBJ, "offset", param_list=[1, 2], offset=item)

    def test_offset(self):
        """Test offset argument behavior."""
        pplot.parameterized_color_space([0, 1, 2, 3.3], 0.5)

    def test_color_space(self):
        """Test color argument behavior."""
        pplot.parameterized_color_space([0, 1, 2, 3.3], color_space="Blues")

    @pytest.mark.functions
    def test_color_space_exceptions(self):
        """Test color argument exceptions."""
        AI(FOBJ, "color_space", param_list=[1, 2], color_space=3)
        exmsg = (
            "Argument `color_space` is not one of 'binary', 'Blues', 'BuGn', "
            "'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', "
            "'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', "
            "'YlOrBr' or 'YlOrRd' (case insensitive)"
        )
        AE(FOBJ, ValueError, exmsg, param_list=[1, 2], color_space="a")

    def test_parameterized_color_space(self):
        """Test color_space function behavior."""
        # pylint: disable=E1101
        import matplotlib.pyplot as plt

        color_space = plt.cm.Greys
        result = pplot.parameterized_color_space(
            [0, 2 / 3.0, 4 / 3.0, 2], 0.25, "Greys"
        )
        assert result == [
            color_space(0.25),
            color_space(0.5),
            color_space(0.75),
            color_space(1.0),
        ]
