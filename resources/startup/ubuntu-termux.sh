#!/usr/bin/bash

directory="ubuntu-for-ultroid"
architecture=$(dpkg --print-architecture)

install_ubuntu(){
    apt update
    apt upgrade -y
    apt install proot wget -y
    if [ "$architecture" = "arm" ];
    then
        architecture="armhf"
    elif [ "$architecture" = "aarch64" ];
    then
        architecture="arm64"
    elif [ "$architecture" = "amd64" ];
    then
        architecture="amd64"
    elif [ "$architecture" = "x86_64" ];
    then
        architecture="amd64"
    else
        echo "Unknown Architecture - $architecture!!"
        exit 1
    fi

    echo "Your architecture is $architecture. Downloading ubuntu package for your architecture."
    wget http://cdimage.ubuntu.com/ubuntu-base/releases/21.04/release/ubuntu-base-21.04-base-${architecture}.tar.gz -O "ubuntu.tar.gz"

    root=`pwd`
    mkdir -p $directory && cd $directory
    tar -zxf $root/ubuntu.tar.gz --exclude='dev'||:
    echo "nameserver 8.8.8.8\nnameserver 8.8.4.4\n" > etc/resolv.conf
    stubs=()
    stubs+=('usr/bin/groups')
    for e in ${stubs[@]};
    do
        echo -e "#!/bin/sh\nexit" > "$e"
    done
    cd $root
}       

install_ubuntu
