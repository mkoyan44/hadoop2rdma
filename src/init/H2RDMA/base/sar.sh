#!/bin/bash
while [ true ]
do

if [ -f /etc/debian_version ]; then
    sleep 1
        /usr/lib/sysstat/sa1 1 1
elif [ -f /etc/redhat-release ]; then
        sleep 1
        /usr/lib64/sa/sa1 1 1
fi
done
