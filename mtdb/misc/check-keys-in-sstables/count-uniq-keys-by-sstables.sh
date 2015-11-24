#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

for ((i=1; i <= 17; i++ ))
do
	NUM_KEYS=`cat keys-$i | wc -l`
	NUM_UNIQ_KEYS=`sort < keys-$i | uniq | wc -l`
	printf "%d %s %s\n" $i $NUM_KEYS $NUM_UNIQ_KEYS
done
