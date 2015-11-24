#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

cmd="cat"
for ((i=1; i <= 17; i++ ))
do
	cmd+=" keys-$i"
done

cmd+=" | sort | uniq | wc -l"
echo $cmd

eval $cmd
