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
    pip3 install -q -r $DIR/requirements.txt && pip3 install av -q --no-binary av
}

railways_dep(){
    if [ ! $RAILWAY_STATIC_URL ]
        then
            echo -e "\n\nInstalling YouTube dependency... "
            pip3 install -q yt-dlp
    fi
}

install_okteto_cli(){
    if [ $OKTETO_TOKEN ]
        then
            echo -e "\n\nInstalling Okteto-CLI... "
            curl https://get.okteto.com -sSfL | sh
    fi
}

dep_install(){
    echo -e "\n\nInstalling DB Requirement..."
    if [ $MONGO_URI ]
        then
            pip3 install -q pymongo[srv]
    elif [ $DATABASE_URL ]
        then
            pip3 install -q psycopg2-binary
    elif [ $REDIS_URI ]
        then
            pip3 install -q redis hiredis
    fi
}

main(){
    (clone_repo) & spinner
    (install_requirements) & spinner
    (railways_dep) & spinner
    (dep_install) & spinner
    (install_okteto_cli) & spinner
}

main
