@echo off
echo Welcome to Ultroid!

set SESSION_BAT_URL=https://raw.githubusercontent.com/TeamUltroid/Ultroid/main/resources/scripts/windows/session.bat

if [%1]==[] goto noargs
if [%1]==[--help] goto help
if [%1]==[session] goto session
if [%1]==[start] goto ultStart
goto invalidargs

:noargs
echo No arguments provided.
echo Use --help to see the list of arguments.
goto end

:help
echo Usage: ./ultroid [options]
echo Options:
echo   --help: Show this help message
echo   session: Generate a new session
echo   start: Start the bot
goto end

:session
if exist scripts/windows/session.bat goto sessionStart
echo Fetching session generator from GitHub...
curl %SESSION_BAT_URL% -o scripts/windows/session.bat
goto sessionStart
goto end

:sessionStart
call scripts/windows/session.bat
goto end

:ultStart
call scripts/windows/startup.bat
goto end

:invalidargs
echo Invalid arguments provided.
goto end

:end
exit /b 1