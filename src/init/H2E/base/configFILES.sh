#!/bin/bash
root=$1
hostname=( `cat "$(pwd)/hostFile"`)
echo 'Y' | cp changeBlock.sh sar.sh setBlockSize.sh runHadoop.sh $root/src/Data/hadoop-2.7.4/sbin/   
for ((i=0; i<${#hostname[@]}; i++));
do
    rsync -avz --include ".*" $root/src/Data/hadoop-2.7.4/  root@${hostname[i]}:/tmp/hadoop/
    
    if [[ $i == 0 ]]; then
        scp -r $(pwd)/templates-H2R-Basic/master/* root@${hostname[i]}:/tmp/hadoop/etc/hadoop/
    else
        scp -r $(pwd)/templates-H2R-Basic/slaves/* root@${hostname[i]}:/tmp/hadoop/etc/hadoop/
    fi
done
