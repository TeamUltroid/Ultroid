# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import asyncio
import math
import os
import re
import sys
import time
from traceback import format_exc
from urllib.parse import unquote
from urllib.request import urlretrieve

from .. import run_as_module

if run_as_module:
    from ..configs import Var


try:
    from aiohttp import ClientSession as aiohttp_client
except ImportError:
    aiohttp_client = None
    try:
        import requests
    except ImportError:
        requests = None

try:
    import heroku3
except ImportError:
    heroku3 = None

try:
    from git import Repo
    from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
except ImportError:
    Repo = None


import asyncio
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps

from telethon.helpers import _maybe_await
from telethon.tl import types
from telethon.utils import get_display_name

from .._misc import CMD_HELP
from .._misc._wrappers import eod, eor
from ..exceptions import DependencyMissingError
from . import *

if run_as_module:
    from ..dB._core import ADDONS, HELP, LIST, LOADED

from ..version import ultroid_version
from .FastTelethon import download_file as downloadable
from .FastTelethon import upload_file as uploadable


def run_async(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(
            ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 5),
            partial(function, *args, **kwargs),
        )

    return wrapper


# ~~~~~~~~~~~~~~~~~~~~ small funcs ~~~~~~~~~~~~~~~~~~~~ #


def make_mention(user, custom=None):
    if user.username:
        return f"@{user.username}"
    return inline_mention(user, custom=custom)


def inline_mention(user, custom=None, html=False):
    mention_text = get_display_name(user) or "Deleted Account" if not custom else custom
    if isinstance(user, types.User):
        if html:
            return f"<a href=tg://user?id={user.id}>{mention_text}</a>"
        return f"[{mention_text}](tg://user?id={user.id})"
    if isinstance(user, types.Channel) and user.username:
        if html:
            return f"<a href=https://t.me/{user.username}>{mention_text}</a>"
        return f"[{mention_text}](https://t.me/{user.username})"
    return mention_text

async def check_reply_to(event):
    replytoIDS = [client.me.id]
    if (event.is_private and event.is_reply) or (
        event.is_reply and event.reply_to_msg_id
    ):
        try:
            replied_message = await event.client.get_messages(
                event.chat_id, ids=event.reply_to_msg_id
            )
            if replied_message.from_id:
                user_id = replied_message.from_id.user_id
                if user_id in replytoIDS:
                    return True
            elif replied_message.peer_id and not replied_message.from_id:
                channel_id = replied_message.peer_id.channel_id
                if channel_id in replytoIDS:
                    return True
            # If neither user_id nor channel_id is in truai, return False
            return False
        except Exception as e:
            # Log the exception for debugging
            print(f"Exception: {e}")
            return False
    return False

# ----------------- Load \\ Unloader ---------------- #


def un_plug(shortname):
    from .. import asst, ultroid_bot

    try:
        all_func = LOADED[shortname]
        for client in [ultroid_bot, asst]:
            for x, _ in client.list_event_handlers():
                if x in all_func:
                    client.remove_event_handler(x)
        del LOADED[shortname]
        del LIST[shortname]
        ADDONS.remove(shortname)
    except (ValueError, KeyError):
        name = f"addons.{shortname}"
        for client in [ultroid_bot, asst]:
            for i in reversed(range(len(client._event_builders))):
                ev, cb = client._event_builders[i]
                if cb.__module__ == name:
                    del client._event_builders[i]
                    try:
                        del LOADED[shortname]
                        del LIST[shortname]
                        ADDONS.remove(shortname)
                    except KeyError:
                        pass


