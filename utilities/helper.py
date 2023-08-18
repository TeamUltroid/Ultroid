# Ultroid - UserBot
# Copyright (C) 2020-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import asyncio
import math
import os
import requests
import re
import sys
import time
from traceback import format_exc
from inspect import getmembers, isfunction
from contextlib import suppress
from urllib.parse import unquote
import asyncio
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from database._core import LIST
from telethon.helpers import _maybe_await
from telethon.tl import types
from telethon.tl.types import (
    User,
    Channel,
    SendMessageUploadDocumentAction,
    DocumentAttributeAnimated,
    DocumentAttributeAudio,
    DocumentAttributeFilename,
    DocumentAttributeImageSize,
    DocumentAttributeSticker,
    DocumentAttributeVideo,
    Message,
)
from telethon.utils import get_display_name
from telethon.tl.functions.messages import SetTypingRequest
from . import *

from core.git import repo
from core.config import HOSTED_ON

from core.version import version
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


def fetch_sync(url, re_json=False, evaluate=None, method="GET", *args, **kwargs):
    methods = {"POST": requests.post, "HEAD": requests.head, "GET": requests.get}
#    print("fetching", url)
    output = methods.get(method, requests.get)(url, *args, **kwargs)

    if callable(evaluate):
        return evaluate(output)
    elif re_json:
        # type: ignore
        if "application/json" in output.headers.get("content-type", ""):
            return output.json()
        return output.text
    return output.content


async_searcher = fetch = run_async(fetch_sync)

# ~~~~~~~~~~~~~~~~~~~~ small funcs ~~~~~~~~~~~~~~~~~~~~ #


def get_all_files(path, extension=None):
    filelist = []
    for root, _, files in os.walk(path):
        if extension:
            files = filter(lambda e: e.endswith(extension), files)
        filelist.extend(os.path.join(root, file) for file in files)
    return sorted(filelist)


def inline_mention(user, custom=None, html=False):
    mention_text = custom or get_display_name(user) or "Deleted Account"
    if isinstance(user, User):
        if html:
            return f"<a href=tg://user?id={user.id}>{mention_text}</a>"
        return f"[{mention_text}](tg://user?id={user.id})"
    if isinstance(user, Channel) and user.username:
        if html:
            return f"<a href=https://t.me/{user.username}>{mention_text}</a>"
        return f"[{mention_text}](https://t.me/{user.username})"
    return mention_text


# ----------------- Load \\ Unloader ---------------- #


def unload_plugin(shortname):
    from core import ultroid_bot, asst

    if shortname.endswith(".py"):
        shortname = shortname[:-3]
    shortname = shortname.replace("/", ".").replace("\\", ".")
    try:
        mod = sys.modules[shortname]
    except KeyError:
        try:
            mod = sys.modules[f"modules.addons.{shortname}"]
        except KeyError:
            return
    with suppress(KeyError):
        del LIST[shortname]
    funcs = list(
        filter(
            lambda func: not func[0].startswith("__") and isfunction(func[1]),
            getmembers(mod),
        )
    )
    _removed = []
    for client in [ultroid_bot, asst]:
        for i, e in client.list_event_handlers():
            if i in funcs:
                client.remove_event_handler(i, e)
                _removed.append(i)
    return _removed



async def updateme_requirements():
    """Update requirements.."""
    await bash(f"{sys.executable} -m pip install --no-cache-dir -r requirements.txt")


# --------------------------------------------------------------------- #

class BashError(Exception):
    ...

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
            return out, f"{match[2].upper()}_NOT_FOUND"
    return out, err


# ---------------------------UPDATER-------------------------------- #
# Will add in class


def get_origin_upstream() -> tuple:
    branch = repo.active_branch()
    for remote in repo.remotes():
        repo.fetch_remote(remote)
    origin = repo.rev_parse(f"origin/{branch}")
    upstream = repo.rev_parse(branch)
    return (origin, upstream)


def check_update() -> bool:
    origin, upstream = get_origin_upstream()
    return origin != upstream


# ~~~~~~~~~~~~~~~~~~~~DDL Downloader~~~~~~~~~~~~~~~~~~~~
# @buddhhu @new-dev0


async def download_file(link, name, validate=False):
    """for files, without progress callback with aiohttp"""

    def _download(response):
        if validate and "application/json" in response.headers.get("Content-Type"):
            return None, response.json()
        with open(name, "wb") as file:
            file.write(response.content)
        return name, ""

    return await async_searcher(link, evaluate=_download)


async def fast_download(download_url, filename=None, progress_callback=None):
    session = requests.Session()
    response = session.get(download_url, timeout=None, stream=True)
    if not filename:
        filename = unquote(download_url.rpartition("/")[-1])
    total_size = int(response.headers.get("content-length", 0)) or None
    downloaded_size = 0
    start_time = time.time()
    with open(filename, "wb") as f:
        for chunk in response.iter_content(2**20):
            if chunk:
                f.write(chunk)
                downloaded_size += len(chunk)
            if progress_callback and total_size:
                await _maybe_await(progress_callback(downloaded_size, total_size))
    return filename, time.time() - start_time


