#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

#export FN_IN=$SRC_DIR/read-keys
export FN_IN=$SRC_DIR/read-keys-1
export FN_OUT=$SRC_DIR/read-keys-dist.pdf
gnuplot $SRC_DIR/_key-dist.gnuplot
echo "Created "$FN_OUT
