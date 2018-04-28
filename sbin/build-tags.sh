#!/bin/bash
# build-tags.sh
# Copyright (c) 2013-2018 Pablo Acosta-Serafini
# See LICENSE for details

source $(dirname "${BASH_SOURCE[0]}")/functions.sh

print_usage_message () {
	echo -e "build-tags.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  build-tags.sh -h" >&2
	echo -e "  build-tags.sh\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  show this help message and exit" >&2
}

pkg_dir=$(dirname $(current_dir "${BASH_SOURCE[0]}"))
pkg_name=$(basename "${pkg_dir}")

# Read command line options
while getopts ":h" opt; do
	case ${opt} in
		h)
			print_usage_message
			exit 0
			;;
		\?)
			echo "build-tags.sh: invalid option" >&2
			print_usage_message
			exit 1
			;;
	esac
done
shift $((OPTIND - 1))
if [ "$#" != 0 ]; then
	echo "build-tags.sh: too many command line arguments" >&2
	exit 1
fi

sdirs=$(find . -name "*.py" -exec dirname {} + | sort -u )
fdirs=()
for sdir in ${sdirs[*]}; do
    fdirs+=("$(readlink -f "${sdir}")")
done
cmd="ctags -V --tag-relative -f ${pkg_dir}/tags -R"
for fdir in ${fdirs[*]}; do
    cmd="${cmd} ${fdir}/*.py"
done
eval "${cmd}"
