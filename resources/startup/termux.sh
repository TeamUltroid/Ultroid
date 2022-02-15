echo "Updating System.."
pkg update -y
apt update
apt upgrade -y

python_not_installed="$(python -c 'exit()')"

# Install Python if n0t installed..
if [python_not_installed]
then
    echo "Installing Python..\nThis may take some long..."
    pkg install python3 -y
fi

echo "Running up Installation tool."
python ./_termux.py