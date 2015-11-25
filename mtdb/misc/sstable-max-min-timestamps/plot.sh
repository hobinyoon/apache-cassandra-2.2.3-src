#!/bin/bash

set -e
set -u

if [ "$#" -ne 1 ]; then
	echo "Usage: "$0" fn_in"
	echo "  E.g.: "$0" data"
	exit 1
fi

SRC_DIR=`dirname $BASH_SOURCE`
FN_IN_1=$1
FN_OUT_1=$FN_IN_1"-ts-converted"

echo "Converting timestamp to datetime ..."
pushd convert > /dev/null
ant build | sed 's/^/  /'
echo
java ConvertTsToDatetime "../"$FN_IN_1 "../"$FN_OUT_1 | sed  's/^/  /'
popd > /dev/null

echo
echo "Plotting ..."
export FN_IN=$FN_OUT_1
export FN_OUT=sstable-max-min-timpstamps.pdf
gnuplot $SRC_DIR/_sstable-max-min-timestamps.gnuplot | sed  's/^/  /'
echo "  Created "$FN_OUT
