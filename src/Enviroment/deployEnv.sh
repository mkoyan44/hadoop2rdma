#!/bin/bash
pip install googledrivedownloader
curDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
tmpFile='/home/amkoyan/deployGrid5000/Centos6.9Hadoop.tgz'
tgzFile="$curDir/Centos6.9Hadoop.tgz"
if [ ! -f $tgzFile ]; then
	python $curDir/downloadGoogleDrive.py --id "1OT45jgtdcBbH1VIQqmmQfAu8U252f-Yg" --path $curDir
	tar -zxf "$curDir/dataSrc.tar.gz" -C $curDir
fi
sed -i "s|$tmpFile|$tgzFile|g" $curDir/enviroment-kadeploy-1.2.conf
kadeploy3 -a "$curDir/enviroment-kadeploy-1.2.conf" -f "$OAR_FILE_NODES" -k
if [ $? -eq 1 ];then
	echo "Please reserve node before deploying envirmoent by using oarsub\n
	example: oarsub -p "cluster='orion'" -l nodes=4,walltime=48 -I -t deploy"
	exit 1
fi
