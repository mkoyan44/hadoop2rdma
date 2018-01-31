#!/bin/bash
hostname=( `cat "$(pwd)/hostFile"`)
ssh root@${hostname[0]}  "bash -s" < testJOB-SSH.sh

