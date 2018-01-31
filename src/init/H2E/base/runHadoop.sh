#!/bin/bash
file="$5"
root="/tmp/log"
out="/tmp/out"
mkdir -p {$root,$out}
echo 'y' | /opt/intelProfiler/storage-snapshot/sps-stop.sh
sleep 3
echo 'y' | /opt/intelProfiler/storage-snapshot/sps-start.sh

for benchmarkCommand in "$1" "$2" "$3" "$4"
do
        echo $benchmarkCommand
        $benchmarkCommand
done

sleep 3

outDat=$(echo 'y' | /opt/intelProfiler/storage-snapshot/sps-stop.sh | grep -i 'Stopped gathering system data.' | awk '{print $9}')
mv -f $outDat "$out/$file.dat"