#!/bin/bash

HOSTNAME=`hostname`
DATETIME=`date +"%y%m%d-%H%M%S"`

FN_PREFIX="data/"$HOSTNAME"."$DATETIME"."

DN_LOCAL_SSD=/mnt/local-ssd
DN_EBS_SSD=/mnt/ebs-ssd-gp2
DN_EBS_MAG=/mnt/ebs-mag

# Create test files
# time dd bs=1024 count=262144 < /dev/urandom > $DN_LOCAL_SSD/ioping-test \
# && time cp $DN_LOCAL_SSD/ioping-test $DN_EBS_SSD/ioping-test \
# && time cp $DN_LOCAL_SSD/ioping-test $DN_EBS_MAG/ioping-test

# Measure direct IO latencies. Cwd should be on local ssd.
time ioping -D -c 1000 -i 0.0001 $DN_LOCAL_SSD/ioping-test > $FN_PREFIX"local-ssd-direct"
time ioping -C -c 1000 -i 0.0001 $DN_LOCAL_SSD/ioping-test > $FN_PREFIX"local-ssd-cached"

time ioping -D -c 1000 -i 0.0001 $DN_EBS_SSD/ioping-test > $FN_PREFIX"ebs-ssd-gp2-direct"
time ioping -C -c 1000 -i 0.0001 $DN_EBS_SSD/ioping-test > $FN_PREFIX"ebs-ssd-gp2-cached"

time ioping -D -c 1000 -i 0.0001 $DN_EBS_MAG/ioping-test > $FN_PREFIX"ebs-mag-direct"
time ioping -C -c 1000 -i 0.0001 $DN_EBS_MAG/ioping-test > $FN_PREFIX"ebs-mag-cached"
