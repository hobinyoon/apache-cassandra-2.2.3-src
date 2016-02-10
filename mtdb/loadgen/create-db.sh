#!/bin/bash

#cqlsh fails sometimes
#set -e

set -u

SRC_DIR=`dirname $BASH_SOURCE`
pushd $SRC_DIR > /dev/null

while [ 1 ]; do
	~/work/cassandra/bin/cqlsh -f create-keyspace.cql
	RESULT=$?
	if [ $RESULT -eq 0 ]; then
		break
	else
		DATETIME=`date +"%y%m%d-%H%M%S"`
		echo $DATETIME" Failed. Restarting Cassandra and retrying in 30 secs ..." | tee -a create-db.log
		../../bin/kill-cassandra.sh
		../../bin/cassandra
		sleep 30
	fi
done
