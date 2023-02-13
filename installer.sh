#!/usr/bin/env bash

REPO="https://github.com/TeamUltroid/Ultroid.git"
CURRENT_DIR="$(pwd)"
ENV_FILE_PATH=".env"
DIR="/root/TeamUltroid"

while [ $# -gt 0 ]; do
    case "$1" in
    --dir=*)
        DIR="${1#*=}" || DIR="/root/TeamUltroid"
        ;;
    --branch=*)
        BRANCH="${1#*=}" || BRANCH="main"
        ;;
    --env-file=*)
        ENV_FILE_PATH="${1#*=}" || ENV_FILE_PATH=".env"
        ;;
    --no-root)
        NO_ROOT=true
        ;;
    *)
        echo "Unknown parameter passed: $1"
        exit 1
        ;;
    esac
    shift
done

check_dependencies() {
    # check if debian
    echo "Checking dependencies..."
    # read file with root access
    if ! [[ $(ls -l "/etc/sudoers" | cut -d " " -f1) =~ "r" ]]; then
        # check dependencies if installed
        echo -e "Root access not found. Checking if dependencies are installed." >&2
        if ! [ -x "$(command -v python3)" ] || ! [ -x "$(command -v python)" ]; then
            echo -e "Python3 isn't installed. Please install python3.8 or higher to run this bot." >&2
            exit 1
        fi
        if [ $(python3 -c "import sys; print(sys.version_info[1])") -lt 8 ] || [ $(python -c "import sys; print(sys.version_info[1])") -lt 8 ]; then
            echo -e "Python 3.8 or higher is required to run this bot." >&2
            exit 1
        fi
        # check if any of ffmpeg, mediainfo, neofetch, git is not installed
        if ! command -v ffmpeg &>/dev/null || ! command -v mediainfo &>/dev/null || ! command -v neofetch &>/dev/null || ! command -v git &>/dev/null; then
            echo -e "Some dependencies aren't installed. Please install ffmpeg, mediainfo, neofetch and git to run this bot." >&2
            exit 1
        fi
    fi
    if [ -x "$(command -v apt-get)" ]; then
        echo -e "Installing dependencies..."
        # check if any of ffmpeg, mediainfo, neofetch, git is not installed via dpkg
        if dpkg -l | grep -q ffmpeg || dpkg -l | grep -q mediainfo || dpkg -l | grep -q neofetch || dpkg -l | grep -q git; then
            sudo apt-get -qq -o=Dpkg::Use-Pty=0 update
            sudo apt-get install -qq -o=Dpkg::Use-Pty=0 python3 python3-pip ffmpeg mediainfo neofetch git -y
        fi
    elif [ -x "$(command -v pacman)" ]; then
        echo -e "Installing dependencies..."
        if pacman -Q | grep -q ffmpeg || pacman -Q | grep -q mediainfo || pacman -Q | grep -q neofetch || pacman -Q | grep -q git; then
            sudo pacman -Sy python python-pip git ffmpeg mediainfo neofetch --noconfirm
        fi
    else
        echo -e "Unknown OS. Checking if dependecies are installed" >&2
        if ! [ -x "$(command -v python3)" ] || ! [ -x "$(command -v python)" ]; then
            echo -e "Python3 isn't installed. Please install python3.8 or higher to run this bot." >&2
            exit 1
        fi
        if [ $(python3 -c "import sys; print(sys.version_info[1])") -lt 8 ] || [ $(python -c "import sys; print(sys.version_info[1])") -lt 8 ]; then
            echo -e "Python 3.8 or higher is required to run this bot." >&2
            exit 1
        fi
        if ! command -v ffmpeg &>/dev/null || ! command -v mediainfo &>/dev/null || ! command -v neofetch &>/dev/null || ! command -v git &>/dev/null; then
            echo -e "Some dependencies aren't installed. Please install ffmpeg, mediainfo, neofetch and git to run this bot." >&2
            exit 1
        fi
    fi
}

check_python() {
    # check if python is installed
    if ! command -v python3 &>/dev/null; then
        echo -e "Python3 isn't installed. Please install python3.8 or higher to run this bot."
        exit 1
    elif ! command -v python &>/dev/null; then
        echo -e "Python3 isn't installed. Please install python3.8 or higher to run this bot."
        exit 1
    fi
    if [ $(python3 -c "import sys; print(sys.version_info[1])") -lt 8 ]; then
        echo -e "Python 3.8 or higher is required to run this bot."
        exit 1
    elif [ $(python -c "import sys; print(sys.version_info[1])") -lt 3 ]; then
        if [ $(python -c "import sys; print(sys.version_info[1])") -lt 8 ]; then
            echo -e "Python 3.8 or higher is required to run this bot."
            exit 1
        fi
    fi
}

