#!/bin/bash

set -e
set -u

sudo add-apt-repository -y ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer git ctags ant htop tree maven gnuplot-nox ntp ioping realpath make gcc cmake g++ libboost-dev libboost-system-dev libboost-timer-dev collectl -y
sudo apt-get autoremove -y vim-tiny
mkdir -p ~/work
cd ~/work
git clone https://github.com/hoytech/vmtouch.git
cd vmtouch
make -j
sudo make install
sudo service ntp stop
sudo ntpdate -bv 0.ubuntu.pool.ntp.org
sudo service ntp start
cd ~/work
git clone git@github.com:hobinyoon/linux-home.git
cd linux-home
./setup-linux.sh
