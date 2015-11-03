#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

# Generate data
FN_DATA=data-obj-age
FN_DATA_SORTED=$FN_DATA"-sorted"
if [ ! -f $FN_DATA_SORTED ];
then
	echo "Generating data ..."
	../../loadgen --test_obj_ages=plot/obj-age-when-accessed/$FN_DATA | sed 's/^/  /'
	echo

	echo "Sorting ..."
	time sort -n < $FN_DATA > $FN_DATA_SORTED
	echo
fi

# Plot
echo "Plotting ..."
export FN_IN=$SRC_DIR/$FN_DATA_SORTED
export FN_OUT=$SRC_DIR/obj-age.pdf
gnuplot $SRC_DIR/_obj-age.gnuplot
echo "Created "$FN_OUT
