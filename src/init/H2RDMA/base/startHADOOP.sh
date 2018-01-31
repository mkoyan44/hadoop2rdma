#!/bin/bash
set -x 
set -e
hostname=( `cat "$(pwd)/hostFile"` )
for host in ${hostname[@]}
do
	echo $host
	ssh root@"$host" 'rm -rf /tmp/hadoop/hdfs/* && mkdir -p /tmp/hadoop/hdfs/{namenode,datanode}'
done
ssh root@${hostname[0]} "bash -s" < startHADOOP-SSH.sh
