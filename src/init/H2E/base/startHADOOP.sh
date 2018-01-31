#!/bin/bash
hostname=( `cat "$(pwd)/hostFile"` )
for host in ${hostname[@]}
do
	ssh root@"$host" 'rm -rf /tmp/hadoop/hdfs/* && mkdir -p /tmp/hadoop/hdfs/{namenode,datanode}'
done
ssh root@${hostname[0]} "bash -s" < startHADOOP-SSH.sh
