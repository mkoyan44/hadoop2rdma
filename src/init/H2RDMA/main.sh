#!/bin/bash
curDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
root=$(echo $curDir | awk -F'/' '{print "/"$2"/"$3"/"$4}')

cd $root/src/init/H2RDMA/base
hostname=( `cat "$(pwd)/hostFile"`)
# Initial SSH syncroniation and /etc/hosts file set up
echo "Initial SSH syncroniation and /etc/hosts file set up"
for host in ${hostname[@]}
    do
        ssh root@$host "bash -s" < ssh.sh
        # Run Host and Slave File
    done
bash hosts.sh

bash data.sh $root
# Get and Install Hadoop
echo "Get and Install Hadoop"

/home/$USER/.local/bin/pssh -h hostFile  -l root -t 0 -I< perfOpt.sh
/home/$USER/.local/bin/pssh -h hostFile  -l root -t 0 -I< master.sh
/home/$USER/.local/bin/pssh -h hostFile  -l root -t 0 -I< ibSetup.sh
/home/$USER/.local/bin/pssh -h hostFile  -l root -t 0 -I< udaInit.sh
#Send Configs
bash configFILES.sh $root
# Tune hadoop
bash tuneAllhosts.sh
# Start Hadoop and format namenode
bash startHADOOP.sh
# Test JOB
bash testJOB.sh
# gen hostname-freq.txt
bash get_host_freq.sh $root > hostname-freq.txt
