#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

time sort -n < num-reads-per-obj > num-reads-per-obj-sorted

export FN_IN=$SRC_DIR/num-reads-per-obj-sorted
export FN_OUT=$SRC_DIR/num-reads-per-obj.pdf
gnuplot $SRC_DIR/_num-reads-per-obj.gnuplot
echo "Created "$FN_OUT
