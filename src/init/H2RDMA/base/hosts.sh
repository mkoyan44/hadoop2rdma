#!/bin/bash

rm -f $(pwd)/templates-H2R-Basic/master/slaves


hostname=( `cat "$(pwd)/hostFile"`)

for ((i=0; i<${#hostname[@]}; i++));
  do
    h=$(awk -F'.' '{ for(i=1;i<=NF;i++) print $i }' <<< ${hostname[i]} |head -1)
    if [[ $i == 0 ]]; then
		      echo "$h" > "$(pwd)/templates-H2R-Basic/slaves/masters"
		      echo "$h" > "$(pwd)/templates-H2R-Basic/master/masters"

    else
		     tmpHostname[i]="slave-$i"
    fi
    
    ip=$( host ${hostname[i]} | awk '{ print $4 }')
    tl=$(awk -F'.' '{ for(i=1;i<=NF;i++) print $i }' <<< $ip |tail -1)
    ssh root@${hostname[i]} "echo "$h" > /etc/hostname"
    echo "10.0.0.$tl $h" >> "$(pwd)/hosts"
    echo "$h" >> "$(pwd)/templates-H2R-Basic/master/slaves"
    echo "127.0.0.1 localhost" >> "$(pwd)/hosts"
  done

for host in ${hostname[@]}
 do
  scp hosts root@$host:/etc/hosts
  scp bashrc root@$host:/root/.bashrc
 done
rm $(pwd)/hosts
