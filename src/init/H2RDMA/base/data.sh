#!/bin/bash
root=$1
pip install googledrivedownloader

if [ ! -d "$root/src/Data/hadoop-2.7.4" ]; then
	mkdir -p $root/src/Data
	python downloadGoogleDrive.py --id "18KOPQqcvE379wLtX0oAlRcMKg4m3zTAB" --path $root/src/Data
	tar -xzf $root/src/Data/dataSrc.tar.gz $root/src/Data
fi


rm -f $root/src/Data/dataSrc.tar.gz
cp sar.sh setBlockSize.sh changeBlock.sh runHadoop.sh $1/src/Data/hadoop-2.7.4/sbin/
pip install --user pssh
echo "Data"
/home/$USER/.local/bin/prsync -ravz -h "$(pwd)/hostFile" -l root $1/src/Data/hadoop-2.7.4/ /tmp/hadoop/
/home/$USER/.local/bin/prsync -ravz -h "$(pwd)/hostFile" -l root $1/src/Data/ibDriver/ /tmp/ibDriver
/home/$USER/.local/bin/prsync -ravz -h "$(pwd)/hostFile" -l root $1/src/Data/intelProfiler /opt
