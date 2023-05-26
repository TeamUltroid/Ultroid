::!/usr/bin/env bash
:: Ultroid - UserBot
:: Copyright (C) 2021-2022 TeamUltroid
::
:: This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
:: PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

@echo off

:::      _    _ _ _             _     _ 
:::     | |  | | | |           (_)   | |
:::     | |  | | | |_ _ __ ___  _  __| |
:::     | |  | | | __| '__/ _ \| |/ _  |
:::     | |__| | | |_| | | (_) | | (_| |
:::      \____/|_|\__|_|  \___/|_|\__,_|
:::
:::      Visit @TheUltroid for updates!!

for /f "delims=: tokens=*" %%A in ('findstr /b ::: "%~f0"') do @echo(%%A

pip show telethon >nul 2>&1 || goto install

:install
pip install -r requirements.txt
pip install -r resources/extras/optional-requirements.txt
echo Installed all dependencies
echo Starting Ultroid.

python -m core