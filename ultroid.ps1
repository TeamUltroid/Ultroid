$VerbosePreference = 'SilentlyContinue'
$ErrorActionPreference = 'Stop'

echo "Welcome to Ultroid!"
echo ""

# define vars
$SESSION_PS1_URL = "https://raw.githubusercontent.com/TeamUltroid/Ultroid/master/session.ps1"
$INSTALLER_PS1_URL = "https://raw.githubusercontent.com/TeamUltroid/Ultroid/master/scripts/windows/installer.ps1"

# arguements
$arg = $args[0]

# args switch case
switch ($arg)
{
    "--help" {
        echo "List of arguments:"
        echo "  --help: Show this help message"
        echo "  install: Install Ultroid"
        echo "  session: Generate session for Ultroid"
        echo "  start: Start Ultroid bot"
    }
    $null {
        echo "No arguement provided"
        echo "Use --help to see the list of arguments."
    }
    "install" {
        # check if --help
        if ($args[1] -eq "--help") {
            echo "Usage: ./ultroid.ps1 install [Options]"
            echo "Options:"
            echo "  --help: Show this help message"
        } else {

            # check if installer.ps1 exists in scripts/windows
            if (Test-Path -Path "scripts\windows\installer.ps1") {
                echo "installer.ps1 exists"
                echo "Running installer.ps1"
                Set-ExecutionPolicy Bypass -Scope Process -Force ; . .\scripts\windows\installer.ps1
            } else {
                echo "Fetching installer.ps1"
                # fetch and run installer.ps1 without downloading
                Set-ExecutionPolicy Bypass -Scope Process -Force ; Invoke-WebRequest -Uri $INSTALLER_PS1_URL | Invoke-Expression
            }
        }
    }
    "session" {
        # check if session.ps1 exists in root directory
        if (Test-Path -Path "scripts\windows\session.ps1") {
            echo "session.ps1 exists"
            echo "Running session.ps1"
            Set-ExecutionPolicy Bypass -Scope Process -Force ; . .\scripts\windows\session.ps1
        } else {
            echo "Fetching session.ps1"
            # fetch and run session.ps1 without downloading
            Set-ExecutionPolicy Bypass -Scope Process -Force ; Invoke-WebRequest -Uri $SESSION_PS1_URL | Invoke-Expression
        }
    }
    "start" {
        # check arguement if --help
        if ($args[1] -eq "--help") {
            echo "Usage: ./ultroid.ps1 start [Options]"
            echo "Options:"
            echo "  --help: Show this help message"
            echo "  --http-server: Start the bot with http server"
        } else {
            # directly running assuming that the bot is already installed
            echo "Starting Ultroid"
            Set-ExecutionPolicy Bypass -Scope Process -Force ; . .\scripts\windows\start.ps1
        }
    }
    default {
        echo "Invalid arguement provided"
        echo "Use --help to see the list of arguments."
    }
}
