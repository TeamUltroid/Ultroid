#!/usr/bin/bash

# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


main(){
    install_ubuntu
    update_packages
    install_packages
    install_opencv
    install_pillow
    install_dependencies
    # should_start
}

update_packages(){
    echo "Updating Packages..."
    apt update
    apt upgrade -y
    clear
}

install_packages(){
    echo "Installing missing Packages..."
    apt install -y \
        python \
        wget \
        git \
        ffmpeg \
        mediainfo \
        neofetch \
        jq \
        libatlas-base-dev \
        libavcodec-dev \
        libavdevice-dev \
        libavfilter-dev \
        libavformat-dev \
        libavutil-dev \
        libboost-python-dev \
        libcurl4-openssl-dev \
        libffi-dev \
        libgconf-2-4 \
        libgtk-3-dev \
        libjpeg-dev \
        libjpeg62-turbo-dev \
        libopus-dev \
        libopus0 \
        libpq-dev \
        libreadline-dev \
        libswresample-dev \
        libswscale-dev \
        libssl-dev \
        libwebp-dev \
        libx11-dev \
        libxi6 \
        libxml2-dev \
        libxslt1-dev \
        libyaml-dev \
        megatools \
        openssh-client \
        openssh-server \
        openssl \
        p7zip-full \
        pdftk \
        procps \
        unzip \
        wkhtmltopdf \
        zip
    clear
    echo "Remove Unused packages..."
    apt autoremove --purge
    clear
}

install_opencv(){
    echo "Installing OpenCV..."
    curl -LO https://its-pointless.github.io/setup-pointless-repo.sh
    bash setup-pointless-repo.sh
    apt install opencv
    rm setup-pointless-repo.sh
    clear
}

install_pillow(){
    echo "Installing Pillow..."
    export LDFLAGS="-L/system/lib/"
    export CFLAGS="-I/data/data/com.termux/files/usr/include/"
    pip install -U pip wheel setuptools
    pip install Pillow
    clear
}

install_dependencies(){
    echo "Installing Dependencies..."
    wget -O requirements.txt https://raw.githubusercontent.com/TeamUltroid/Ultroid/dev/resources/startup/optional-requirements.txt
    pip install --no-cache-dir -r requirements.txt
    pip install av --no-binary av
    rm requirements.txt
    clear
}

should_start(){
    echo "Getting Started..."
    git clone https://github.com/TeamUltroid/Ultroid
    cd Ultroid
    clear

    read -p "Should I start the bot? Yes/No: " start;

    if [ $start = "Yes" ];
    then
        sh resources/startup/startup.sh
    elif [ $start != "Yes" ];
    then
        echo "Bye Bye..."
    fi
}

main
