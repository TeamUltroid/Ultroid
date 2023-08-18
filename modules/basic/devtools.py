# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# Please read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from localization import get_help

__doc__ = get_help("devtools")

import contextlib
import inspect
import sys
import time
import traceback
from io import BytesIO, StringIO
from os import remove
from pprint import pprint

from telethon.utils import get_display_name

from utilities.tools import is_url_ok

try:
    import black
except ImportError:
    black = None

from os import remove

from telethon.tl import functions

from core.remote import rm
from database.helpers import get_random_color
from utilities.misc import json_parser
from utilities.tools import Carbon, safe_load
from telethon.errors import RPCError
from .. import *

Tasks = {}
fn = functions


@ultroid_cmd(
    pattern="sysinfo$",
)
async def _(e):
    xx = await e.eor(get_string("com_1"))
    x, y = await bash("neofetch|sed 's/\x1B\\[[0-9;\\?]*[a-zA-Z]//g' >> neo.txt")
    if y and y.endswith("NOT_FOUND"):
        return await xx.edit(f"Error: `{y}`")
    with open("neo.txt", "r", encoding="utf-8") as neo:
        p = (neo.read()).replace("\n\n", "")
    haa = await Carbon(code=p, file_name="neofetch", backgroundColor=get_random_color())
    if isinstance(haa, dict):
        LOGS.exception(haa)
        x, y = await bash("neofetch --stdout")
        await xx.edit(f"`{x}`")
    else:
        await e.reply(file=haa)
        await xx.delete()
    remove("neo.txt")


@ultroid_cmd(pattern="bash", fullsudo=True, only_devs=True)
async def bash_func(event):
    carb, rayso, yamlf = (
        udB.get_key("CARBON_ON_BASH"),
        udB.get_key("RAYSO_ON_BASH"),
        False,
    )
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
        if cmd.split()[0] in ["-c", "--carbon"]:
            cmd = cmd.split(maxsplit=1)[1]
            carb = True
        elif cmd.split()[0] in ["-r", "--rayso"]:
            cmd = cmd.split(maxsplit=1)[1]
            rayso = True
    except IndexError:
        return await event.eor(get_string("devs_1"), time=10)
    xx = await event.eor(get_string("com_1"))
    reply_to_id = event.reply_to_msg_id or event.id
    stdout, stderr = await bash(cmd, run_code=1)
    OUT = f"**☞ BASH\n\n• COMMAND:**\n`{cmd}` \n\n"
    err, out = "", ""
    if stderr:
        err = f"**• ERROR:** \n`{stderr}`\n\n"
    if stdout:
        if (carb or rayso) and (
            event.is_private
            or event.chat.admin_rights
            or event.chat.creator
            or event.chat.default_banned_rights.embed_links
        ):
            li = await Carbon(
                code=stdout,
                rayso=rayso,
                file_name="bash",
                download=True,
                backgroundColor=get_random_color(),
            )
            if isinstance(li, dict):
                await xx.edit(
                    f"Unknown Response from Carbon: `{li}`\n\nstdout`:{stdout}`\nstderr: `{stderr}`"
                )
                return
            with rm.get("graph", helper=True, dispose=True) as mod:
                url = mod.upload_file(li)
            OUT = f"[\xad]({url}){OUT}"
            out = "**• OUTPUT:**"
            remove(li)
        else:
            if "pip" in cmd and all(":" in line for line in stdout.split("\n")):
                try:
                    load = safe_load(stdout)
                    stdout = ""
                    for data in list(load.keys()):
                        res = load[data] or ""
                        if res and "http" not in str(res):
                            res = f"`{res}`"
                        stdout += f"**{data}**  :  {res}\n"
                    yamlf = True
                except Exception as er:
                    stdout = f"`{stdout}`"
                    LOGS.exception(er)
            else:
                stdout = f"`{stdout}`"
            out = f"**• OUTPUT:**\n{stdout}"
    if not stderr and not stdout:
        out = "**• OUTPUT:**\n`Success`"
    OUT += err + out
    if len(OUT) > 4096:
        ultd = err + out
        with BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "bash.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption=f"`{cmd}`" if len(cmd) < 998 else None,
                reply_to=reply_to_id,
            )

            await xx.delete()
        return
    await xx.edit(OUT, link_preview=not yamlf)


pp = pprint  # ignore: pylint
bot = ultroid = ultroid_bot


class u:
    _ = ""


def _parse_eval(value=None):
    if not value:
        return value
    if hasattr(value, "stringify"):
        with contextlib.suppress(TypeError):
            return value.stringify()
    if black and isinstance(value, (dict, list)):
        with contextlib.suppress(Exception):
            return black.format_str(str(value), mode=black.Mode())
    if isinstance(value, dict):
        with contextlib.suppress(BaseException):
            return json_parser(value, indent=1)
    elif isinstance(value, list):
        newlist = "["
        for index, child in enumerate(value):
            newlist += "\n  " + str(_parse_eval(child))
            if index < len(value) - 1:
                newlist += ","
        newlist += "\n]"
        return newlist
    return str(value)


