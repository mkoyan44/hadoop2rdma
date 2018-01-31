#!/bin/bash


hostname=( `cat "$(pwd)/hostFile"`)

for host in ${hostname[@]}
do
	ssh root@$host "bash -s" < tune.sh
done
