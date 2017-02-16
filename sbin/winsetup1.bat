REM [START IGNORE]
set PYTHON_MAJOR=2
set INTERP=py27
set PYVER=2.7
REM [STOP IGNORE]
REM install:
REM ###
REM # Set up environment variables
REM ###
set
set PYTHONCMD=python
set PIPCMD=pip
set PYTESTCMD=py.test
set REPO_DIR=%CD%
for %%i in (%REPO_DIR%) do @echo %%~ni> pkg_name.txt
set /p PKG_NAME=<pkg_name.txt
set RESULTS_DIR=%REPO_DIR%\results
set MAIN_REQUIREMENTS_FILE=%REPO_DIR%\requirements\main_%INTERP%.pip
set TESTS_REQUIREMENTS_FILE=%REPO_DIR%\requirements\tests_%INTERP%.pip
set DOCS_REQUIREMENTS_FILE=%REPO_DIR%\requirements\docs_%INTERP%.pip
set CITMP=%REPO_DIR%\CITMP
if not exist "%CITMP%" mkdir %CITMP%
echo "INTERP=%INTERP%"
echo "PKG_NAME=%PKG_NAME%"
echo "PYTHONCMD=%PYTHONCMD%"
echo "PIPCMD=%PIPCMD%"
echo "PYTESTCMD=%PYTESTCMD%"
echo "REPO_DIR=%REPO_DIR%"
echo "RESULTS_DIR=%RESULTS_DIR%"
echo "MAIN_REQUIREMENTS_FILE=%MAIN_REQUIREMENTS_FILE%"
echo "TESTS_REQUIREMENTS_FILE=%TESTS_REQUIREMENTS_FILE%"
echo "DOCS_REQUIREMENTS_FILE=%DOCS_REQUIREMENTS_FILE%"
echo "CITMP=%CITMP%"
REM ###
REM # Install tools and dependencies of package dependencies
REM ###
set PATH=C:\\Miniconda-x64;C:\\Miniconda-x64\\Scripts;%PATH%
conda update -y conda
conda env remove -y --name %INTERP%
conda create -y --name %INTERP% python=%PYVER% numpy scipy matplotlib
activate %INTERP%
which python