if run_as_module:

    async def safeinstall(event):
        from .. import HNDLR
        from ..startup.utils import load_addons

        if not event.reply_to:
            return await eod(
                event, f"Please use `{HNDLR}install` as reply to a .py file."
            )
        ok = await eor(event, "`Installing...`")
        reply = await event.get_reply_message()
        if not (
            reply.media
            and hasattr(reply.media, "document")
            and reply.file.name
            and reply.file.name.endswith(".py")
        ):
            return await eod(ok, "`Please reply to any python plugin`")
        plug = reply.file.name.replace(".py", "")
        if plug in list(LOADED):
            return await eod(ok, f"Plugin `{plug}` is already installed.")
        sm = reply.file.name.replace("_", "-").replace("|", "-")
        dl = await reply.download_media(f"addons/{sm}")
        if event.text[9:] != "f":
            read = open(dl).read()
            for dan in KEEP_SAFE().All:
                if re.search(dan, read):
                    os.remove(dl)
                    return await ok.edit(
                        f"**Installation Aborted.**\n**Reason:** Occurance of `{dan}` in `{reply.file.name}`.\n\nIf you trust the provider and/or know what you're doing, use `{HNDLR}install f` to force install.",
                    )
        try:
            load_addons(dl)  # dl.split("/")[-1].replace(".py", ""))
        except BaseException:
            os.remove(dl)
            return await eor(ok, f"**ERROR**\n\n`{format_exc()}`", time=30)
        plug = sm.replace(".py", "")
        if plug in HELP:
            output = "**Plugin** - `{}`\n".format(plug)
            for i in HELP[plug]:
                output += i
            output += "\n© @TeamUltroid"
            await eod(ok, f"✓ `Ultroid - Installed`: `{plug}` ✓\n\n{output}")
        elif plug in CMD_HELP:
            output = f"Plugin Name-{plug}\n\n✘ Commands Available-\n\n"
            output += str(CMD_HELP[plug])
            await eod(ok, f"✓ `Ultroid - Installed`: `{plug}` ✓\n\n{output}")
        else:
            try:
                x = f"Plugin Name-{plug}\n\n✘ Commands Available-\n\n"
                for d in LIST[plug]:
                    x += HNDLR + d + "\n"
                await eod(ok, f"✓ `Ultroid - Installed`: `{plug}` ✓\n\n`{x}`")
            except BaseException:
                await eod(ok, f"✓ `Ultroid - Installed`: `{plug}` ✓")

    async def heroku_logs(event):
        """
        post heroku logs
        """
        from .. import LOGS

        xx = await eor(event, "`Processing...`")
        if not (Var.HEROKU_API and Var.HEROKU_APP_NAME):
            return await xx.edit(
                "Please set `HEROKU_APP_NAME` and `HEROKU_API` in vars."
            )
        try:
            app = (heroku3.from_key(Var.HEROKU_API)).app(Var.HEROKU_APP_NAME)
        except BaseException as se:
            LOGS.info(se)
            return await xx.edit(
                "`HEROKU_API` and `HEROKU_APP_NAME` is wrong! Kindly re-check in config vars."
            )
        await xx.edit("`Downloading Logs...`")
        ok = app.get_log()
        with open("ultroid-heroku.log", "w") as log:
            log.write(ok)
        await event.client.send_file(
            event.chat_id,
            file="ultroid-heroku.log",
            thumb=ULTConfig.thumb,
            caption="**Ultroid Heroku Logs.**",
        )

        os.remove("ultroid-heroku.log")
        await xx.delete()

    async def def_logs(ult, file):
        await ult.respond(
            "**Ultroid Logs.**",
            file=file,
            thumb=ULTConfig.thumb,
        )

    async def updateme_requirements():
        """Update requirements.."""
        await bash(
            f"{sys.executable} -m pip install --no-cache-dir -r requirements.txt"
        )

    @run_async
    def gen_chlog(repo, diff):
        """Generate Changelogs..."""
        UPSTREAM_REPO_URL = (
            Repo().remotes[0].config_reader.get("url").replace(".git", "")
        )
        ac_br = repo.active_branch.name
        ch_log = tldr_log = ""
        ch = f"<b>Ultroid {ultroid_version} updates for <a href={UPSTREAM_REPO_URL}/tree/{ac_br}>[{ac_br}]</a>:</b>"
        ch_tl = f"Ultroid {ultroid_version} updates for {ac_br}:"
        d_form = "%d/%m/%y || %H:%M"
        for c in repo.iter_commits(diff):
            ch_log += f"\n\n💬 <b>{c.count()}</b> 🗓 <b>[{c.committed_datetime.strftime(d_form)}]</b>\n<b><a href={UPSTREAM_REPO_URL.rstrip('/')}/commit/{c}>[{c.summary}]</a></b> 👨‍💻 <code>{c.author}</code>"
            tldr_log += f"\n\n💬 {c.count()} 🗓 [{c.committed_datetime.strftime(d_form)}]\n[{c.summary}] 👨‍💻 {c.author}"
        if ch_log:
            return str(ch + ch_log), str(ch_tl + tldr_log)
        return ch_log, tldr_log


# --------------------------------------------------------------------- #


async def bash(cmd, run_code=0):
    """
    run any command in subprocess and get output or error."""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip() or None
    out = stdout.decode().strip()
    if not run_code and err:
        if match := re.match("\/bin\/sh: (.*): ?(\w+): not found", err):
            return out, f"{match.group(2).upper()}_NOT_FOUND"
    return out, err


# ---------------------------UPDATER-------------------------------- #
# Will add in class


