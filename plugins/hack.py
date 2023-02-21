# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

• `{i}hack`
    Do a Prank With Replied user.

"""

import asyncio
import random

from . import *


@ultroid_cmd(pattern="hack")
async def _(event):
    animation_interval = 0.7
    animation_ttl = range(0, 11)
    xx = await event.eor("Installing..")
    animation_chars = [
        "`Installing Files To Hacked Private Server...`",
        "`Target Selected.`",
        "`Installing... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Installing... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Installing... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`lnstallig... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Installing... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Installing... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ `",
        "`Installing... 84%\n█████████████████████▒▒▒▒ `",
        "`Installing... 100%\n████████Installed██████████ `",
        "`Target files Uploading...\n\nDirecting To Remote  server to hack..`",
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await xx.edit(animation_chars[i % 11])
    await asyncio.sleep(2)
    animation_interval = 0.6
    animation_ttl = range(0, 14)
    await xx.edit("`Connecting nd getting combined token from my.telegram.org`")
    await asyncio.sleep(1)
    animation_chars = [
        "`root@anon:~#` ",
        "`root@anon:~# ls`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~#`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# `",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@anon:~# trap whoami`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@anon:~# trap whoami\n\nwhoami=user`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@anon:~# trap whoami\n\nwhoami=user\nboost_trap on force ...`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@anon:~# trap whoami\n\nwhoami=user\nboost_trap on force ...\nvictim detected in ghost ...`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@anon:~# trap whoami\n\nwhoami=user\nboost_trap on force ...\nvictim detected in ghost ...\n\nAll Done!`",
        "`root@anon:~# ls\n\n  usr  ghost  codes  \n\nroot@aono:~# # So Let's Hack it ...\nroot@anon:~# touch setup.py\n\nsetup.py deployed ...\nAuto CMD deployed ...\n\nroot@anon:~# trap whoami\n\nwhoami=user\nboost_trap on force ...\nvictim detected  in ghost ...\n\nAll Done!\nInstalling Token!\nToken=`DJ65gulO90P90nlkm65dRfc8I`",
    ]
    for i in animation_ttl:
        await asyncio.sleep(animation_interval)
        await xx.edit(animation_chars[i % 14])
    await asyncio.sleep(2)
    await xx.edit("`starting telegram hack`")
    await asyncio.sleep(1)
    # credit to kraken,sawan
    await xx.edit(
        "`hacking... 0%completed.\nTERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (1.3) kB`"
    )
    await asyncio.sleep(2)
    await xx.edit(
        " `hacking... 4% completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Package`"
    )
    await asyncio.sleep(1)
    await xx.edit(
        "`hacking.....6% completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target account chat\n lding chat tg-bot bruteforce finished`"
    )
    await asyncio.sleep(1)
    await xx.edit(
        "`hacking.....8%completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target account chat\n lding chat tg-bot bruteforce finished\n creating pdf of chat`"
    )
    await asyncio.sleep(1)
    await xx.edit(
        "`hacking....15%completed\n Terminal:chat history from telegram exporting to private database.\n terminal 874379gvrfghhuu5tlotruhi5rbh installing`"
    )
    await asyncio.sleep(1)
    await xx.edit(
        "`hacking....24%completed\n TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target account chat\n lding chat tg-bot bruteforce finished\nerminal:chat history from telegram exporting to private database.\n terminal 874379gvrfghhuu5tlotruhi5rbh installed\n creting data into pdf`"
    )
    await asyncio.sleep(1)
    await xx.edit(
        "`hacking....32%completed\n looking for use history \n downloading-telegram -id prtggtgf . gfr (12.99 mb)\n collecting data starting imprute attack to user account\n chat history from telegram exporting to private database.\n terminal 874379gvrfghhuu5tlotruhi5rbh installed\n creted data into pdf\nDownload sucessful Bruteforce-Telegram-0.1.tar.gz (1.3)`"
    )
    await asyncio.sleep(1)
    await xx.edit(
        "`hacking....38%completed\n\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Package\n  Downloading Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB): finished with status 'done'\nCreated wheel for telegram: filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e`"
    )
    await asyncio.sleep(1)
    await xx.edit(
        "`hacking....52%completed\nexterting data from telegram private server\ndone with status 36748hdeg \n checking for more data in device`"
    )
    await asyncio.sleep(2)
    await xx.edit(
        "`hacking....60%completed\nmore data found im target device\npreparing to download data\n process started with status 7y75hsgdt365ege56es \n status changed to up`"
    )
    await asyncio.sleep(1)
    await xx.edit(
        "`hacking....73% completed\n downloading data from device\n process completed with status 884hfhjh\nDownloading-0.1.tar.gz (9.3 kB)\nCollecting Data Packageseeing target\n lding chat tg-bot bruteforce finished\n creating pdf of chat`"
    )
    await asyncio.sleep(1)
    await xx.edit(
        "`hacking...88%completed\nall data from telegram private server downloaded\nterminal download sucessfull--with status jh3233fdg66y yr4vv.irh\n data collected from tg-bot\nTERMINAL:\n Bruteforce-Telegram-0.1.tar.gz (1.3)downloaded`"
    )
    await asyncio.sleep(0.5)
    await xx.edit(
        "`100%\n█████████HACKED███████████ `\n\n\n  TERMINAL:\nDownloading Bruteforce-Telegram-0.1.tar.gz (9.3 kB)\nCollecting Data Package\n  Downloading Telegram-Data-Sniffer-7.1.1-py2.py3-none-any.whl (82 kB)\nBuilding wheel for Tg-Bruteforcing (setup.py): finished with status 'done'\nCreated wheel for telegram: filename=Telegram-Data-Sniffer-0.0.1-py3-none-any.whl size=1306 sha256=cb224caad7fe01a6649188c62303cd4697c1869fa12d280570bb6ac6a88e6b7e\n  Stored in directory: `"
    )
    await asyncio.sleep(2)
    await xx.edit("`account hacked\n collecting all data\n converting data into pdf`")
    await asyncio.sleep(1)
    sub = "https://drive.google.com/file/d/"
    LINKS = [
        "1JNA0HY1v8ClBDU9PhmyQ-z8KuLgvteT5/view?usp=sharing",
        "1HXclQumyRIRy9STTiHcTAHpSMM2mj5ZF/view?usp=sharing",
    ]
    ME = sub + LINKS[random.randrange(0, len(LINKS))]
    MSG = "`pdf created click link below to download data\n\n"
    MSG += " Don't worry only i can open this 😎😎.. If u don't"
    MSG += f" Believe me, try to download` 🙂\n\n{ME}"
    await xx.edit(MSG)
