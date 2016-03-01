#!/bin/bash

mkdir	-p ~/work/cassandra/mtdb/logs/num-cass-threads || true

fn="/home/ubuntu/work/cassandra/mtdb/logs/num-cass-threads/"`date +'%y%m%d-%H%M%S'`
echo ${fn}
touch ${fn}

while [ 1 ]; do
	echo `date +'%y%m%d-%H%M%S '` >> ${fn}
	ps -T -p `ps -ef | grep -i org.apache.cassandra.service.CassandraDaemo[n] | awk '{ print $2 }'` | wc -l >> ${fn}
	sleep 1
done
