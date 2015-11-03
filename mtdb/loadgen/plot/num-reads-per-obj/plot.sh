#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

# Generate data
FN_DATA=data-num-reads-per-obj
FN_DATA_SORTED=$FN_DATA"-sorted"
if [ ! -f $FN_DATA_SORTED ];
then
	echo "Generating data ..."
	../../loadgen --test_num_reads_per_obj=plot/num-reads-per-obj/$FN_DATA | sed 's/^/  /'
	echo

	echo "Sorting ..."
	time sort -n < $FN_DATA > $FN_DATA_SORTED
	echo
fi

# Plot
echo "Plotting ..."
export FN_IN=$SRC_DIR/$FN_DATA_SORTED
export FN_OUT=$SRC_DIR/num-reads-per-obj.pdf
time gnuplot $SRC_DIR/_num-reads-per-obj.gnuplot
echo "Created "$FN_OUT
