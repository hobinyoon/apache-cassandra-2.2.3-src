#!/bin/bash

set -e
set -u

# Verbose
set -v

SRC_DIR=`dirname $BASH_SOURCE`

FN_W=$SRC_DIR/../write/write-keys
FN_R=$SRC_DIR/../read/read-keys-1000000

sort -n < $FN_W | uniq > w-unique
sort -n < $FN_R | uniq > r-unique

diff -u w-unique r-unique > w-r-diff
