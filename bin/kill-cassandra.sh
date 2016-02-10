#!/bin/bash

set -e
set -u

cass_pid=`ps -ef | grep -i CassandraDaemo[n] | awk '{print $2}'`
if [[ -z $cass_pid ]]; then
	echo "No Cassandra to kill."
	exit 0
fi

kill $cass_pid

# wait for termination
while [ 1 ]; do
	num_inst=`ps -ef | grep -i CassandraDaemo[n] | wc -l`
	#echo $num_inst 
	if [[ "$num_inst" == "0" ]]; then
		echo " terminated"
		break
	fi
	sleep 0.1
	echo -n "."
done
