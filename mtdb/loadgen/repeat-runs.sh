#!/bin/bash

set -e
set -u

if [[ $# -ne 1 ]]; then
	printf "Usage: %s num_runs\n" $0
	exit 1
fi
NUM_RUNS=$1

printf "NUM_RUNS=%d\n" $NUM_RUNS
SRC_DIR=`dirname $BASH_SOURCE`
PROCESS_LOG_DIR=$SRC_DIR"/../process-log/calc-cost-latency-plot-tablet-timeline"
#echo $PROCESS_LOG_DIR
pushd $SRC_DIR > /dev/null

for ((i=0; i<$NUM_RUNS; i++)); do
	printf "i=%d\n" $i
	./create-db.sh
	./loadgen

	pushd $PROCESS_LOG_DIR > /dev/null
	./plot-cost-latency-tablet-timelines.py
	popd > /dev/null
done