async def updater():
    from .. import LOGS

    try:
        off_repo = Repo().remotes[0].config_reader.get("url").replace(".git", "")
    except Exception as er:
        LOGS.exception(er)
        return
    try:
        repo = Repo()
    except NoSuchPathError as error:
        LOGS.info(f"`directory {error} is not found`")
        Repo().__del__()
        return
    except GitCommandError as error:
        LOGS.info(f"`Early failure! {error}`")
        Repo().__del__()
        return
    except InvalidGitRepositoryError:
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()
        repo.create_head("main", origin.refs.main)
        repo.heads.main.set_tracking_branch(origin.refs.main)
        repo.heads.main.checkout(True)
    ac_br = repo.active_branch.name
    repo.create_remote("upstream", off_repo) if "upstream" not in repo.remotes else None
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)
    changelog, tl_chnglog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    return bool(changelog)


# ----------------Fast Upload/Download----------------
# @1danish_00 @new-dev0 @buddhhu


async def uploader(file, name, taime, event, msg):
    with open(file, "rb") as f:
        result = await uploadable(
            client=event.client,
            file=f,
            filename=name,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    event,
                    taime,
                    msg,
                ),
            ),
        )
    return result


async def downloader(filename, file, event, taime, msg):
    with open(filename, "wb") as fk:
        result = await downloadable(
            client=event.client,
            location=file,
            out=fk,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d,
                    t,
                    event,
                    taime,
                    msg,
                ),
            ),
        )
    return result


# ~~~~~~~~~~~~~~~Async Searcher~~~~~~~~~~~~~~~
# @buddhhu


async def async_searcher(
    url: str,
    post: bool = False,
    head: bool = False,
    headers: dict = None,
    evaluate=None,
    object: bool = False,
    re_json: bool = False,
    re_content: bool = False,
    *args,
    **kwargs,
):
    if aiohttp_client:
        async with aiohttp_client(headers=headers) as client:
            method = client.head if head else (client.post if post else client.get)
            data = await method(url, *args, **kwargs)
            if evaluate:
                return await evaluate(data)
            if re_json:
                return await data.json()
            if re_content:
                return await data.read()
            if head or object:
                return data
            return await data.text()
    # elif requests:
    #     method = requests.head if head else (requests.post if post else requests.get)
    #     data = method(url, headers=headers, *args, **kwargs)
    #     if re_json:
    #         return data.json()
    #     if re_content:
    #         return data.content
    #     if head or object:
    #         return data
    #     return data.text
    else:
        raise DependencyMissingError("install 'aiohttp' to use this.")


# ~~~~~~~~~~~~~~~~~~~~DDL Downloader~~~~~~~~~~~~~~~~~~~~
# @buddhhu @new-dev0


async def download_file(link, name, validate=False):
    """for files, without progress callback with aiohttp"""

    async def _download(content):
        if validate and "application/json" in content.headers.get("Content-Type"):
            return None, await content.json()
        with open(name, "wb") as file:
            file.write(await content.read())
        return name, ""

    return await async_searcher(link, evaluate=_download)


async def fast_download(download_url, filename=None, progress_callback=None):
    if not aiohttp_client:
        return await download_file(download_url, filename)[0], None
    async with aiohttp_client() as session:
        async with session.get(download_url, timeout=None) as response:
            if not filename:
                filename = unquote(download_url.rpartition("/")[-1])
            total_size = int(response.headers.get("content-length", 0)) or None
            downloaded_size = 0
            start_time = time.time()
            with open(filename, "wb") as f:
                async for chunk in response.content.iter_chunked(1024):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                    if progress_callback and total_size:
                        await _maybe_await(
                            progress_callback(downloaded_size, total_size)
                        )
            return filename, time.time() - start_time


# --------------------------Media Funcs-------------------------------- #


def mediainfo(media):
    xx = str((str(media)).split("(", maxsplit=1)[0])
    m = ""
    if xx == "MessageMediaDocument":
        mim = media.document.mime_type
        if mim == "application/x-tgsticker":
            m = "sticker animated"
        elif "image" in mim:
            if mim == "image/webp":
                m = "sticker"
            elif mim == "image/gif":
                m = "gif as doc"
            else:
                m = "pic as doc"
        elif "video" in mim:
            if "DocumentAttributeAnimated" in str(media):
                m = "gif"
            elif "DocumentAttributeVideo" in str(media):
                i = str(media.document.attributes[0])
                if "supports_streaming=True" in i:
                    m = "video"
                m = "video as doc"
            else:
                m = "video"
        elif "audio" in mim:
            m = "audio"
        else:
            m = "document"
    elif xx == "MessageMediaPhoto":
        m = "pic"
    elif xx == "MessageMediaWebPage":
        m = "web"
    return m


