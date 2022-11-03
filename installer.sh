#!/usr/bin/env bash

REPO="https://github.com/riizzvbss/Ayra-Userbot2.git"
DIR="/root/riizzvbss"

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
            if [ currentbranch != $BRANCH ]
                then
                    git checkout $BRANCH
            fi
            if [ -d "addons" ]
                then
                    cd addons
                    git pull
            fi
            return
    fi
    echo -e "Cloning Ayra ${BRANCH}... "
    git clone -b $BRANCH $REPO $DIR
}

install_requirements(){
    pip install --upgrade pip
    echo -e "\n\nInstalling requirements... "
    pip3 install -q --no-cache-dir -r $DIR/requirements.txt
    pip3 install -q -r $DIR/resources/startup/optional-requirements.txt
}

railways_dep(){
    if [ $RAILWAY_STATIC_URL ]
        then
            echo -e "Installing YouTube dependency... "
            pip3 install -q yt-dlp
    fi
}

misc_install(){
    if [ $OKTETO_TOKEN ]
        then
            echo -e "Installing Okteto-CLI... "
            curl https://get.okteto.com -sSfL | sh
    elif [ $VCBOT ]
        then
            if [ -d $DIR/vcbot ]
                then
                    cd $DIR/vcbot
                    git pull
            else
                echo -e "Cloning VCBOT.."
                git clone https://github.com/riizzvbss/MusicUbot $DIR/vcbot
            fi
            pip3 install pytgcalls>=3.0.0.dev21 && pip3 install av -q --no-binary av
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
    (misc_install)
}

main
