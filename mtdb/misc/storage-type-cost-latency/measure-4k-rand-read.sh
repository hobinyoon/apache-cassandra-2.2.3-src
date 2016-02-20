#!/bin/bash

HOSTNAME=`hostname`
DATETIME=`date +"%y%m%d-%H%M%S"`
echo $DATETIME

FN_PREFIX="data/"$HOSTNAME"."$DATETIME"."

DN_LOCAL_SSD=/mnt/local-ssd
DN_EBS_SSD_GP2=/mnt/ebs-ssd-gp2
#DN_EBS_SSD_IOP=/mnt/ebs-ssd-iop
DN_EBS_MAG=/mnt/ebs-mag

# Create test files
#echo "Creating test files ..."
#time dd bs=1024 count=262144 < /dev/urandom > $DN_LOCAL_SSD/ioping-test \
#&& time cp $DN_LOCAL_SSD/ioping-test $DN_EBS_SSD_GP2/ioping-test \
#&& time cp $DN_LOCAL_SSD/ioping-test $DN_EBS_MAG/ioping-test
## && time cp $DN_LOCAL_SSD/ioping-test $DN_EBS_SSD_IOP/ioping-test \

#ioping -D -c 1000 -i 0.0001 $DN_LOCAL_SSD/ioping-test > $FN_PREFIX"local-ssd-direct"
#ioping -D -c 1000 -i 0.0001 $DN_EBS_SSD_GP2/ioping-test > $FN_PREFIX"ebs-ssd-gp2-direct"
#ioping -D -c 1000 -i 0.0001 $DN_EBS_SSD_IOP/ioping-test > $FN_PREFIX"ebs-ssd-gp2-direct"

## Cwd should be on local ssd.
#echo
#echo "Measuing direct/cached IO latencies ..."
vmtouch -t $DN_LOCAL_SSD/ioping-test
vmtouch $DN_LOCAL_SSD/ioping-test
time ioping -C -c 1000 -i 0.0001 $DN_LOCAL_SSD/ioping-test > $FN_PREFIX"local-ssd-cached"
time ioping -D -c 1000 -i 0.0001 $DN_LOCAL_SSD/ioping-test > $FN_PREFIX"local-ssd-direct"

vmtouch -t $DN_EBS_SSD_GP2/ioping-test
vmtouch $DN_EBS_SSD_GP2/ioping-test
time ioping -C -c 1000 -i 0.0001 $DN_EBS_SSD_GP2/ioping-test > $FN_PREFIX"ebs-ssd-gp2-cached"
time ioping -D -c 1000 -i 0.0001 $DN_EBS_SSD_GP2/ioping-test > $FN_PREFIX"ebs-ssd-gp2-direct"

#vmtouch -t $DN_EBS_SSD_IOP/ioping-test
#vmtouch $DN_EBS_SSD_IOP/ioping-test
#time ioping -C -c 1000 -i 0.0001 $DN_EBS_SSD_IOP/ioping-test > $FN_PREFIX"ebs-ssd-iop-cached"
#time ioping -D -c 1000 -i 0.0001 $DN_EBS_SSD_IOP/ioping-test > $FN_PREFIX"ebs-ssd-iop-direct"

#vmtouch -t $DN_EBS_MAG/ioping-test
#vmtouch $DN_EBS_MAG/ioping-test
#time ioping -C -c 1000 -i 0.0001 $DN_EBS_MAG/ioping-test > $FN_PREFIX"ebs-mag-cached"
#time ioping -D -c 1000 -i 0.0001 $DN_EBS_MAG/ioping-test > $FN_PREFIX"ebs-mag-direct"
