#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

time sort -k 1 -n < obj-age > obj-age-sorted

export FN_IN=$SRC_DIR/obj-age-sorted
export FN_OUT=$SRC_DIR/obj-age.pdf
gnuplot $SRC_DIR/_obj-age.gnuplot
echo "Created "$FN_OUT
