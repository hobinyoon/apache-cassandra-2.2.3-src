#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

if [ "$#" -ne 1 ]; then
	printf "Usage: %s path_to_data\n" $0
	printf "  E.g.: %s ~/work/cassandra/data/data/keyspace1/standard1-2d180380949311e5945a1d822de6a4f1\n" $0
	exit 1
fi

DN_DATA=$1
TABLE_ID=`basename $DN_DATA`

printf "Table ID: %s\n" $TABLE_ID
mkdir $TABLE_ID

for ((i=1; ; i++ ))
do
	FN_SSTABLE=$DN_DATA/la-$i-big-Data.db
	if [ ! -f "$FN_SSTABLE" ]; then
		break
	fi

	FN_KEY=$TABLE_ID/keys-$i
	printf "Creating %s ...\n" $FN_KEY
	(time ~/work/cassandra/bin/sstablekeys $FN_SSTABLE > $FN_KEY) | sed 's/^/  /'
done
