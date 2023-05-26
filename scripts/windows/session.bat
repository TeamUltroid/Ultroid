:: Ultroid - UserBot
:: Copyright (C) 2020-2023 TeamUltroid
::
:: This file is a part of https://github.com/TeamUltroid/Ultroid/
:: PLease read the GNU Affero General Public License in https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/.

@echo off
cls
:::   _    _ _ _             _     _ 
:::  | |  | | | |           (_)   | |
:::  | |  | | | |_ _ __ ___  _  __| |
:::  | |  | | | __| '__/ _ \| |/ _  |
:::  | |__| | | |_| | | (_) | | (_| |
:::   \____/|_|\__|_|  \___/|_|\__,_|
for /f "delims=: tokens=*" %%A in ('findstr /b ::: "%~f0"') do @echo(%%A

echo Starting dependency installation in $sec seconds...

echo Installing Dependencies.
if exist resources/session/ssgen.py goto sessionStart
echo Fetching ssgen.py from GitHub...
curl https://raw.githubusercontent.com/TeamUltroid/Ultroid/main/resources/session/ssgen.py -o resources/session/ssgen.py

:sessionStart
cls
python resources/session/ssgen.py

exit /b 1