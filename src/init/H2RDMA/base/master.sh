#!/bin/bash
mkdir -p /tmp/hadoop
dataDIR=( "/tmp/hadoop/tmp" "/tmp/hadoop/hdfs/namenode" "/tmp/hadoop/hdfs/datanode" )
for i in ${dataDIR[@]}
do
  if [[  ! -d "$i" ]]; then
    mkdir -p $i
  fi
done

tmp=$(rpm -qa | grep -i openjdk)
# Install JAVA
if [[ -z $tmp ]]; then
  yum install epel-release -y
  yum install rsync java-1.8.0-openjdk.x86_64 java-1.8.0-openjdk-devel.x86_64 vim cpufrequtils sysstat dstat python34.x86_64 -y
  yum install ganglia-gmond -y
  service gmond status
  modprobe acpi_cpufreq
  modprobe cpufreq_ondemand
  modprobe cpufreq_ondemand
  modprobe cpufreq_powersave
  iptables -t nat -F
  iptables -t FILTER -F
  iptables -t MANGLE -F
  rm /etc/localtime
  ln -s /usr/share/zoneinfo/Europe/Paris /etc/localtime
fi
if [[ -z $(ps aux|grep -i /tmp/hadoop/sbin/sar.sh |grep -v 'grep') ]];then
	screen -d -m sh -c 'bash /tmp/hadoop/sbin/sar.sh'
fi
