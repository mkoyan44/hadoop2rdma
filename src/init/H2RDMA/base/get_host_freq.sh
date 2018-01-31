#!/bin/bash
hostname=( `cat "$1/src/init/H2RDMA/base/hostFile"`)

for h in ${hostname[@]}
do
	freq=$(ssh root@$h 'cat /sys/devices/system/cpu/cpu1/cpufreq/scaling_available_frequencies')
	printf "%s:%s\n" "$h" "$freq"
done
