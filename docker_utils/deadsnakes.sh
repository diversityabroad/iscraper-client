#!/usr/bin/env bash

apt-get update && apt-get -y install software-properties-common python-software-properties wget
add-apt-repository ppa:deadsnakes/ppa
apt-get update

wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
py_ver=`python -c 'import sys; print ".".join(str(x) for x in sys.version_info[:2])'`

for i in 2.6 2.7 3.4 3.5 3.6
do
  if [ "$i" != "$py_ver" ]
  then
    apt-get -y install python$i python$i-dev
    python$i /tmp/get-pip.py
  else
    echo "Default Python version is $i, installing dev libraries and pip only"
    apt-get install -y python$-dev
    python$i /tmp/get-pip.py
  fi
done
