#!/bin/bash
# rtest.sh
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details

opath=${PATH}
num_cpus=$(python -c "from __future__ import print_function; import multiprocessing; print(multiprocessing.cpu_count())")
export PATH=${HOME}/python/python2.7/bin:${HOME}/python/python3.5/bin:${HOME}/python/python3.6/bin:${PATH}
tox -- -n ${num_cpus} "$@"
export PATH=${opath}
