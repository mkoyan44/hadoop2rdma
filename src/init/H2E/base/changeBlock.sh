#!/bin/bash

blockSize=$1
bs="$blockSize"'m'
echo 'y'| cp /tmp/hadoop/etc/hadoop/hdfs-site.xml.orig /tmp/hadoop/etc/hadoop/hdfs-site.xml
sed -i "s/BLOCK/$bs/g" /tmp/hadoop/etc/hadoop/hdfs-site.xml
rm -rf /tmp/hadoop/hdfs/ && mkdir -p /tmp/hadoop/hdfs/{namenode,datanode}
echo $bs
