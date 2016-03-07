#!/bin/bash

set -e
set -u
set -v

#sudo cp ~/work/cassandra/mtdb/ec2-tools/etc-fstab /etc/fstab
#sudo umount /mnt
#
#sudo mkdir -p /mnt/local-ssd
#sudo mount /mnt/local-ssd
#sudo chown -R ubuntu /mnt/local-ssd
#mkdir -p /mnt/local-ssd/cass-data
#mkdir -p /mnt/local-ssd/mtdb-cold

#mkdir ~/cass-data-vol
#sudo ln -s ~/cass-data-vol /mnt/ebs-ssd-gp2
#mkdir /mnt/ebs-ssd-gp2/cass-data
#
#sudo ln -s /mnt/ebs-ssd-gp2 /mnt/cold-storage
#
#sudo chown -R ubuntu /mnt/ebs-ssd-gp2
#
#sudo chown -R ubuntu /mnt/cold-storage

sudo mkdir -p /mnt/cold-storage/mtdb-cold
sudo chown -R ubuntu /mnt/cold-storage/mtdb-cold

mkdir -p ~/work/cassandra/mtdb/logs/collectl
ln -s /mnt/local-ssd/cass-data ~/work/cassandra/data
