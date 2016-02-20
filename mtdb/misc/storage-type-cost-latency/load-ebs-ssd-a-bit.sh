#!/bin/bash

#while [ 1 ]; do dd bs=256K count=1 if=/dev/zero of=/mnt/ebs-ssd-gp2/dd-test >/dev/null 2>&1 ; sleep 0.1; done

DN_EBS_SSD_GP2=/mnt/ebs-ssd-gp2
ioping -D -i 0.01 $DN_EBS_SSD_GP2/ioping-test > /dev/null
