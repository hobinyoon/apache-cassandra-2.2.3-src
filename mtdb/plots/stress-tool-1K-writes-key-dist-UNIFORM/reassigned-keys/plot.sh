#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

export FN_IN=$SRC_DIR/keys-sequential
export FN_OUT=$SRC_DIR/write-keys-dist.pdf
gnuplot $SRC_DIR/_key-dist.gnuplot
echo "Created "$FN_OUT
