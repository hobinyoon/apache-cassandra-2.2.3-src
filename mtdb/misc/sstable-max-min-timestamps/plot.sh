#!/bin/bash

set -e
set -u

if [ "$#" -ne 1 ]; then
	echo "Usage: "$0" fn_in"
	echo "  E.g.: "$0" data"
	exit 1
fi

SRC_DIR=`dirname $BASH_SOURCE`

echo "Plotting ..."
export FN_IN=$1
export FN_OUT=sstable-max-min-timpstamps.pdf
gnuplot $SRC_DIR/_sstable-max-min-timestamps.gnuplot
echo "Created "$FN_OUT
