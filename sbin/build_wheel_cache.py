#!/usr/bin/env python
# build_wheel_cache.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import argparse
import os
import subprocess
import sys
import warnings
# Intra-package imports
from sbin.functions import SUPPORTED_VERS


###
# Global variables
###
COMP_FLAGS = ['CFLAGS', 'CXXFLAGS', 'LDFLAGS']

###
# Functions
###
# This is a sub-set of the pmisc.pcolor function, repeated here because
# this script may be run right after cloning and peng module may not be in
# the Python search path
def _os_cmd(cmd, quiet=False):
    """ Execute shell command and display standard output """
    env = os.environ.copy()
    for flag in COMP_FLAGS:
        env[flag] = ''
    if not quiet:
        print(' '.join(cmd))
    pobj = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env
    )
    stdout, _ = pobj.communicate()
    if not quiet:
        print(stdout)
    return pobj.returncode


def _pcolor(text, color, indent=0):
    """ Colorized print to standard output """
    esc_dict = {
        'black':30, 'red':31, 'green':32, 'yellow':33, 'blue':34, 'magenta':35,
        'cyan':36, 'white':37, 'none':-1
    }
    if esc_dict[color] != -1:
        return (
            '\033[{color_code}m{indent}{text}\033[0m'.format(
                color_code=esc_dict[color],
                indent=' '*indent,
                text=text
            )
        )
    return '{indent}{text}'.format(indent=' '*indent, text=text)


def _pip_install(pyver, pkg_name, quiet=False, upgrade=False):
    """ Install package via pip """
    cmd = (
        ['pip{0}'.format(pyver), 'install']+
        (['--upgrade'] if upgrade else [])+
        (['--quiet'] if quiet else [])+
        ['--force-reinstall', pkg_name]
    )
    return _os_cmd(cmd, quiet)


def build_wheel_cache(args):
    """ Build pip wheel cache """
    # pylint: disable=R0912,R0914
    exitfirst = args.exitfirst
    quiet = args.quiet
    pyvers = [item.strip() for item in args.versions.split(',')]
    pkg_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    old_python_path = os.environ['PYTHONPATH']
    template = 'Building {0} wheel cache for Python {1}'
    for pyver in pyvers:
        pycmd = which('python{0}'.format(pyver))
        if not pycmd:
            print('Python {0} not found'.format(pyver))
            if exitfirst:
                sys.exit(1)
            continue
        pipcmd = which('pip{0}'.format(pyver))
        if not pipcmd:
            print('pip {0} not found'.format(pyver))
            if exitfirst:
                sys.exit(1)
            continue
        if not quiet:
            print('Python interpreter: {0}'.format(pycmd))
            print('pip: {0}'.format(pipcmd))
        os.environ['PYTHONPATH'] = ''
        lines = load_requirements(pkg_dir, pyver)
        for line in lines:
            if 'numpy' in line:
                numpy_line = line
                break
        else:
            raise RuntimeError('Numpy dependency could not be found')
        # Numpy appears to error out during importing if nose is not
        # pre-installed, apparently, it is not part of their dependency tree
        if pyver == '2.6':
            retcode = _pip_install(pyver, 'nose', quiet)
            if retcode and exitfirst:
                sys.exit(1)
        for line in lines:
            print(_pcolor(template.format(line, pyver), 'cyan'))
            const_line = []
            if ('scipy' in line) or ('matplotlib' in line):
                # Install numpy before scipy otherwise pip throws an exception
                retcode = _pip_install(pyver, numpy_line.strip(), quiet, True)
                if retcode and exitfirst:
                    sys.exit(1)
                # Create constraint file, scipy and/or matplotlib may try to
                # build a version of numpy that is newer than the one in the
                # requirements file
                fname = os.path.join(
                    pkg_dir, 'requirements', 'constraints.pip'
                )
                const_line = ['--constraint', fname]
                with open(fname, 'w') as fhandle:
                    fhandle.write(numpy_line)
            retcode = _os_cmd(
                ['pip{0}'.format(pyver)]+(['--quiet'] if quiet else [])+
                ['wheel']+const_line+[line],
                quiet
            )
            if const_line:
                os.remove(fname)
            if retcode and exitfirst:
                sys.exit(1)
        os.environ['PYTHONPATH'] = old_python_path


def check_flags():
    """ Check that certain environment variables are not set """
    envs = []
    for flag in COMP_FLAGS:
        envs += [flag] if os.environ.get(flag, None) else []
    if envs:
        letter = 's' if len(envs) > 1 else ''
        pron = 'are' if len(envs) > 1 else 'is'
        fjoint = ', '.join(envs)
        msg = (
            'Environment variable'+letter+' '+fjoint+' '+pron+' defined, '
            'this could cause problems with the compilation of certain '
            'packages'
        )
        warnings.warn(msg)


def load_requirements(pkg_dir, pyver):
    """ Get package names from requirements.txt file """
    pyver = pyver.replace('.', '')
    reqs_dir = os.path.join(pkg_dir, 'requirements')
    reqs_files = [
        'main_py{0}.pip'.format(pyver),
        'tests_py{0}.pip'.format(pyver),
        'docs_py{0}.pip'.format(pyver),
    ]
    ret = []
    for rfile in [os.path.join(reqs_dir, item) for item in reqs_files]:
        with open(os.path.join(reqs_dir, rfile), 'r') as fobj:
            lines = [
                item.strip() for item in fobj.readlines() if item.strip()
            ]
        ret.extend(lines)
    return ret


def valid_pyver(value):
    """ Argparse checker for Python interpreter version """
    value = value[0] if isinstance(value, list) else value
    tokens = [item.strip() for item in value.split(',')]
    for token in tokens:
        if token not in SUPPORTED_VERS:
            raise argparse.ArgumentTypeError(
                'invalid Python interpreter version: {0}'.format(token)
            )
    return ', '.join(tokens)


def which(name):
    """ Search PATH for executable files with the given name """
    # Inspired by https://twistedmatrix.com/trac/browser/tags/releases/
    # twisted-8.2.0/twisted/python/procutils.py
    # pylint: disable=W0141
    result = []
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for pdir in os.environ.get('PATH', '').split(os.pathsep):
        fname = os.path.join(pdir, name)
        if os.path.isfile(fname) and os.access(fname, os.X_OK):
            result.append(fname)
    return result[0] if result else None


if __name__ == '__main__':
    PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PARSER = argparse.ArgumentParser(
        description='Build peng dependency wheels'
    )
    PARSER.add_argument(
        '-x', '--exitfirst',
        help='exit instantly on first error',
        action="store_true"
    )
    PARSER.add_argument(
        '-q', '--quiet',
        help='decrease verbosity',
        action="store_true"
    )
    PARSER.add_argument(
        '-v', '--versions',
        help='Python interpreter version(s)',
        type=valid_pyver,
        default=', '.join(SUPPORTED_VERS)
    )
    ARGS = PARSER.parse_args()
    check_flags()
    build_wheel_cache(ARGS)
