#!/bin/bash

ulimit -l unlimited
echo '* soft memlock unlimited' >  /etc/security/limits.conf
echo '* hard memlock unlimited' >> /etc/security/limits.conf
echo "options mlx4_core log_num_mtt=24 log_mtts_per_seg=0" > /etc/modprobe.d/mofed.conf
swapoff -a
rpm -Uvh https://www.mellanox.com/downloads/UDA/libuda-3.4.1-0.1034.el6.x86_64.rpm
ln -s /usr/lib64/uda/uda-hadoop-2.x.jar /tmp/hadoop/share/hadoop/common/lib/

/etc/init.d/opensmd stop
service openibd restart
/etc/init.d/opensmd start
