#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

for ((i=1; i <= 17; i++ ))
do
	echo $i
	time ~/work/cassandra/bin/sstablekeys ~/work/cassandra/data/data/keyspace1/standard1-8be2ccd08fb411e5b8c71d822de6a4f1/la-$i-big-Data.db > keys-$i
done