# --------------------------Media Funcs-------------------------------- #


def mediainfo(message: Message) -> str:
    for _ in [
        "audio",
        "contact",
        "dice",
        "game",
        "geo",
        "gif",
        "invoice",
        "photo",
        "poll",
        "sticker",
        "venue",
        "video",
        "video_note",
        "voice",
        "document",
    ]:
        if getattr(message, _, None):
            if _ == "sticker":
                stickerType = {"video/webm": "video_sticker", 
                               "image/webp": "static_sticker",
                               "application/x-tgsticker": "animated_sticker"}
                return stickerType[message.document.mime_type]
            elif _ == "document":
                attributes = {
                    DocumentAttributeSticker: "sticker",
                    DocumentAttributeAnimated: "gif",
                    DocumentAttributeAudio: "audio",
                    types.DocumentAttributeCustomEmoji: "custom emoji",
                    DocumentAttributeVideo: "video",
                    DocumentAttributeImageSize: "photo",
                    }
                for __ in message.document.attributes:
                    if type(__) in attributes:
                        _i = attributes[type(__)]
                        if _i == "photo" and any(
                            isinstance(k, DocumentAttributeSticker)
                            for k in message.document.attributes
                        ):
                            _i = "sticker"
                        
                        return _i + " as document"
            return _
    return ""


# ------------------Some Small Funcs----------------


def time_with_fixed_format(years, months, weeks, days, hours, minutes, seconds):
    tmp = (
        ((f"{years} years ") if years else "")
        + ((f"{months} months ") if months else "")
        + ((f"{weeks} weeks ") if weeks else "")
        + ((f"{days} days ") if days else "")
        + ((f"{hours}:") if hours else "00:")
        + ((f"{minutes}:") if minutes else "00:")
        + ((f"{seconds}") if seconds else "00")
    )
    _ = re.search("(\d+:\d+:\d+)", tmp).group(0)
    _tmp = ":".join(
        str(k).zfill(2) for k in re.search("(\d+:\d+:\d+)", tmp).group(0).split(":")
    )
    return re.sub(_, _tmp, tmp)


def time_formatter(milliseconds, fixed_format=False):
    minutes, seconds = divmod(int(milliseconds / 1000), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    months, weeks = divmod(weeks, 4)
    years, months = divmod(months, 13)  # Because 13*4*7 is 364 days

    if fixed_format:
        return time_with_fixed_format(
            years, months, weeks, days, hours, minutes, seconds
        )
    tmp = (
        (f"{str(weeks)}w:" if weeks else "")
        + (f"{str(days)}d:" if days else "")
        + (f"{str(hours)}h:" if hours else "")
        + (f"{str(minutes)}m:" if minutes else "")
        + (f"{str(seconds)}s" if seconds else "")
    )
    if not tmp:
        return "0s"
    return tmp[:1] if tmp.endswith(":") else tmp


def humanbytes(size: int) -> str:
    size = int(size)
    if not size:
        return "0B"
    unit = ""
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z", "Y"]:
        if size < 1024:
            break
        size /= 1024
    if isinstance(size, int):
        size = f"{size}{unit}B"
    elif isinstance(size, float):
        size = f"{size:.2f}{unit}B"
    return size


def numerize(number: int) -> str:
    number = int(number)
    if not number:
        return ""
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
    if (
        No_Flood.get(event.chat_id, {}).get(event.id)
        and (now - No_Flood[event.chat_id][event.id]) < 1.1
    ):
        return
    else:
        No_Flood.update({event.chat_id: {event.id: now}})
    diff = time.time() - start
    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        time_to_completion = round((total - current) / speed) * 1000
        progress_str = "`[{0}{1}] {2}%`\n\n".format(
            "".join("●" for _ in range(math.floor(percentage / 5))),
            "".join("" for _ in range(20 - math.floor(percentage / 5))),
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
        if type_of_ps.startswith("Upload"):
            await event.client(
                SetTypingRequest(
                    event.chat_id, SendMessageUploadDocumentAction(round(percentage))
                )
            )
        if file_name:
            return await event.edit(
                f"`✦ {type_of_ps}`\n\n`File Name: {file_name}`\n\n{tmp}"
            )
        await event.edit(f"`✦ {type_of_ps}`\n\n{tmp}")


# ------------------System\\Heroku stuff----------------
# @xditya @sppidy @techierror


async def restart(ult=None):
    if HOSTED_ON == "heroku":
        from core.heroku import restart

        await restart(ult)
    else:
        # TODO: test multi client
        os.execl(sys.executable, sys.executable, "-m", "pyUltroid", *sys.argv[1:])


async def shutdown(ult):
    ult = await ult.eor("Shutting Down")
    if HOSTED_ON == "heroku":
        from core.heroku import shutdown

        await shutdown(ult)
    else:
        sys.exit()