clone_repo() {
    # check if pyultroid, startup, plugins folders exist
    cd $DIR
    if [ ! $BRANCH ]; then
        export BRANCH="main"
    fi
    if [ -d $DIR ]; then
        if [ -d $DIR/.git ]; then
            echo -e "Updating Ultroid ${BRANCH}... "
            cd $DIR
            git pull
            currentbranch="$(git rev-parse --abbrev-ref HEAD)"
            case $currentbranch in
            $BRANCH)
                # do nothing
                ;;
            *)
                echo -e "Switching to branch ${BRANCH}... "
                echo -e $currentbranch
                git checkout $BRANCH
                ;;
            esac
        else
            rm -rf $DIR
            exit 1
        fi
        if [ -d "addons" ]; then
            cd addons
            git pull
        fi
        return
    else
        mkdir -p $DIR
        echo -e "Cloning Ultroid ${BRANCH}... "
        git clone -b $BRANCH $REPO $DIR
    fi
}

install_requirements() {
    pip3 install -q --upgrade pip
    echo -e "\n\nInstalling requirements... "
    pip3 install -q --no-cache-dir -r $DIR/requirements.txt
    pip3 install -q -r $DIR/resources/startup/optional-requirements.txt
}

railways_dep() {
    if [ $RAILWAY_STATIC_URL ]; then
        echo -e "Installing YouTube dependency... "
        pip3 install -q yt-dlp
    fi
}

misc_install() {
    if [ $SETUP_PLAYWRIGHT ]
    then
        echo -e "Installing playwright."
        pip3 install playwright
        playwright install
    fi
    if [ $OKTETO_TOKEN ]; then
        echo -e "Installing Okteto-CLI... "
        curl https://get.okteto.com -sSfL | sh
    elif [ $VCBOT ]; then
        if [ -d $DIR/vcbot ]; then
            cd $DIR/vcbot
            git pull
        else
            echo -e "Cloning VCBOT.."
            git clone https://github.com/TeamUltroid/VcBot $DIR/vcbot
        fi
        pip3 install pytgcalls==3.0.0.dev23 && pip3 install av -q --no-binary av
    fi
}

dep_install() {
    echo -e "\n\nInstalling DB Requirement..."
    if [ $MONGO_URI ]; then
        echo -e "   Installing MongoDB Requirements..."
        pip3 install -q pymongo[srv]
    elif [ $DATABASE_URL ]; then
        echo -e "   Installing PostgreSQL Requirements..."
        pip3 install -q psycopg2-binary
    elif [ $REDIS_URI ]; then
        echo -e "   Installing Redis Requirements..."
        pip3 install -q redis hiredis
    fi
}

main() {
    echo -e "Starting Ultroid Setup..."
    if [ -d "pyUltroid" ] && [ -d "resources" ] && [ -d "plugins" ]; then
        DIR=$CURRENT_DIR
    fi
    if [ -f $ENV_FILE_PATH ]
    then
        set -a
        source <(cat $ENV_FILE_PATH | sed -e '/^#/d;/^\s*$/d' -e "s/'/'\\\''/g" -e "s/=\(.*\)/='\1'/g")
        set +a
        cp $ENV_FILE_PATH .env
    fi
    (check_dependencies)
    (check_python)
    (clone_repo)
    (install_requirements)
    (railways_dep)
    (dep_install)
    (misc_install)
    echo -e "\n\nSetup Completed."
}

if [ $NO_ROOT ]; then
    echo -e "Running with non root"
    main
    return 0
elif [ -t 0 ]; then
    unameOut="$(uname -s)"
    case "${unameOut}" in
        Linux*)     machine=Linux;;
        Darwin*)    machine=Mac;;
        CYGWIN*)    machine=Cygwin;;
        MINGW*)     machine=MinGw;;
        *)          machine="UNKNOWN:${unameOut}"
    esac
    if machine != "Linux"; then
        echo -e "This script is only for Linux. Please use the Windows installer."
        exit 1
    fi
    # check if sudo is installed
    if ! command -v sudo &>/dev/null; then
        echo -e "Sudo isn't installed. Please install sudo to run this bot."
        exit 1
    fi
    sudo echo "Sudo permission granted."
    main
else
    echo "Not an interactive terminal, skipping sudo."
    # run main function
    main
fi
