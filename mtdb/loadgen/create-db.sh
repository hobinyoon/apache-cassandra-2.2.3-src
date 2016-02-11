#!/bin/bash

#cqlsh fails sometimes
#set -e

if [ -z "$CASSANDRA_SERVER_ADDR" ]; then
	echo "CASSANDRA_SERVER_ADDR is not set."
	exit 1
fi
printf "CASSANDRA_SERVER_ADDR=%s\n" $CASSANDRA_SERVER_ADDR

SRC_DIR=`dirname $BASH_SOURCE`
pushd $SRC_DIR > /dev/null

set -u

while [ 1 ]; do
	~/work/cassandra/bin/cqlsh -f create-keyspace.cql $CASSANDRA_SERVER_ADDR
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
