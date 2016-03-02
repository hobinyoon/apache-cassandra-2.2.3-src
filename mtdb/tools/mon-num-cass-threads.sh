#!/bin/bash

mkdir	-p ~/work/cassandra/mtdb/logs/num-cass-threads || true

fn="/home/ubuntu/work/cassandra/mtdb/logs/num-cass-threads/"`date +'%y%m%d-%H%M%S'`
echo ${fn}
touch ${fn}

while [ 1 ]; do
	echo -n `date +'%y%m%d-%H%M%S'` >> ${fn}
	cass_pid=`ps -ef | grep -i org.apache.cassandra.service.CassandraDaemo[n] | awk '{ print $2 }'`
	if [ ${#cass_pid} -ne 0 ]; then
		echo -n " " >> ${fn}
		ps -T -p ${cass_pid} | wc -l >> ${fn}
	else
		echo "" >> ${fn}
	fi
	sleep 1
done
