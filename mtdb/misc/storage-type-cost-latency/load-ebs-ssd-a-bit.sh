#!/bin/bash

while [ 1 ]; do dd bs=1M count=1 if=/dev/zero of=/mnt/ebs-ssd-gp2/dd-test >/dev/null 2>&1 ; sleep 0.01; done
