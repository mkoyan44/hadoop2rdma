#!/bin/bash
HADOOP_HOME=/tmp/hadoop
export PATH=$PATH:$HADOOP_HOME/bin
export PATH=$PATH:$HADOOP_HOME/sbin
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk.x86_64
hadoop jar /tmp/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.9.0.jar pi -Dmapred.reducetask.shuffle.consumer.plugin=com.mellanox.hadoop.mapred.UdaShuffleConsumerPlugin -Dmapreduce.job.reduce.shuffle.consumer.plugin.class=com.mellanox.hadoop.mapred.UdaShuffleConsumerPlugin 30 100
