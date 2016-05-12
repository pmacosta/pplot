.. README.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details


.. image:: https://badge.fury.io/py/pplot.svg
    :target: https://pypi.python.org/pypi/pplot
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/l/pplot.svg
    :target: https://pypi.python.org/pypi/pplot
    :alt: License

.. image:: https://img.shields.io/pypi/pyversions/pplot.svg
    :target: https://pypi.python.org/pypi/pplot
    :alt: Python versions supported

.. image:: https://img.shields.io/pypi/format/pplot.svg
    :target: https://pypi.python.org/pypi/pplot
    :alt: Format

|

.. image::
   https://travis-ci.org/pmacosta/pplot.svg?branch=master

.. image::
   https://ci.appveyor.com/api/projects/status/
   7dpk342kxs8kcg5t/branch/master?svg=true
   :alt: Windows continuous integration

.. image::
   https://codecov.io/github/pmacosta/pplot/coverage.svg?branch=master
   :target: https://codecov.io/github/pmacosta/pplot?branch=master
   :alt: Continuous integration coverage

.. image::
   https://readthedocs.org/projects/pip/badge/?version=stable
   :target: http://pip.readthedocs.org/en/stable/?badge=stable
   :alt: Documentation status

|

Description
===========

.. role:: bash(code)
	:language: bash

.. [[[cog
.. import os, sys
.. from docs.support.term_echo import ste
.. file_name = sys.modules['docs.support.term_echo'].__file__
.. mdir = os.path.realpath(
..     os.path.dirname(os.path.dirname(os.path.dirname(file_name)))
.. )
.. import docs.support.requirements_to_rst
.. docs.support.requirements_to_rst.def_links(cog)
.. ]]]
.. _Astroid: https://bitbucket.org/logilab/astroid
.. _Cog: http://nedbatchelder.com/code/cog
.. _Coverage: http://coverage.readthedocs.org/en/coverage-4.0a5
.. _Decorator: https://pythonhosted.org/decorator
.. _Docutils: http://docutils.sourceforge.net/docs
.. _Funcsigs: https://pypi.python.org/pypi/funcsigs
.. _Matplotlib: http://matplotlib.org
.. _Mock: http://www.voidspace.org.uk/python/mock
.. _Nose: http://nose.readthedocs.org
.. _Numpy: http://www.numpy.org
.. _Pcsv: http://pcsv.readthedocs.org
.. _Peng: http://peng.readthedocs.org
.. _Pexdoc: http://pexdoc.readthedocs.org
.. _Pillow: https://python-pillow.github.io
.. _Pmisc: http://pmisc.readthedocs.org
.. _PyContracts: https://andreacensi.github.io/contracts
.. _Pylint: http://www.pylint.org
.. _PyParsing: http://pyparsing.wikispaces.com/
.. _Py.test: http://pytest.org
.. _Pytest-coverage: https://pypi.python.org/pypi/pytest-cov
.. _Pytest-xdist: https://pypi.python.org/pypi/pytest-xdist
.. _Scipy: http://www.scipy.org
.. _Six: https://pythonhosted.org/six
.. _Sphinx: http://sphinx-doc.org
.. _ReadTheDocs Sphinx theme: https://github.com/snide/sphinx_rtd_theme
.. _Inline Syntax Highlight Sphinx Extension:
   https://bitbucket.org/klorenz/sphinxcontrib-inlinesyntaxhighlight
.. _Tox: https://testrun.org/tox
.. _Virtualenv: http://docs.python-guide.org/en/latest/dev/virtualenvs
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

.. figure:: ./support/Class_hierarchy_example.png
   :scale: 100%

**Figure 1:** Example diagram of the class hierarchy of a figure. In
this particular example the figure consists of 3 panels. Panel 1 has a
series whose data comes from a basic source, panel 2 has three series, two
of which come from comma-separated values (CSV) files and one that comes
from a basic source. Panel 3 has one series whose data comes from a basic
source.

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
    :lines: 1,6-10,19-119

|

.. csv-table:: data.csv file
   :file: ./support/data.csv
   :header-rows: 1

|

.. figure:: ./support/plot_example_1.png
   :scale: 100%

**Figure 2:** plot_example_1.png generated by plot_example_1.py

|

Interpreter
===========

The package has been developed and tested with Python 2.6, 2.7, 3.3, 3.4
and 3.5 under Linux (Debian, Ubuntu), Apple OS X and Microsoft Windows

Installing
==========

.. code-block:: bash

	$ pip install pplot

Documentation
=============

