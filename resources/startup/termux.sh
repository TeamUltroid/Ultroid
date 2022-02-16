echo "Updating System..\n\n"
pkg update -y
apt update
apt upgrade -y

python_not_installed="$(python -c 'exit()')"

# Install Python if n0t installed..
if [ python_not_installed ]
then
    echo "Installing Python..\nThis may take some long...\n"
    pkg install python3 -y
fi

echo "Running up Installation tool.\n"
python resources/startup/_termux.py
