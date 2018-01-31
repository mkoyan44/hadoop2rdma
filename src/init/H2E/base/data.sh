#!/bin/bash
root=$1
pip install googledrivedownloader

if [ ! -d "$root/src/Data/hadoop-2.7.4" ]; then
	mkdir -p $root/src/Data
	python downloadGoogleDrive.py --id "15e0GFmwm7PilJC24qeu6G6nlsCULkfGe" --path $root/src/Data
	tar -xzf "$root/src/Data/dataSrc.tar.gz" -C $root/src/Data 
fi

rm -f $root/src/Data/dataSrc.tar.gz
cp sar.sh setBlockSize.sh changeBlock.sh runHadoop.sh $root/src/Data/hadoop-2.7.4/sbin/

pip install --user pssh
/home/$USER/.local/bin/pscp -r -h "$(pwd)/hostFile" -l root $root/src/Data/hadoop-2.7.4/ /tmp/hadoop/
/home/$USER/.local/bin/pscp -r -h "$(pwd)/hostFile" -l root $root/src/Data/intelProfiler /opt
