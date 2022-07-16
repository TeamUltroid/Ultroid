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
    if [ -d $DIR ]
        then
            echo -e $DIR "Already exists.."
            cd $DIR
            git pull
            currentbranch="$(git rev-parse --abbrev-ref HEAD)"
            if [currentbranch != $BRANCH]
                then
                    git checkout $BRANCH
            fi
    fi
    echo -e "Cloning Ultroid ${BRANCH}... "
    git clone -b $BRANCH $REPO $DIR
}

install_requirements(){
    echo -e "Installing requirements... "
    pip3 install -q -r $DIR/requirements.txt && pip3 install av -q --no-binary av
    pip3 install -r resources/startup/optional-requirements.txt -y
}

railways_dep(){
    if [ $RAILWAY_STATIC_URL ]
        then
            echo -e "Installing YouTube dependency... "
            pip3 install -q yt-dlp
    fi
}

install_okteto_cli(){
    if [ $OKTETO_TOKEN ]
        then
            echo -e "Installing Okteto-CLI... "
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
    (clone_repo)
    (install_requirements)
    (railways_dep)
    (dep_install)
    (install_okteto_cli)
}

main
