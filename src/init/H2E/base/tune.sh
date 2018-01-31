#!/bin/bash


h=$(cat /etc/hosts | grep -i master | awk '{print $1}')
vcpu=$(cat /proc/cpuinfo |grep -i processor | wc -l)
mem=$(free -h |awk 'NR==2 {print $2}')
mem=${mem%G}


ls /tmp/hadoop/etc/hadoop/{mapred-site.xml,yarn-site.xml} | xargs -I {} python3 /tmp/hadoop/sbin/optimaze.py -c $vcpu -m $mem -f {}


# Change hostname
sed -i "s/master/$h/g" /tmp/hadoop/etc/hadoop/core-site.xml
sed -i "s/master/$h/g" /tmp/hadoop/etc/hadoop/mapred-site.xml
sed -i "s/master/$h/g" /tmp/hadoop/etc/hadoop/yarn-site.xml

echo 'y'| cp /tmp/hadoop/etc/hadoop/sysstat /etc/cron.d/

rm -rf /tmp/hadoop/hdfs/ && mkdir -p /tmp/hadoop/hdfs/{namenode,datanode}


rm -rf /var/log/sa/sa* 

# run sar for taking every minute
if [[ -z $(ps aux|grep -i /tmp/NPB/bin/sar.sh |grep -v 'grep') ]];then
	bash /tmp/hadoop/sbin/optimaze.sh &
fi
