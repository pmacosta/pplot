.. README.rst
.. Copyright (c) 2013-2019 Pablo Acosta-Serafini
.. See LICENSE for details

.. image:: https://badge.fury.io/py/pplot.svg
    :target: https://pypi.org/project/pplot
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/l/pplot.svg
    :target: https://pypi.org/project/pplot
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/pplot.svg
    :target: https://pypi.org/project/pplot
    :alt: Python versions supported

.. image:: https://img.shields.io/pypi/format/pplot.svg
    :target: https://pypi.org/project/pplot
    :alt: Format

|

.. image::
    https://dev.azure.com/pmasdev/pplot/_apis/build/status/pmacosta.pplot?branchName=master
    :target: https://dev.azure.com/pmasdev/pplot/_build?definitionId=3&_a=summary
    :alt: Continuous integration test status

.. image::
    https://img.shields.io/azure-devops/coverage/pmasdev/pplot/8.svg
    :target: https://dev.azure.com/pmasdev/pplot/_build?definitionId=6&_a=summary
    :alt: Continuous integration test coverage

.. image::
    https://readthedocs.org/projects/pip/badge/?version=stable
    :target: https://pip.readthedocs.io/en/stable/?badge=stable
    :alt: Documentation status

|

Description
===========

.. role:: bash(code)
	:language: bash

.. [[[cog
.. import os, sys, pmisc, docs.support.requirements_to_rst
.. file_name = sys.modules['docs.support.requirements_to_rst'].__file__
.. mdir = os.path.join(os.path.realpath(
..    os.path.dirname(os.path.dirname(os.path.dirname(file_name)))), 'pypkg'
.. )
.. docs.support.requirements_to_rst.def_links(cog)
.. ]]]
.. _Astroid: https://bitbucket.org/logilab/astroid
.. _Cog: https://nedbatchelder.com/code/cog
.. _Coverage: https://coverage.readthedocs.io
.. _Decorator: https://decorator.readthedocs.io
.. _Docutils: http://docutils.sourceforge.net/docs
.. _Funcsigs: https://pypi.org/project/funcsigs
.. _Matplotlib: https://matplotlib.org
.. _Mock: https://docs.python.org/3/library/unittest.mock.html
.. _Numpy: http://www.numpy.org
.. _Pcsv: https://pcsv.readthedocs.org
.. _Peng: https://peng.readthedocs.org
.. _Pexdoc: https://pexdoc.readthedocs.org
.. _Pillow: https://python-pillow.org
.. _Pmisc: http://pmisc.readthedocs.org
.. _PyContracts: https://andreacensi.github.io/contracts
.. _Pydocstyle: http://www.pydocstyle.org
.. _Pylint: https://www.pylint.org
.. _Py.test: http://pytest.org
.. _Pytest-coverage: https://pypi.org/project/pytest-cov
.. _Pytest-pmisc: https://pytest-pmisc.readthedocs.org
.. _Pytest-xdist: https://pypi.org/project/pytest-xdist
.. _Scipy: https://www.scipy.org
.. _Six: https://pythonhosted.org/six
.. _Sphinx: http://sphinx-doc.org
.. _ReadTheDocs Sphinx theme: https://github.com/rtfd/sphinx_rtd_theme
.. _Inline Syntax Highlight Sphinx Extension:
   https://bitbucket.org/klorenz/sphinxcontrib-inlinesyntaxhighlight
.. _Shellcheck Linter Sphinx Extension: https://pypi.org/project
   /sphinxcontrib-shellcheck
.. _Tox: https://testrun.org/tox
.. _Virtualenv: https://docs.python-guide.org/dev/virtualenvs
.. [[[end]]]


This module can be used to create high-quality, presentation-ready X-Y graphs
quickly and easily

***************
Class hierarchy
***************

The properties of the graph (figure in Matplotlib parlance) are defined in an
object of the :py:class:`pplot.Figure` class.

Each figure can have one or more panels, whose properties are defined by objects
of the :py:class:`pplot.Panel` class. Panels are arranged vertically in
the figure and share the same independent axis.  The limits of the independent
axis of the figure result from the union of the limits of the independent axis
of all the panels. The independent axis is shown by default in the bottom-most
panel although it can be configured to be in any panel or panels.

