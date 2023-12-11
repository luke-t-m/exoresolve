#!/bin/bash
set -e

echo "Requires root access."
sudo whoami

RED='\033[1;31m'
GREEN='\033[1;32m'
NC='\033[0m' # No Color
echo "Find path to script."
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "Found $SCRIPT_DIR."

echo "Make directory structure in /usr/local."
sudo mkdir -p /usr/local/exoresolve
sudo mkdir -p /usr/local/exoresolve/lists

echo "Make harbinger, conf, and temp_conf file."
sudo touch "/usr/local/exoresolve/harbinger"
sudo touch "/usr/local/exoresolve/conf"
sudo touch "/usr/local/exoresolve/temp_conf"

echo "Copy exoresolve.py to /usr/local."
sudo cp $SCRIPT_DIR/src/exoresolve.py /usr/local/exoresolve/exoresolve.py

printf "${RED}------------- MAKE KILLHAND -------------${NC}\n"
make -C $SCRIPT_DIR/src/killhand/
printf "${GREEN}-------------- SUCCESSFUL --------------${NC}\n"
echo "Copy killhand.ko to /usr/local."
sudo cp $SCRIPT_DIR/src/killhand/killhand.ko /usr/local/exoresolve/killhand.ko


echo "Test killhand.ko can be inserted and removed."
if lsmod | grep -wq killhand; then
  sudo rmmod killhand
fi
sudo insmod /usr/local/exoresolve/killhand.ko
sudo rmmod killhand

echo "Set /etc/resolv.conf for dnsmasq."
sudo rm /etc/resolv.conf
sudo cp $SCRIPT_DIR/sysfile_bits/resolv.conf /etc/resolv.conf

printf "${RED}-------------- UNIFY LISTS -------------${NC}\n"
sudo python3 $SCRIPT_DIR/unify_lists.py
printf "${GREEN}-------------- SUCCESSFUL --------------${NC}\n"


echo "Modify rc.local to run exoresolve.py iff."
if ! grep -xq "python3 /usr/local/exoresolve/exoresolve.py &" /etc/rc.local
then
    sudo sed -i -e '$i python3 /usr/local/exoresolve/exoresolve.py &\n' /etc/rc.local
fi

echo "Modify /etc/dnsmasq.conf to source our dnsmasq.conf iff."
if ! grep -xq "conf-file=/usr/local/exoresolve/dnsmasq.conf" /etc/dnsmasq.conf
then
    sudo sed -i -e '$i conf-file=/usr/local/exoresolve/dnsmasq.conf\n' /etc/dnsmasq.conf
fi

