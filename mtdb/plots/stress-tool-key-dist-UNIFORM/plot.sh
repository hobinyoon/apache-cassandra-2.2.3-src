#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

export FN_IN=$SRC_DIR/cass-stress-trace.log
export FN_OUT=$SRC_DIR/key-dist-by-time.pdf
gnuplot $SRC_DIR/_key-dist-by-time.gnuplot
echo "Created "$FN_OUT
