#!/usr/bin/env bash

REPO="https://github.com/TeamUltroid/Ultroid.git"
DIR="/root/TeamUltroid"
BRANCH=$BRANCH

spinner(){
    local pid=$!
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ];
    do
        for i in "Ooooo" "oOooo" "ooOoo" "oooOo" "ooooO" "oooOo" "ooOoo" "oOooo" "Ooooo"
        do
          echo -ne "\r$i"
          sleep 0.2
        done
    done
}

clone_repo(){
    if [ ! $BRANCH ]
        then BRANCH="main"
    fi
    echo "Cloning Ultroid ${BRANCH}"
    git clone -q -b $BRANCH $REPO $DIR
}

install_requirements(){
    echo "Installing requirements..."
    pip3 install -q --no-cache-dir -r $DIR/requirements.txt && pip3 install av -q --no-binary av
}

railways_shit(){
    if [ ! $RAILWAY_STATIC_URL ]
        then
            echo "Installing YouTube dependency..."
            pip3 install -q --no-cache-dir yt-dlp
    fi
}

oktetos_shit(){
    if [ $OKTETO_TOKEN ]
        then
            echo "Installing Okteto-CLI..."
            curl https://get.okteto.com -sSfL | sh
    fi
}

main(){
    clone_repo
    (install_requirements) & spinner
    railways_shit
    oktetos_shit
}
