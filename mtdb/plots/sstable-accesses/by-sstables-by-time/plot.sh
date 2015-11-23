#!/bin/bash

set -e
set -u

if [ "$#" -ne 1 ]; then
	echo "Usage: "$0" fn_in_datetime"
	echo "  E.g.: "$0" 151120-1407"
	exit 1
fi

FN_IN_DATETIME=$1
SRC_DIR=`dirname $BASH_SOURCE`

echo "Generating data for plotting ..."
./_gen-data-for-plot.py ../data/$FN_IN_DATETIME

echo
echo "Plotting ..."
export FN_IN=$SRC_DIR/../data/$FN_IN_DATETIME"-formatted"
export FN_OUT=$SRC_DIR/"sstable-accesses-by-time-"$FN_IN_DATETIME".pdf"
gnuplot $SRC_DIR/_sstable-accesses-by-time.gnuplot
echo "Created "$FN_OUT
