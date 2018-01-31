#!/bin/bash


# Vars
	
h=$(cat /etc/hosts | head -1 | awk '{print $2}')
vcpu=$(cat /proc/cpuinfo |grep -i processor | wc -l)
mem=$(free -h |awk 'NR==2 {print $2}')
mem=${mem%G}
ip=$( cat /etc/hosts|grep $(cat /etc/hostname) | awk '{print $1}')
tl=$(awk -F'.' '{ for(i=1;i<=NF;i++) print $i }' <<< $ip |tail -1)


# Optimaze cluster according to CDH
ls /tmp/hadoop/etc/hadoop/{mapred-site.xml,yarn-site.xml} | xargs -I {} python3 /tmp/hadoop/sbin/optimaze.py -c $vcpu -m $mem -f {}


# Conf IB interface
ib0="10.0.0.$tl/24"
ifconfig ib0 $ib0 up


# Change master to original hostname
sed -i "s/master/$h/g" /tmp/hadoop/etc/hadoop/core-site.xml
sed -i "s/master/$h/g" /tmp/hadoop/etc/hadoop/mapred-site.xml
sed -i "s/master/$h/g" /tmp/hadoop/etc/hadoop/yarn-site.xml

# Copy pre configurd corn file
echo 'y'| cp /tmp/hadoop/etc/hadoop/sysstat /etc/cron.d/

# Clean data
rm -rf /tmp/hadoop/hdfs/ && mkdir -p /tmp/hadoop/hdfs/{namenode,datanode}

# Remove 
rm -rf /var/log/sa/sa* 

# run sar for taking every minute
if [[ -z $(ps aux|grep -i /tmp/NPB/bin/sar.sh |grep -v 'grep') ]];then
	bash /tmp/hadoop/sbin/optimaze.sh &
fi
