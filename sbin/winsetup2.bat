REM [START IGNORE]
set PYTHON_MAJOR=2
set INTERP=py27
set PYVER=2.7
REM [STOP IGNORE]
ps: wget https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py
python get-pip.py
pip install --upgrade pip wheel
pip install --upgrade --ignore-installed setuptools
which python
which pip
pip --version
python -c "import os, pip; print(os.path.dirname(os.path.realpath(pip.__path__[0])))" > python_site_packages_dir.txt
set /p PYTHON_SITE_PACKAGES=<python_site_packages_dir.txt
set VIRTUALENV_DIR=C:\Miniconda-x64\envs\%INTERP%
set BIN_DIR=%VIRTUALENV_DIR%\Scripts
set SOURCE_DIR=%PYTHON_SITE_PACKAGES%\%PKG_NAME%
set EXTRA_DIR=%VIRTUALENV_DIR%\share\%PKG_NAME%
set SBIN_DIR=%EXTRA_DIR%\sbin
set PYTHONPATH=%PYTHONPATH%;%PYTHON_SITE_PACKAGES%;%EXTRA_DIR%;%EXTRA_DIR%\tests;%EXTRA_DIR%\docs;%EXTRA_DIR%\docs\support
set TRACER_DIR=%EXTRA_DIR%\docs\support
set COV_FILE=%SOURCE_DIR%\.coveragerc_ci_%INTERP%
echo "PYTHON_SITE_PACKAGES=%PYTHON_SITE_PACKAGES%"
echo "VIRTUALENV_DIR=%VIRTUALENV_DIR%"
echo "BIN_DIR=%BINDIR%"
echo "SOURCE_DIR=%SOURCE_DIR%"
echo "EXTRA_DIR=%EXTRA_DIR%"
echo "SBIN_DIR=%SBIN_DIR%"
echo "PYTHONPATH=%PYTHONPATH%"
echo "TRACER_DIR=%TRACER_DIR%"
echo "COV_FILE=%COV_FILE%"
REM ###
REM # Install package dependencies
REM ###
set OLD_PTYHON_PATH=%PYTHONPATH%
set PYTHONPATH=%REPO_DIR%;%REPO_DIR%\sbin;%PYTHONPATH%
cd %REPO_DIR%
python %REPO_DIR%\sbin\gen_req_files.py freeze
pip install -r%MAIN_REQUIREMENTS_FILE%
pip install -r%TESTS_REQUIREMENTS_FILE%
pip install -r%DOCS_REQUIREMENTS_FILE%
pip freeze
REM ###
REM # Create directories for reports and artifacts
REM ###
if not exist "%RESULTS_DIR%\\testresults" mkdir %RESULTS_DIR%\testresults
if not exist "%RESULTS_DIR%\\codecoverage" mkdir %RESULTS_DIR%\codecoverage
if not exist "%RESULTS_DIR%\\artifacts" mkdir %RESULTS_DIR%\artifacts

REM build_script:
REM ###
REM # Install package
REM ###
type %REPO_DIR%\MANIFEST.in
REM # Fix Git symbolik links
python .\sbin\fix_windows_symlinks.py
python setup.py sdist --formats=zip
timeout /t 5
REM # Change directory away from repository, otherwise pip does not install package
set PYTHONPATH=%OLD_PTYHON_PATH%
python -c "import os, sys; sys.path.append(os.path.realpath('./'+os.environ['PKG_NAME']));import version; print(version.__version__)" > version.txt
set /p PKG_VERSION=<version.txt
echo "PKG_VERSION=%PKG_VERSION%"
cd %PYTHON_SITE_PACKAGES%
pip install --upgrade %REPO_DIR%\dist\%PKG_NAME%-%PKG_VERSION%.zip

REM ###
REM # sbin/wintest.bat file
REM ###
REM # Write coverage configuration file
REM ###
python %SBIN_DIR%\coveragerc_manager.py 'ci' 1 %INTERP% %PYTHON_SITE_PACKAGES%
type %COV_FILE%
if "%INTERP%" == "py26" python %SBIN_DIR%\patch_pylint.py %PYTHON_SITE_PACKAGES%
REM ###
REM # Change to tests sub-directory to mimic Tox conditions
REM ###
cd %EXTRA_DIR%\tests

REM test_script:
REM ###
REM # Run tests
REM ###
python -c "from __future__ import print_function; import multiprocessing; print(multiprocessing.cpu_count())" > num_cpus.txt
SET /p NUM_CPUS=<num_cpus.txt
ECHO "NUM_CPUS=%NUM_CPUS%"
REM # Omitted tests are not Windows-specific and are handled by Travis-CI
python %SBIN_DIR%\check_files_compliance.py -tps -d %SOURCE_DIR% -m %EXTRA_DIR%
REM # pylint 1.6.x appears to have a bug in Python 3.6 that is only going to be fixed with Pylint 2.0
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %SOURCE_DIR%
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %SBIN_DIR%
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %EXTRA_DIR%\tests
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %EXTRA_DIR%\docs\support
set DODOCTEST=1
py.test -n %NUM_CPUS% --collect-only --doctest-glob="*.rst" %EXTRA_DIR%\docs > doctest.log 2>&1 || set DODOCTEST=0
if %DODOCTEST%==1 py.test --doctest-glob="*.rst" %EXTRA_DIR%\docs
py.test -n %NUM_CPUS% --doctest-modules %SOURCE_DIR%
REM # Coverage tests runs all the unit tests, no need to run the non-coverage
REM # tests since the report is not being used
REM # - py.test -s -vv --junitxml=%RESULTS_DIR%\testresults\pytest.xml
py.test -n %NUM_CPUS% --cov-config %COV_FILE% --cov %SOURCE_DIR% --cov-report term
REM # Re-building exceptions auto-documentation takes a long time in Appveyor.
REM # They have (and should be) spot-checked every now and then
REM # - python %SBIN_DIR%\build_docs.py -r -t -d %SOURCE_DIR%

REM on_failure:
7z a %EXTRA_DIR%\artifacts_%INTERP%.zip %EXTRA_DIR%\artifacts\*.*
appveyor PushArtifact %EXTRA_DIR%\artifacts_%INTERP%.zip
