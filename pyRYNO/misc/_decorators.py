# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from .. import *
from ..utils import *
import re
import inspect
import sys
import asyncio
import requests
from telethon import *
from ..dB.database import Var
from ..dB.core import *
from ..functions.all import time_formatter as tf
from pathlib import Path
from traceback import format_exc
from time import gmtime, strftime, sleep
from asyncio import create_subprocess_shell as asyncsubshell, subprocess as asyncsub
from os import remove
from sys import *
from telethon.errors.rpcerrorlist import (
    FloodWaitError,
    MessageIdInvalidError,
    MessageNotModifiedError,
)
from ._wrappers import *


# sudo
ok = udB.get("SUDOS")
if ok:
    SUDO_USERS = set(int(x) for x in ok.split())
else:
    SUDO_USERS = ""

if SUDO_USERS:
    sudos = list(SUDO_USERS)
else:
    sudos = ""

on = udB.get("SUDO") if udB.get("SUDO") is not None else "False"

if on == "True":
    sed = [ultroid_bot.uid, *sudos]
else:
    sed = [ultroid_bot.uid]

hndlr = "\\" + HNDLR


# decorator


def ultroid_cmd(allow_sudo=on, **args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    pattern = args.get("pattern", None)
    groups_only = args.get("groups_only", False)
    admins_only = args.get("admins_only", False)
    disable_errors = args.get("disable_errors", False)
    trigger_on_fwd = args.get("trigger_on_fwd", False)
    args["outgoing"] = True

    if allow_sudo == "True":
        args["from_users"] = sed
        args["incoming"] = True

    else:
        args["outgoing"] = True

    if pattern is not None:
        if pattern.startswith(r"\#"):
            args["pattern"] = re.compile(pattern)
        else:
            args["pattern"] = re.compile(hndlr + pattern)
        reg = re.compile("(.*)")
        try:
            cmd = re.search(reg, pattern)
            try:
                cmd = (
                    cmd.group(1)
                    .replace("$", "")
                    .replace("?(.*)", "")
                    .replace("(.*)", "")
                    .replace("(?: |)", "")
                    .replace("| ", "")
                    .replace("( |)", "")
                    .replace("?((.|//)*)", "")
                    .replace("?P<shortname>\\w+", "")
                )
            except:
                pass
            try:
                LIST[file_test].append(cmd)
            except:
                LIST.update({file_test: [cmd]})
        except:
            pass
    args["blacklist_chats"] = True
    black_list_chats = list(Var.BLACKLIST_CHAT)
    if len(black_list_chats) > 0:
        args["chats"] = black_list_chats

    # check if the plugin should allow edited updates
    if "allow_edited_updates" in args and args["allow_edited_updates"]:
        args["allow_edited_updates"]
        del args["allow_edited_updates"]
    if "admins_only" in args:
        del args["admins_only"]
    if "groups_only" in args:
        del args["groups_only"]
    if "disable_errors" in args:
        del args["disable_errors"]
    if "trigger_on_fwd" in args:
        del args["trigger_on_fwd"]
    # check if the plugin should listen for outgoing 'messages'

    def decorator(func):
        async def wrapper(ult):
            chat = await ult.get_chat()
            if not trigger_on_fwd and ult.fwd_from:
                return
            if disable_errors:
                return
            if groups_only and ult.is_private:
                return await eod(ult, "`Use this in group/channel.`", time=3)
            if admins_only and not chat.admin_rights:
                return await eod(ult, "`I am not an admin.`", time=3)
            try:
                await func(ult)
            except MessageIdInvalidError:
                pass
            except MessageNotModifiedError:
                pass
            except FloodWaitError as fwerr:
                await ultroid_bot.asst.send_message(
                    Var.LOG_CHANNEL,
                    f"`FloodWaitError:\n{str(fwerr)}\n\nSleeping for {tf((fwerr.seconds + 10)*1000)}`",
                )
                sleep(fwerr.seconds + 10)
                await ultroid_bot.asst.send_message(
                    Var.LOG_CHANNEL,
                    "`Bot is working again`",
                )
            except events.StopPropagation:
                raise events.StopPropagation
            except KeyboardInterrupt:
                pass
            except BaseException as e:
                LOGS.exception(e)
                if not disable_errors:
                    date = strftime("%Y-%m-%d %H:%M:%S", gmtime())

                    text = """
**RYNO - Error Report!!**
You can either ignore this or report it to @OFFICIALRYNO.
"""

                    ftext = "\nDisclaimer:\nThis file uploaded ONLY here, "
                    ftext += "we logged only fact of error and date, "
                    ftext += "we respect your privacy, "
                    ftext += "you may not report this error if you've "
                    ftext += "any confidential data here, no one will see your data "
                    ftext += "if you choose not to do so.\n\n"
                    ftext += "--------START ULTROID CRASH LOG--------"
                    ftext += "\nDate: " + date
                    ftext += "\nGroup ID: " + str(ult.chat_id)
                    ftext += "\nSender ID: " + str(ult.sender_id)
                    ftext += "\n\nEvent Trigger:\n"
                    ftext += str(ult.text)
                    ftext += "\n\nTraceback info:\n"
                    ftext += str(format_exc())
                    ftext += "\n\nError text:\n"
                    ftext += str(sys.exc_info()[1])
                    ftext += "\n\n--------END RYNO CRASH LOG--------"

                    command = 'git log --pretty=format:"%an: %s" -5'

                    ftext += "\n\n\nLast 5 commits:\n"

                    process = await asyncsubshell(
                        command, stdout=asyncsub.PIPE, stderr=asyncsub.PIPE
                    )
                    stdout, stderr = await process.communicate()
                    result = str(stdout.decode().strip()) + str(stderr.decode().strip())

                    ftext += result

                    file = open("RYNO-log.txt", "w+")
                    file.write(ftext)
                    file.close()
                    key = (
                        requests.post(
                            "https://nekobin.com/api/documents", json={"content": ftext}
                        )
                        .json()
                        .get("result")
                        .get("key")
                    )
                    url = f"https://nekobin.com/{key}"
                    text += f"\nPasted [here]({url}) too."
                    if Var.LOG_CHANNEL:
                        Placetosend = Var.LOG_CHANNEL
                    else:
                        Placetosend = ultroid_bot.uid
                    await ultroid_bot.asst.send_file(
                        Placetosend,
                        "RYNO-log.txt",
                        caption=text,
                    )
                    remove("RYNO-log.txt")

        ultroid_bot.add_event_handler(wrapper, events.NewMessage(**args))
        try:
            LOADED[file_test].append(wrapper)
        except Exception:
            LOADED.update({file_test: [wrapper]})
        return wrapper

    return decorator
