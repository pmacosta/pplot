#!/bin/bash
# shellcheck disable=SC1090,SC1091
# build-tags.sh
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details

#
#/ build-tags.sh
#/ Usage:
#/   build-tags.sh -h
#/   build-tags.sh
#/ Options:
#/   -h  show this help message and exit


source "$(dirname "${BASH_SOURCE[0]}")/functions.sh"
pkg_dir=$(dirname "$(current_dir "${BASH_SOURCE[0]}")")
sname=$(basename "$0")

if [ "${BASH_SOURCE[0]}" != "$0" ]; then
    exit 0
fi
### Unofficial strict mode
set -euo pipefail
IFS=$'\n\t'
### Help message
usage() { grep '^#/' "$0" | cut -c4- ; }
### Parse arguments
OPTIND=1
while getopts ":h" opt; do
	case ${opt} in
		h)
			usage
			exit 0
			;;
		\?)
            echo -e "${sname}: invalid option -${OPTARG}\n" >&2
			usage
			exit 1
			;;
	esac
done
shift $((OPTIND - 1))
if [ "$#" != 0 ]; then
    echo "${sname}: invalid number of arguments"
	exit 1
fi

sdirs=$(\
    find \
    "${pkg_dir}" \
    -path "${pkg_dir}/.tox" -prune \
    -o -name "*.py" \
    -exec dirname {} + | \
    sort -u \
)
fdirs=()
for sdir in ${sdirs[*]}; do
    fdirs+=("$(readlink -f "${sdir}")")
done
cmd="ctags -V --tag-relative -f ${pkg_dir}/tags -R"
for fdir in ${fdirs[*]}; do
    cmd="${cmd} \"${fdir}\"/*.py"
done
eval "${cmd}"
