# fixtures.py
# Copyright (c) 2013-2017 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E0611,W0621

# Standard library imports
from __future__ import print_function
import os
import shutil
import subprocess
# PyPI imports
from PIL import Image
import numpy as np
import pytest
import scipy
from scipy.misc import imread
# Intra-package imports
import pplot


###
# Global variables
###
IMGTOL = 1e-3

###
# Fixtures
###
def compare_images(ref_fname, act_fname, no_print=True, isize=None):
    """ Compare two images by calculating Manhattan and Zero norms """
    # Source: http://stackoverflow.com/questions/189943/
    # how-can-i-quantify-difference-between-two-images
    ref_img = Image.open(ref_fname)
    act_img = Image.open(act_fname)
    if (ref_img.size != act_img.size) or ((isize and (act_img.size != isize))):
        m_norm, z_norm = 2*[2*IMGTOL]
    else:
        # Element-wise for Scipy arrays
        ref_img = imread(ref_fname).astype(float)
        act_img = imread(act_fname).astype(float)
        diff = ref_img-act_img
        # Manhattan norm
        m_norm = scipy.sum(np.abs(diff))
        # Zero norm
        z_norm = scipy.linalg.norm(diff.ravel(), 0)
    result = bool((m_norm < IMGTOL) and (z_norm < IMGTOL))
    if not no_print:
        print(
            'Image 1: {0}, Image 2: {1} -> ({2}, {3}) [{4}]'.format(
                ref_fname, act_fname, m_norm, z_norm, result
            )
        )
    return result


def compare_image_set(tmpdir, images_dict_list, section, isize=None):
    """ Compare image sets """
    subdir = 'test_images_{0}'.format(section)
    tmpdir.mkdir(subdir)
    global_result = True
    for images_dict in images_dict_list:
        ref_file_name_list = images_dict['ref_fname']
        test_file_name = images_dict['test_fname']
        print('Reference images:')
        for ref_file_name in ref_file_name_list:
            img_size = Image.open(ref_file_name).size
            print('   file://{0} {1}'.format(
                    os.path.realpath(ref_file_name),
                    img_size
                )
            )
        img_size = Image.open(test_file_name).size
        if isize:
            print('Extra size data: {0}'.format(isize))
        print('Actual image:')
        print('   file://{0} {1}'.format(
                os.path.realpath(test_file_name),
                img_size
            )
        )
        partial_result = []
        for ref_file_name in ref_file_name_list:
            partial_result.append(
                compare_images(ref_file_name, test_file_name, isize=isize)
            )
        result = any(partial_result)
        global_result = global_result and result
        if not result:
            print('Images do not match')
            export_image(test_file_name)
        print('')
    if global_result:
        try:
            tmpdir.remove(subdir)
        except OSError: # pragma: no cover
            pass
    return global_result


@pytest.fixture
def default_source():
    """
    Provides a default source to be used in testing the
    pplot.Series class
    """
    return pplot.BasicSource(
        indep_var=np.array([5, 6, 7, 8]),
        dep_var=np.array([0, -10, 5, 4])
    )


@pytest.fixture
def default_series(default_source):
    """
    Provides a default series object to be used in testing the
    pplot.Panel class
    """
    return pplot.Series(
        data_source=default_source,
        label='test series'
    )


@pytest.fixture
def default_panel(default_series):
    """
    Provides a default panel object to be used in testing the
    pplot.Figure class
    """
    return pplot.Panel(
        series=default_series,
        primary_axis_label='Primary axis',
        primary_axis_units='A',
        secondary_axis_label='Secondary axis',
        secondary_axis_units='B'
    )


def export_image(fname, method=True):
    tdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    artifact_dir = os.path.join(tdir, 'artifacts')
    if not os.path.exists(artifact_dir):
        os.makedirs(artifact_dir)
    if method:
        src = fname
        dst = os.path.join(artifact_dir, os.path.basename(fname))
        print('Copying image to {0}'.format(dst))
        shutil.copyfile(src, dst)
    else:
        if os.environ.get('APPVEYOR', None):
            proc = subprocess.Popen(
                ['appveyor', 'PushArtifact', os.path.realpath(fname)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            proc.communicate()
        elif os.environ.get('TRAVIS', None):
            # If only a few binary files need to be exported a hex dump works,
            # otherwise the log can grow past 4MB and the process is terminated
            # by Travis
            proc = subprocess.Popen(
                [
                    os.path.join(tdir, 'sbin', 'png-to-console.sh'),
                    os.path.realpath(fname)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, _ = proc.communicate()
            print(stdout)

@pytest.fixture
def negative_panel():
    """
    Provides a panel with series containing negative data to be used in testing
    the pplot.Figure class
    """
    negative_data_source = pplot.BasicSource(
        indep_var=np.array([-5, 6, 7, 8]),
        dep_var=np.array([0.1, 10, 5, 4])
    )
    negative_series = pplot.Series(
        data_source=negative_data_source, label='negative data series'
    )
    return pplot.Panel(series=negative_series)
