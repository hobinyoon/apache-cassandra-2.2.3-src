#!/bin/bash

set -e
set -u

SRC_DIR=`dirname $BASH_SOURCE`

time mvn package -Dmaven.test.skip=true
echo

time java \
	-cp target/loadgen-0.1.jar:$HOME/.m2/repository/org/yaml/snakeyaml/1.16/snakeyaml-1.16.jar \
	mtdb.LoadGen
