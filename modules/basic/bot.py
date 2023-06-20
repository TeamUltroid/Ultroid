# Ultroid - UserBot
# Copyright (C) 2021-2022 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import os
import sys
import time

from core import start_time
from core.remote import rm
from core.git import repo
from database.helpers import get_random_color
from utilities.helper import bash, check_update, get_origin_upstream, time_formatter
from utilities.tools import Carbon

from .. import HOSTED_ON, get_string, udB, ultroid_cmd


@ultroid_cmd(pattern="ping$")
async def ping_func(event):
    """Show response time of bot."""
    start = time.time()
    x = await event.eor("Pong !")
    end = round((time.time() - start) * 1000)
    uptime = time_formatter((time.time() - start_time) * 1000)
    await x.edit(get_string("ping").format(end, uptime))


@ultroid_cmd(pattern="logs( (.*)|$)")
async def logs_func(event):
    """Get logs of the bot.

    Args:
        open - Send last 4000 characters of logs in a message.
        carbon - Send last 2500 characters of logs in carbon image.
        graph - Upload Logs on Telegraph"""
    arg = event.pattern_match.group(1).strip()
    if not arg:
        arg = udB.get_key("_LOG_MODE")
    elif arg != "file":
        udB.set_key("_LOG_MODE", arg)

    file_path = "ultroid.log"
    if arg == "open":
        with open(file_path, "r") as file:
            content = file.read()[-4000:]
        return await event.eor(f"`{content}`")
    elif arg == "carbon":
        event = await event.eor(get_string("com_1"))
        with open(file_path, "r") as f:
            code = f.read()[-2500:]
        file = await Carbon(
            file_name="ultroid-logs",
            code=code,
            backgroundColor=get_random_color(),
        )
        if isinstance(file, dict):
            return await event.eor(f"`{file}`")
        return await event.eor("**Ultroid Logs.**", file=file)
    elif arg == "graph":
        with rm.get("graph", helper=True, dispose=True) as mod:
            client = mod.get_client()
            with open(file_path, "r") as file:
                title = "Ultroid Logs"
                if pat := udB.get_key("_TG_LOG"):
                    page = client.edit_page(pat, title, content=[file.read()])
                else:
                    page = client.create_page(title=title, content=[file.read()])
                    udB.set_key("_TG_LOG", page["path"])
        return await event.eor(f'[Ultroid Logs]({page["url"]})', link_preview=True)
    await event.eor(file=file_path)


@ultroid_cmd(pattern="restart$")
async def restart_func(event):
    """Restart the bot."""
    event = await event.eor("Restarting...")
    self_ = "bot" if event.client.me.bot else "user"
    udB.set_key("_RESTART", [event.chat_id, event.id, self_])
    if HOSTED_ON == "heroku":
        from core.heroku import restart

        msg = restart()
        if msg is True:
            return
        await event.eor(msg)
    os.execl(sys.executable, sys.executable, "-m", "core")


@ultroid_cmd(pattern="update( (.*)|$)")
async def update_func(e):
    """Update the bot to it's latest release.

    Args:
        fast/soft - Fetch latest release without updating changed dependencies."""
    xx = await e.eor(get_string("upd_1"))
    cmd = e.pattern_match.group(1).strip()
    if cmd and ("fast" in cmd or "soft" in cmd):
        await bash("git pull -f")
        #        call_back()
        await xx.edit(get_string("upd_7"))
        os.execl(sys.executable, sys.executable, "-m", "core")
        # return
    remote_url = repo.get_remote_url()
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]
    m = check_update()
    if not m:
        branch = repo.active_branch()
        return await xx.edit(
            f'<code>Your BOT is </code><strong>up-to-date</strong><code> with </code><strong><a href="{remote_url}/tree/{branch}">[{branch}]</a></strong>',
            parse_mode="html",
            link_preview=False,
        )
    org, up = get_origin_upstream()
    msg = await xx.eor(
        f'<strong><a href="{remote_url}/compare/{up}...{org}">[ChangeLogs]</a></strong>\n<code>Updating...</code>',
        parse_mode="html",
        link_preview=False,
    )
    await update(msg)


async def update(eve):
    if HOSTED_ON == "heroku":
        from core.heroku import update

        return await update(eve)
    else:
        # call_back()
        await bash(f"git pull && {sys.executable} -m pip install -r requirements.txt")
        os.execl(sys.executable, sys.executable, "-m", "core")
