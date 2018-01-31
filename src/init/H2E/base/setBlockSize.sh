#!/bin/bash
/tmp/hadoop/sbin/stop-all.sh
wn=$(cat /etc/hosts |grep -v 'master'| awk '{print $2}')
for h in ${wn[@]}
do
	ssh root@"$h" "bash -s" < /tmp/hadoop/sbin/changeBlock.sh $1
done
sleep 10
rm -rf /tmp/hadoop/hdfs/ && mkdir -p /tmp/hadoop/hdfs/{namenode,datanode}
echo 'Y' | hdfs namenode  -format
/tmp/hadoop/sbin/start-all.sh