Each panel can have one or more data series, whose properties are defined by
objects of the :py:class:`pplot.Series` class. A series can be associated
with either the primary or secondary dependent axis of the panel. The limits of
the primary and secondary dependent axis of the panel result from the union of
the primary and secondary dependent data points of all the series associated
with each axis. The primary axis is shown on the left of the panel and the
secondary axis is shown on the right of the panel. Axes can be linear or
logarithmic.

The data for a series is defined by a source. Two data sources are provided:
the :py:class:`pplot.BasicSource` class provides basic data validation
and minimum/maximum independent variable range bounding. The
:py:class:`pplot.CsvSource` class builds upon the functionality of the
:py:class:`pplot.BasicSource` class and offers a simple way of accessing
data from a comma-separated values (CSV) file.  Other data sources can be
programmed by inheriting from the :py:class:`pplot.functions.DataSource`
abstract base class (ABC). The custom data source needs to implement the
following methods: :code:`__str__`, :code:`_set_indep_var` and
:code:`_set_dep_var`. The latter two methods set the contents of the
independent variable (an increasing real Numpy vector) and the dependent
variable (a real Numpy vector) of the source, respectively.

.. [REMOVE START]
.. figure:: ./support/Class_hierarchy_example.png
   :scale: 100%

**Figure 1:** Example diagram of the class hierarchy of a figure. In
this particular example the figure consists of 3 panels. Panel 1 has a
series whose data comes from a basic source, panel 2 has three series, two
of which come from comma-separated values (CSV) files and one that comes
from a basic source. Panel 3 has one series whose data comes from a basic
source.
.. [REMOVE STOP]

***************
Axes tick marks
***************

Axes tick marks are selected so as to create the most readable graph. Two
global variables control the actual number of ticks,
:py:data:`pplot.constants.MIN_TICKS` and
:py:data:`pplot.constants.SUGGESTED_MAX_TICKS`.
In general the number of ticks are between these two bounds; one or two more
ticks can be present if a data series uses interpolation and the interpolated
curve goes above (below) the largest (smallest) data point. Tick spacing is
chosen so as to have the most number of data points "on grid". Engineering
notation (i.e. 1K = 1000, 1m = 0.001, etc.) is used for the axis tick marks.

*******
Example
*******

.. literalinclude:: ./support/plot_example_1.py
    :language: python
    :tab-width: 4
    :lines: 1,6-108

|

.. [REMOVE START]
.. csv-table:: data.csv file
   :file: ./support/data.csv
   :header-rows: 1

|

.. figure:: ./support/plot_example_1.png
   :scale: 100%

**Figure 2:** plot_example_1.png generated by plot_example_1.py

|

.. [REMOVE STOP]

Interpreter
===========

The package has been developed and tested with Python 2.7, 3.5, 3.6 and 3.7
under Linux (Debian, Ubuntu), Apple macOS and Microsoft Windows

Installing
==========

.. code-block:: bash

	$ pip install pplot

Documentation
=============

Available at `Read the Docs <https://pplot.readthedocs.io>`_

Contributing
============

1. Abide by the adopted `code of conduct
   <https://www.contributor-covenant.org/version/1/4/code-of-conduct>`_

2. Fork the `repository <https://github.com/pmacosta/pplot>`_ from
   GitHub and then clone personal copy [#f1]_:

    .. code-block:: bash

        $ github_user=myname
        $ git clone --recursive \
              https://github.com/"${github_user}"/pplot.git
        Cloning into 'pplot'...
        ...
        $ cd pplot
        $ export PPLOT_DIR=${PWD}

3. Install the project's Git hooks and build the documentation. The pre-commit
   hook does some minor consistency checks, namely trailing whitespace and
   `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ compliance via
   Pylint. Assuming the directory to which the repository was cloned is
   in the :bash:`$PPLOT_DIR` shell environment variable:

	.. code-block:: bash

		$ "${PPLOT_DIR}"/pypkg/complete-cloning.sh
                Installing Git hooks
                Building pplot package documentation
                ...

4. Ensure that the Python interpreter can find the package modules
   (update the :bash:`$PYTHONPATH` environment variable, or use
   `sys.paths() <https://docs.python.org/3/library/sys.html#sys.path>`_,
   etc.)

	.. code-block:: bash

		$ export PYTHONPATH=${PYTHONPATH}:${PPLOT_DIR}

