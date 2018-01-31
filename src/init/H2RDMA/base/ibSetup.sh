#!/bin/bash
yum install pciutils gtk2 atk cairo gcc-gfortran perl libxml2-python tcsh libnl lsof tcl numactl tk -y
echo 'Y' | /tmp/ibDriver/mlnxofedinstall --without-fw-update
/etc/init.d/openibd restart
/etc/init.d/opensmd restart
