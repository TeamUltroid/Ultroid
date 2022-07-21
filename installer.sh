#!/usr/bin/env bash

REPO="https://github.com/TeamUltroid/Ultroid.git"
DIR="/root/TeamUltroid"

spinner(){
    local pid=$!
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ];
    do
        for i in "Ooooo" "oOooo" "ooOoo" "oooOo" "ooooO" "oooOo" "ooOoo" "oOooo" "Ooooo"
        do
          echo -ne "\r• $i"
          sleep 0.2
        done
    done
}

clone_repo(){
    if [ ! $BRANCH ]
        then export BRANCH="main"
    fi
    echo -e "\n\nCloning Ultroid ${BRANCH}... "
    git clone -b $BRANCH $REPO $DIR
}

install_requirements(){
    echo -e "\n\nInstalling requirements... "
    pip3 install -q --no-cache-dir -r $DIR/requirements.txt && pip3 install av -q --no-binary av
    pip3 install -q -r $DIR/resources/startup/optional-requirements.txt
}

railways_dep(){
    if [ $RAILWAY_STATIC_URL ]
        then
            echo -e "\n\nInstalling YouTube dependency... "
            pip3 install -q --no-cache-dir yt-dlp
    fi
}

install_okteto_cli(){
    if [ $OKTETO_TOKEN ]
        then
            echo -e "\n\nInstalling Okteto-CLI... "
            curl https://get.okteto.com -sSfL | sh
    fi
}

main(){
    (clone_repo)
    (install_requirements)
    (railways_dep)
    (install_okteto_cli)
}

main