5. Install the dependencies (if needed, done automatically by pip):

    .. [[[cog
    .. import docs.support.requirements_to_rst
    .. docs.support.requirements_to_rst.proc_requirements(cog)
    .. ]]]


    * `Astroid`_ (1.3.8 or newer)

    * `Cog`_ (2.4 or newer)

    * `Coverage`_ (3.7.1 or newer)

    * `Decorator`_ (4.2.1 or newer)

    * `Docutils`_ (0.12 or newer)

    * `Funcsigs`_ (1.0.2 or newer)

    * `Inline Syntax Highlight Sphinx Extension`_ (0.2 or newer)

    * `Matplotlib`_ (2.0.0 or newer)

    * `Mock`_ (2.0.0 or newer)

    * `Numpy`_ (1.13.1 or newer)

    * `Pcsv`_ (1.0.7 or newer)

    * `Peng`_ (1.0.8 or newer)

    * `Pexdoc`_ (1.1.1 or newer)

    * `Pillow`_ (4.0.0 or newer)

    * `Pmisc`_ (1.5.5 or newer)

    * `Py.test`_ (3.3.2 or newer)

    * `PyContracts`_ (1.8.2 or newer)

    * `Pydocstyle`_ (3.0.0 or newer)

    * `Pylint`_ (1.8.1 or newer)

    * `Pytest-coverage`_ (2.5.1 or newer)

    * `Pytest-pmisc`_ (1.0.6 or newer)

    * `Pytest-xdist`_ (optional, 1.22.0 or newer)

    * `ReadTheDocs Sphinx theme`_ (0.2.4 or newer)

    * `Scipy`_ (1.0.0 or newer)

    * `Shellcheck Linter Sphinx Extension`_ (1.0.5 or newer)

    * `Six`_ (1.11.0 or newer)

    * `Sphinx`_ (1.6.6 or newer)

    * `Tox`_ (2.9.1 or newer)

    * `Virtualenv`_ (15.1.0 or newer)

    .. [[[end]]]

6. Implement a new feature or fix a bug

