#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

# Generate data
FN_DATA=WRs
if [ ! -f $FN_DATA ];
then
	echo "Generating data ..."
	../../loadgen --dump=true --dumpfn=plot/write-reads-by-time/$FN_DATA --writes=50 | sed 's/^/  /'
fi

# Plot
export FN_IN=$SRC_DIR/$FN_DATA
export FN_OUT=$SRC_DIR/WRs.pdf
gnuplot $SRC_DIR/_WRs-by-time.gnuplot
echo "Created "$FN_OUT
