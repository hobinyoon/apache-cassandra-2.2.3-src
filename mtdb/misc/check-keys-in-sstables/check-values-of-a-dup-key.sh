#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

for ((i=1; i <= 2; i++ ))
do
	printf "SSTable %d:\n" $i
	~/work/cassandra/tools/bin/sstable2json \
		~/work/cassandra/data/data/keyspace1/standard1-8be2ccd08fb411e5b8c71d822de6a4f1/la-$i-big-Data.db \
		| grep -A 5 5050324f36364e4e3330 \
		|| true
done
