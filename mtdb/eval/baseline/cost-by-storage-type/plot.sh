#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

export FN_IN=$SRC_DIR/data
export FN_OUT=$SRC_DIR/storage-cost-by-types.pdf
gnuplot $SRC_DIR/storage-cost-by-types.gnuplot
printf "  Created %s %d\n" $FN_OUT `wc -c < $FN_OUT`
