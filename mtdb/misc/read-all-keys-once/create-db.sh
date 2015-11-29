#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`
pushd $SRC_DIR > /dev/null

~/work/cassandra/bin/cqlsh -f create-keyspace.cql
