#!/usr/bin/env bash

REPO="https://github.com/TeamUltroid/Ultroid.git"
DIR="/root/TeamUltroid"
BRANCH=$BRANCH

spinner(){
    local pid=$!
    local delay=0.5
    local spinstr=( 0oooo o0ooo oo0oo ooo0o oooo0 )
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

clone_repo(){
    if [ ! $BRANCH ]
        then BRANCH="main"
    fi
    echo "Cloning Ultroid ${BRANCH}"
    git clone -b $BRANCH $REPO $DIR
}

install_requirements(){
    pip3 install -q --no-cache-dir -r $DIR/requirements.txt && pip3 install av -q --no-binary av
}

railways_shit(){
    if [ ! $RAILWAY_STATIC_URL ]
        then pip3 install -q --no-cache-dir yt-dlp
    fi
}

oktetos_shit(){
    if [ $OKTETO_TOKEN ]
        then curl https://get.okteto.com -sSfL | sh
    fi
}

main(){
    clone_repo
    (install_requirements) & spinner
    railways_shit
    oktetos_shit
}