Available at `Read the Docs <https://pplot.readthedocs.org>`_

Contributing
============

1. Abide by the adopted `code of conduct
   <http://contributor-covenant.org/version/1/3/0>`_

2. Fork the `repository <https://github.com/pmacosta/pplot>`_ from
   GitHub and then clone personal copy [#f1]_:

	.. code-block:: bash

		$ git clone \
		      https://github.com/[github-user-name]/pplot.git
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

		$ ${PPLOT_DIR}/sbin/complete-cloning.sh
                Installing Git hooks
                Building pplot package documentation
                ...

4. Ensure that the Python interpreter can find the package modules
   (update the :bash:`$PYTHONPATH` environment variable, or use
   `sys.paths() <https://docs.python.org/2/library/sys.html#sys.path>`_,
   etc.)

	.. code-block:: bash

		$ export PYTHONPATH=${PYTHONPATH}:${PPLOT_DIR}

5. Install the dependencies (if needed, done automatically by pip):

    .. [[[cog
    .. import docs.support.requirements_to_rst
    .. docs.support.requirements_to_rst.proc_requirements(cog)
    .. ]]]


    * `Astroid`_ (Python 2.6: older than 1.4, Python 2.7 or newer: 1.3.8
      or newer)

    * `Cog`_ (2.4 or newer)

    * `Coverage`_ (3.7.1 or newer)

    * `Decorator`_ (3.4.2 or newer)

    * `Docutils`_ (0.12 or newer)

    * `Funcsigs`_ (Python 2.x only, 0.4 or newer)

    * `Inline Syntax Highlight Sphinx Extension`_ (0.2 or newer)

    * `Matplotlib`_ (1.4.1 or newer)

    * `Mock`_ (Python 2.x only, 1.0.1 or newer)

    * `Nose`_ (Python 2.6: 1.0.0 or newer)

    * `Numpy`_ (1.8.2 or newer)

    * `Pcsv`_ (1.0.0 or newer)

    * `Peng`_ (1.0.0 or newer)

    * `Pexdoc`_ (1.0.0 or newer)

    * `Pillow`_ (2.6.1 or newer)

    * `Pmisc`_ (1.0.0 or newer)

    * `Py.test`_ (2.7.0 or newer)

    * `PyContracts`_ (1.7.2 or newer except 1.7.7)

    * `PyParsing`_ (2.0.7 or newer)

    * `Pylint`_ (Python 2.6: 1.3 or newer and older than 1.4, Python 2.7
      or newer: 1.3.1 or newer)

    * `Pytest-coverage`_ (1.8.0 or newer)

    * `Pytest-xdist`_ (optional, 1.8.0 or newer)

    * `ReadTheDocs Sphinx theme`_ (0.1.9 or newer)

    * `Scipy`_ (0.13.3 or newer)

    * `Six`_ (1.4.0 or newer)

    * `Sphinx`_ (1.2.3 or newer)

    * `Tox`_ (1.9.0 or newer)

    * `Virtualenv`_ (13.1.2 or newer)

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
   (Tox is configured as its virtual environment manager) [#f2]_:

	.. code-block:: bash

	    $ python setup.py tests
            running tests
            running egg_info
            writing requirements to pplot.egg-info/requires.txt
            writing pplot.egg-info/PKG-INFO
            ...

   Tox (or Setuptools via Tox) runs with the following default environments:
   ``py26-pkg``, ``py27-pkg``, ``py33-pkg``, ``py34-pkg`` and ``py35-pkg``
   [#f3]_. These use the Python 2.6, 2.7, 3.3, 3.4 and 3.5 interpreters,
   respectively, to test all code in the documentation (both in Sphinx
   ``*.rst`` source files and in docstrings), run all unit tests, measure test
   coverage and re-build the exceptions documentation. To pass arguments to
   Py.test (the test runner) use a double dash (``--``) after all the Tox
   arguments, for example:

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

   There are other convenience environments defined for Tox [#f4]_:

    * ``py26-repl``, ``py27-repl``, ``py33-repl``, ``py34-repl`` and
      ``py35-repl`` run the Python 2.6, 2.7, 3.3, 3.4 or 3.5 REPL,
      respectively, in the appropriate virtual environment. The ``pplot``
      package is pip-installed by Tox when the environments are created.
      Arguments to the interpreter can be passed in the command line
      after a double dash (``--``)

    * ``py26-test``, ``py27-test``, ``py33-test``, ``py34-test`` and
      ``py35-test`` run py.test using the Python 2.6, 2.7, 3.3, 3.4
      or Python 3.5 interpreter, respectively, in the appropriate virtual
      environment. Arguments to py.test can be passed in the command line
      after a double dash (``--``) , for example:

	.. code-block:: bash

	    $ tox -e py34-test -- -x test_pplot.py
            GLOB sdist-make: [...]/pplot/setup.py
            py34-test inst-nodeps: [...]/pplot/.tox/dist/pplot-[...].zip
            py34-test runtests: PYTHONHASHSEED='680528711'
            py34-test runtests: commands[0] | [...]py.test -x test_pplot.py
            ===================== test session starts =====================
            platform linux -- Python 3.4.2 -- py-1.4.30 -- [...]
            ...

    * ``py26-cov``, ``py27-cov``, ``py33-cov``, ``py34-cov`` and
      ``py35-cov`` test code and branch coverage using the Python 2.6,
      2.7, 3.3, 3.4 or 3.5 interpreter, respectively, in the appropriate
      virtual environment. Arguments to py.test can be passed in the command
      line after a double dash (``--``). The report can be found in
      :bash:`${PPLOT_DIR}/.tox/py[PV]/usr/share/pplot/tests/htmlcov/index.html`
      where ``[PV]`` stands for ``26``, ``27``, ``33``, ``34`` or ``35``
      depending on the interpreter used

8. Verify that continuous integration tests pass. The package has continuous
   integration configured for Linux (via `Travis <http://www.travis-ci.org>`_)
   and for Microsoft Windows (via `Appveyor <http://www.appveyor.com>`_).
   Aggregation/cloud code coverage is configured via
   `Codecov <https://codecov.io>`_. It is assumed that the Codecov repository
   upload token in the Travis build is stored in the :bash:`${CODECOV_TOKEN}`
   environment variable (securely defined in the Travis repository settings
   page). Travis build artifacts can be transferred to Dropbox using the
   `Dropbox Uploader <https://github.com/andreafabrizi/Dropbox-Uploader>`_
   script (included for convenience in the :bash:`${PPLOT_DIR}/sbin` directory).
   For an automatic transfer that does not require manual entering of
   authentication credentials place the APPKEY, APPSECRET, ACCESS_LEVEL,
   OAUTH_ACCESS_TOKEN and OAUTH_ACCESS_TOKEN_SECRET values required by
   Dropbox Uploader in the in the :bash:`${DBU_APPKEY}`,
   :bash:`${DBU_APPSECRET}`, :bash:`${DBU_ACCESS_LEVEL}`,
   :bash:`${DBU_OAUTH_ACCESS_TOKEN}` and
   :bash:`${DBU_OAUTH_ACCESS_TOKEN_SECRET}` environment variables,
   respectively (also securely defined in Travis repository settings page)


9. Document the new feature or bug fix (if needed). The script
   :bash:`${PPLOT_DIR}/sbin/build_docs.py` re-builds the whole package
   documentation (re-generates images, cogs source files, etc.):

	.. [[[cog ste('build_docs.py -h', 0, mdir, cog.out) ]]]

	.. code-block:: bash

	    $ ${PUTIL_DIR}/sbin/build_docs.py -h
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

    Output of shell commands can be automatically included in reStructuredText
    source files with the help of Cog_ and the :code:`docs.support.term_echo` module.

    .. autofunction:: docs.support.term_echo.ste
        :noindex:

    .. autofunction:: docs.support.term_echo.term_echo
        :noindex:

    Similarly Python files can be included in docstrings with the help of Cog_
    and the :code:`docs.support.incfile` module

    .. autofunction:: docs.support.incfile.incfile
        :noindex:

.. rubric:: Footnotes

.. [#f1] All examples are for the `bash <https://www.gnu.org/software/bash/>`_
   shell

.. [#f2] It appears that Scipy dependencies do not include Numpy (as they
   should) so running the tests via Setuptools will typically result in an
   error. The pplot requirement file specifies Numpy before Scipy and this
   installation order is honored by Tox so running the tests via Tox sidesteps
   Scipy's broken dependency problem but requires Tox to be installed before
   running the tests (Setuptools installs Tox if needed)

.. [#f3] It is assumed that all the Python interpreters are in the executables
   path. Source code for the interpreters can be downloaded from Python's main
   `site <http://www.python.org/downloads>`_

.. [#f4] Tox configuration largely inspired by
   `Ionel's codelog <http://blog.ionelmc.ro/2015/04/14/
   tox-tricks-and-patterns/>`_

.. include:: ../CHANGELOG.rst

License
=======

.. include:: ../LICENSE