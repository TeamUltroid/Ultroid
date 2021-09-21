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
    mkdir -p "ubuntu-bindings"
    bin=start-ubuntu.sh
    cat > $bin <<- EOM
#!/bin/bash
cd \$(dirname \$0)
unset LD_PRELOAD
command="proot"
command+=" --link2symlink"
command+=" -0"
command+=" -r $root"
if [ -n "\$(ls -A ubuntu-bindings)" ]; then
for f in ubuntu-bindings/* ;do
  . \$f
done
fi
command+=" -b /dev"
command+=" -b /proc"
command+=" -b /sys"
command+=" -b ubuntu-fs/tmp:/dev/shm"
command+=" -b /data/data/com.termux"
command+=" -b /:/host-rootfs"
command+=" -b /sdcard"
command+=" -b /storage"
command+=" -b /mnt"
command+=" -w /root"
command+=" /usr/bin/env -i"
command+=" HOME=/root"
command+=" PATH=/usr/local/sbin:/usr/local/bin:/bin:/usr/bin:/sbin:/usr/sbin:/usr/games:/usr/local/games"
command+=" TERM=\$TERM"
command+=" LANG=C.UTF-8"
command+=" ANDROID=True"
command+=" /bin/bash --login"
com="\$@"
if [ -z "\$1" ];then
    exec \$command
else
    \$command -c "\$com"
fi
EOM

    termux-fix-shebang $bin
    chmod +x $bin
    rm ubuntu.tar.gz
}

install_ubuntu