@ultroid_cmd(pattern="eval", fullsudo=True, only_devs=True)
async def eval_func(event):
    try:
        cmd = event.text.split(maxsplit=1)[1]
    except IndexError:
        return await event.eor(get_string("devs_2"), time=5)
    xx = None
    mode = ""
    spli = cmd.split()

    async def get_():
        try:
            cm = cmd.split(maxsplit=1)[1]
        except IndexError:
            await event.eor("->> Wrong Format <<-")
            cm = None
        return cm

    if spli[0] in ["-s", "--silent"]:
        await event.delete()
        mode = "silent"
    elif spli[0] in ["-n", "-noedit"]:
        mode = "no-edit"
        xx = await event.reply(get_string("com_1"))
    elif spli[0] in ["-gs", "--source"]:
        mode = "gsource"
    elif spli[0] in ["-ga", "--args"]:
        mode = "g-args"
    if mode:
        cmd = await get_()
    if not cmd:
        return
    if mode != "silent" and not xx:
        xx = await event.eor(get_string("com_1"))
    if black:
        with contextlib.suppress(BaseException):
            cmd = black.format_str(cmd, mode=black.Mode())
    reply_to_id = event.reply_to_msg_id or event
    if (
        any(item in cmd for item in KEEP_SAFE().All)
        and not event.out
        and event.sender_id != ultroid_bot.uid
    ):
        warning = await event.forward_to(udB.get_config("LOG_CHANNEL"))
        await warning.reply(
            f"Malicious Activities suspected by {inline_mention(await event.get_sender())}"
        )
        _ignore_eval.append(event.sender_id)
        return await xx.edit(
            "`Malicious Activities suspected⚠️!\nReported to owner. Aborted this request!`"
        )
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    tima = time.time()
    try:
        # value = await aexec(cmd, event)
        # TODO: Eval can be cancelled
       # task = asyncio.create_task(aexec(cmd, event))
     #   task = asyncio.current_task()
    #    try:
#            task_id = int(list(Tasks.keys())[0])
   #     except IndexError:
       #     task_id = 0
        #task_id += 1
 #       task_id = str(task_id)
    #    Tasks[task_id] = task
     #   task.add_done_callback(lambda _: Tasks.pop(task_id))
      #  await asyncio.wait([task])
    #    value = task.result()
        value = await aexec(cmd, event)
    except RPCError as er:
        value = None
        exc = f"{er.__class__.__name__}: {er}"
    except Exception:
        value = None
        exc = traceback.format_exc()
    tima = time.time() - tima
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    if value:
        try:
            if mode == "gsource":
                stdout = inspect.getsource(value)
            elif mode == "g-args":
                args = inspect.signature(value).parameters.values()
                name = ""
                if hasattr(value, "__name__"):
                    name = value.__name__
                stdout = f"**{name}**\n\n" + "\n ".join([str(arg) for arg in args])
        except Exception:
            exc = traceback.format_exc()
    err = exc or stderr
    evaluation = stdout or _parse_eval(value)
    if mode == "silent":
        if err:
            msg = f"• <b>EVAL ERROR\n\n• CHAT:</b> <code>{get_display_name(event.chat)}</code> [<code>{event.chat_id}</code>]"
            msg += f"\n\n∆ <b>CODE:</b>\n<code>{cmd}</code>\n\n∆ <b>ERROR:</b>\n<code>{err}</code>"
            log_chat = udB.get_config("LOG_CHANNEL")
            if len(msg) > 4000:
                with BytesIO(msg.encode()) as out_file:
                    out_file.name = "Eval-Error.txt"
                return await event.client.send_message(
                    log_chat, f"`{cmd}`", file=out_file
                )
            await event.client.send_message(log_chat, msg, parse_mode="html")
        return
    tmt = tima * 1000
    timef = time_formatter(tmt)
    timeform = timef if timef != "0s" else f"{tmt:.3f}ms"
    if isinstance(evaluation, str) and not (await is_url_ok(evaluation, True)):
        evaluation = f"```{evaluation}```"
    final_output = (
        "__►__ **EVAL** (__in {}__)\n```{}``` ".format(
            timeform,
            cmd,
           
        )
    )
    if err:
        final_output += f"\n\n __►__ **ERROR**: \n`{err}`"
    elif not evaluation:
        evaluation = get_string("instu_4")
    if evaluation:
        final_output += f"\n\n __►__ **OUTPUT**: \n{evaluation}"
    if len(final_output) > 4096:
        final_output = str(evaluation)
        with BytesIO(final_output.encode()) as out_file:
            out_file.name = "eval.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption=f"```{cmd}```" if len(cmd) < 998 else None,
                reply_to=reply_to_id,
            )
        return await xx.delete()
    await xx.edit(final_output)


def _stringify(text=None, *args, **kwargs):
    if text:
        u._ = text
        text = _parse_eval(text)
    return print(text, *args, **kwargs)


async def aexec(code, event):
    exec(
        (
            "async def __aexec(e, client): "
            + "\n print = p = _stringify"
            + "\n message = event = e"
            + "\n u.r = reply = await event.get_reply_message()"
            + "\n chat = event.chat_id"
            + "\n u.lr = locals()"
        )
        + "".join(f"\n {l}" for l in code.split("\n"))
    )

    return await locals()["__aexec"](event, event.client)
