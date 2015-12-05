#!/bin/bash

set -e
set -u

if [ "$#" -ne 1 ]; then
	echo "Usage: "$0" fn_in_datetime"
	echo "  E.g.: "$0" 151120-1407"
	exit 1
fi

FN_IN_DATETIME=$1
SIMULATED_TIME_IN_YEAR=8
SRC_DIR=`dirname $BASH_SOURCE`

echo "Generating data for plotting ..."
./_gen-data-for-plot.py ../data/$FN_IN_DATETIME $SIMULATED_TIME_IN_YEAR | sed 's/^/  /'
if [ "${PIPESTATUS[0]}" -ne "0" ]; then
	exit 1
fi

echo
echo "Plotting ..."
export FN_IN=$SRC_DIR/../data/$FN_IN_DATETIME"-by-sstables-by-time"
export FN_OUT=$SRC_DIR/"sstable-accesses-by-time-"$FN_IN_DATETIME".pdf"
export FN_OUT_LOGSCALE=$SRC_DIR/"sstable-accesses-by-time-logscale-"$FN_IN_DATETIME".pdf"
gnuplot $SRC_DIR/_sstable-accesses-by-time.gnuplot | sed 's/^/  /'
if [ "${PIPESTATUS[0]}" -ne "0" ]; then
	exit 1
fi
printf "  Created %s %d\n" $FN_OUT `wc -c < $FN_OUT`
printf "  Created %s %d\n" $FN_OUT_LOGSCALE `wc -c < $FN_OUT_LOGSCALE`
