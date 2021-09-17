#!/usr/bin/env bash
# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

echo "Updating Packages..."
apt update
apt upgrade -y
clear

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
    netcat \
    ninja-build \
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

echo "Installing OpenCV..."
curl -LO https://its-pointless.github.io/setup-pointless-repo.sh
bash setup-pointless-repo.sh
apt install opencv
rm setup-pointless-repo.sh
clear

echo "Installing Pillow..."
export LDFLAGS="-L/system/lib/"
export CFLAGS="-I/data/data/com.termux/files/usr/include/"
pip install Pillow
clear

echo "Installing Dependencies..."
wget -O requirements.txt https://raw.githubusercontent.com/TeamUltroid/Ultroid/dev/resources/startup/requirements.txt
pip install -U pip wheel setuptools
pip install --no-cache-dir -r requirements.txt
pip install av --no-binary av
rm requirements.txt
clear

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