# ------------------Some Small Funcs----------------


def time_formatter(milliseconds):
    minutes, seconds = divmod(int(milliseconds / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    tmp = (
        ((str(weeks) + "w:") if weeks else "")
        + ((str(days) + "d:") if days else "")
        + ((str(hours) + "h:") if hours else "")
        + ((str(minutes) + "m:") if minutes else "")
        + ((str(seconds) + "s") if seconds else "")
    )
    if not tmp:
        return "0s"

    if tmp.endswith(":"):
        return tmp[:-1]
    return tmp


def humanbytes(size):
    if not size:
        return "0 B"
    for unit in ["", "K", "M", "G", "T"]:
        if size < 1024:
            break
        size /= 1024
    if isinstance(size, int):
        size = f"{size}{unit}B"
    elif isinstance(size, float):
        size = f"{size:.2f}{unit}B"
    return size


def numerize(number):
    if not number:
        return None
    unit = ""
    for unit in ["", "K", "M", "B", "T"]:
        if number < 1000:
            break
        number /= 1000
    if isinstance(number, int):
        number = f"{number}{unit}"
    elif isinstance(number, float):
        number = f"{number:.2f}{unit}"
    return number


No_Flood = {}


async def progress(current, total, event, start, type_of_ps, file_name=None):
    now = time.time()
    if No_Flood.get(event.chat_id):
        if No_Flood[event.chat_id].get(event.id):
            if (now - No_Flood[event.chat_id][event.id]) < 1.1:
                return
        else:
            No_Flood[event.chat_id].update({event.id: now})
    else:
        No_Flood.update({event.chat_id: {event.id: now}})
    diff = time.time() - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        progress_str = "`[{0}{1}] {2}%`\n\n".format(
            "".join("●" for i in range(math.floor(percentage / 5))),
            "".join("" for i in range(20 - math.floor(percentage / 5))),
            round(percentage, 2),
        )

        tmp = (
            progress_str
            + "`{0} of {1}`\n\n`✦ Speed: {2}/s`\n\n`✦ ETA: {3}`\n\n".format(
                humanbytes(current),
                humanbytes(total),
                humanbytes(speed),
                time_formatter(time_to_completion),
            )
        )
        if file_name:
            await event.edit(
                "`✦ {}`\n\n`File Name: {}`\n\n{}".format(type_of_ps, file_name, tmp)
            )
        else:
            await event.edit("`✦ {}`\n\n{}".format(type_of_ps, tmp))


# ------------------System\\Heroku stuff----------------
# @xditya @sppidy @techierror


async def restart(ult=None):
    if Var.HEROKU_APP_NAME and Var.HEROKU_API:
        try:
            Heroku = heroku3.from_key(Var.HEROKU_API)
            app = Heroku.apps()[Var.HEROKU_APP_NAME]
            if ult:
                await ult.edit("`Restarting your app, please wait for a minute!`")
            app.restart()
        except BaseException as er:
            if ult:
                return await eor(
                    ult,
                    "`HEROKU_API` or `HEROKU_APP_NAME` is wrong! Kindly re-check in config vars.",
                )
            LOGS.exception(er)
    else:
        if len(sys.argv) == 1:
            os.execl(sys.executable, sys.executable, "-m", "pyUltroid")
        else:
            os.execl(
                sys.executable,
                sys.executable,
                "-m",
                "pyUltroid",
                sys.argv[1],
                sys.argv[2],
                sys.argv[3],
                sys.argv[4],
                sys.argv[5],
                sys.argv[6],
            )


async def shutdown(ult):
    from .. import HOSTED_ON, LOGS

    ult = await eor(ult, "Shutting Down")
    if HOSTED_ON == "heroku":
        if not (Var.HEROKU_APP_NAME and Var.HEROKU_API):
            return await ult.edit("Please Fill `HEROKU_APP_NAME` and `HEROKU_API`")
        dynotype = os.getenv("DYNO").split(".")[0]
        try:
            Heroku = heroku3.from_key(Var.HEROKU_API)
            app = Heroku.apps()[Var.HEROKU_APP_NAME]
            await ult.edit("`Shutting Down your app, please wait for a minute!`")
            app.process_formation()[dynotype].scale(0)
        except BaseException as e:
            LOGS.exception(e)
            return await ult.edit(
                "`HEROKU_API` and `HEROKU_APP_NAME` is wrong! Kindly re-check in config vars."
            )
    else:
        sys.exit()
