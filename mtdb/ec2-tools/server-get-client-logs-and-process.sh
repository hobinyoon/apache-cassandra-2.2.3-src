#!/bin/bash

set -e
set -u
set -x

killall pressure-memory > /dev/null 2>&1 || true
sudo killall collectl > /dev/null 2>&1 || true
sudo killall mon-num-cass-threads.sh > /dev/null 2>&1 || true
rsync -ave "ssh -o StrictHostKeyChecking=no" $CASSANDRA_CLIENT_ADDR:work/cassandra/mtdb/logs/loadgen ~/work/cassandra/mtdb/logs
cd ~/work/cassandra/mtdb/process-log/calc-cost-latency-plot-tablet-timeline
\rm *.pdf >/dev/null 2>&1 || true
./plot-cost-latency-tablet-timelines.py
du -hs ~/work/cassandra/data/