7. Write a unit test which shows that the contributed code works as expected.
   Run the package tests to ensure that the bug fix or new feature does not
   have adverse side effects. If possible achieve 100% code and branch
   coverage of the contribution. Thorough package validation
   can be done via Tox and Py.test:

	.. code-block:: bash

            $ tox
            GLOB sdist-make: .../pplot/setup.py
            py26-pkg inst-nodeps: .../pplot/.tox/dist/pplot-...zip

   `Setuptools <https://bitbucket.org/pypa/setuptools>`_ can also be used
   (Tox is configured as its virtual environment manager):

	.. code-block:: bash

	    $ python setup.py tests
            running tests
            running egg_info
            writing requirements to pplot.egg-info/requires.txt
            writing pplot.egg-info/PKG-INFO
            ...

   Tox (or Setuptools via Tox) runs with the following default environments:
   ``py27-pkg``, ``py35-pkg``, ``py36-pkg`` and ``py37-pkg`` [#f3]_. These use
   the 2.7, 3.5, 3.6 and 3.7 interpreters, respectively, to test all code in the
   documentation (both in Sphinx ``*.rst`` source files and in docstrings), run
   all unit tests, measure test coverage and re-build the exceptions
   documentation. To pass arguments to Py.test (the test runner) use a double
   dash (``--``) after all the Tox arguments, for example:

	.. code-block:: bash

	    $ tox -e py27-pkg -- -n 4
            GLOB sdist-make: .../pplot/setup.py
            py27-pkg inst-nodeps: .../pplot/.tox/dist/pplot-...zip
            ...

   Or use the :code:`-a` Setuptools optional argument followed by a quoted
   string with the arguments for Py.test. For example:

	.. code-block:: bash

	    $ python setup.py tests -a "-e py27-pkg -- -n 4"
            running tests
            ...

   There are other convenience environments defined for Tox [#f3]_:

    * ``py27-repl``, ``py35-repl``, ``py36-repl`` and ``py37-repl`` run the 2.7,
      3.5, 3.6 or 3.7 REPL, respectively, in the appropriate virtual
      environment. The ``pplot`` package is pip-installed by Tox when the
      environments are created.  Arguments to the interpreter can be passed in
      the command line after a double dash (``--``)

    * ``py27-test``, ``py35-test``, ``py36-test`` and ``py37-test`` run py.test
      using the Python 2.7, 3.5, Python 3.6 or Python 3.7 interpreter,
      respectively, in the appropriate virtual environment. Arguments to py.test
      can be passed in the command line after a double dash (``--``) , for
      example:

	.. code-block:: bash

	    $ tox -e py36-test -- -x test_pplot.py
            GLOB sdist-make: [...]/pplot/setup.py
            py36-test inst-nodeps: [...]/pplot/.tox/dist/pplot-1.1rc1.zip
            py36-test installed: -f file:[...]
            py36-test runtests: PYTHONHASHSEED='1264622266'
            py36-test runtests: commands[0] | [...]py.test -x test_pplot.py
            ===================== test session starts =====================
            platform linux -- Python 3.6.4, pytest-3.3.1, py-1.5.2, pluggy-0.6.0
            rootdir: [...]/pplot/.tox/py36/share/pplot/tests, inifile: pytest.ini
            plugins: xdist-1.21.0, forked-0.2, cov-2.5.1
            collected 414 items
            ...

    * ``py27-cov``, ``py35-cov``, ``py36-cov`` and ``py37-cov`` test code and
      branch coverage using the 2.7, 3.5, 3.6 or 3.7 interpreter, respectively,
      in the appropriate virtual environment. Arguments to py.test can be passed
      in the command line after a double dash (``--``). The report can be found
      in
      :bash:`${PPLOT_DIR}/.tox/py[PV]/usr/share/pplot/tests/htmlcov/index.html`
      where ``[PV]`` stands for ``27``, ``35``, ``36`` or ``37`` depending on
      the interpreter used

8. Verify that continuous integration tests pass. The package has continuous
   integration configured for Linux, Apple macOS and Microsoft Windows (all via
   `Azure DevOps <https://dev.azure.com/pmasdev>`_) Aggregation/cloud code
   coverage is configured via `Codecov <https://codecov.io>`_. It is assumed
   that the Codecov repository upload token in the build is stored in the
   :bash:`$(codecovToken)` environment variable (securely defined in the
   pipeline settings page).

9. Document the new feature or bug fix (if needed). The script
   :bash:`${PPLOT_DIR}/pypkg/build_docs.py` re-builds the whole package
   documentation (re-generates images, cogs source files, etc.):

	.. [[[cog pmisc.ste('build_docs.py -h', 0, mdir, cog.out) ]]]

	.. code-block:: bash

	    $ ${PKG_BIN_DIR}/build_docs.py -h
	    usage: build_docs.py [-h] [-d DIRECTORY] [-r]
	                         [-n NUM_CPUS] [-t]

	    Build pplot package documentation

	    optional arguments:
	      -h, --help            show this help message and exit
	      -d DIRECTORY, --directory DIRECTORY
	                            specify source file directory
	                            (default ../pplot)
	      -r, --rebuild         rebuild exceptions documentation.
	                            If no module name is given all
	                            modules with auto-generated
	                            exceptions documentation are
	                            rebuilt
	      -n NUM_CPUS, --num-cpus NUM_CPUS
	                            number of CPUs to use (default: 1)
	      -t, --test            diff original and rebuilt file(s)
	                            (exit code 0 indicates file(s) are
	                            identical, exit code 1 indicates
	                            file(s) are different)

	.. [[[end]]]

.. rubric:: Footnotes

.. [#f1] All examples are for the `bash <https://www.gnu.org/software/bash/>`_
   shell

.. [#f2] It is assumed that all the Python interpreters are in the executables
   path. Source code for the interpreters can be downloaded from Python's main
   `site <https://www.python.org/downloads/>`_

.. [#f3] Tox configuration largely inspired by
   `Ionel's codelog <https://blog.ionelmc.ro/2015/04/14/
   tox-tricks-and-patterns/>`_

.. include:: ../CHANGELOG.rst

License
=======

.. include:: ../LICENSE
