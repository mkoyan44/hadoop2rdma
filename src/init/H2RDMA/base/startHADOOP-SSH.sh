#!/bin/bash

HADOOP_HOME=/tmp/hadoop
export PATH=$PATH:$HADOOP_HOME/bin
export PATH=$PATH:$HADOOP_HOME/sbin
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk.x86_64
echo 'Y' | hdfs namenode -format
hadoop dfsadmin -safemode leave
/tmp/hadoop/sbin/stop-all.sh;/tmp/hadoop/sbin/start-all.sh
