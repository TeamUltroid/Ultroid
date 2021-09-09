# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.
"""
✘ Commands Available -

• `{i}bash <cmds>`
    Run linux commands on telegram.

• `{i}eval <code>`
    Evaluate python commands on telegram.
    Shortcuts:
        client = bot = event.client
        e = event
        p = print
        reply = await event.get_reply_message()
        chat = event.chat_id

• `{i}cpp <code>`
    Run c++ code from Telegram.
    It should be the complete file base.

• `{i}sysinfo`
    Shows System Info.
"""
import io
import sys
import traceback
from os import remove
from pprint import pprint

from carbonnow import Carbon

from . import *


@ultroid_cmd(
    pattern="sysinfo$",
)
async def _(e):
    xx = await eor(e, "`Sending...`")
    x, y = await bash("neofetch|sed 's/\x1B\\[[0-9;\\?]*[a-zA-Z]//g' >> neo.txt")
    with open("neo.txt", "r") as neo:
        p = (neo.read()).replace("\n\n", "")
    ok = Carbon(base_url="https://carbonara.vercel.app/api/cook", code=p)
    haa = await ok.save("neofetch")
    await e.reply(file=haa)
    await xx.delete()
    remove("neofetch.jpg")
    remove("neo.txt")


@ultroid_cmd(pattern="bash", fullsudo=True, only_devs=True)
async def _(event):
    xx = await eor(event, "`Processing...`")
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await eor(xx, "`No cmd given`", time=10)
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    stdout, stderr = await bash(cmd)
    OUT = f"**☞ BASH\n\n• COMMAND:**\n`{cmd}` \n\n"
    if stderr:
        OUT += f"**• ERROR:** \n`{stderr}`\n\n"
    if stdout:
        _o = stdout.split("\n")
        o = "\n".join(_o)
        OUT += f"**• OUTPUT:**\n`{o}`"
    if not stderr and not stdout:
        OUT += "**• OUTPUT:**\n`Success`"
    if len(OUT) > 4096:
        ultd = OUT.replace("`", "").replace("**", "").replace("__", "")
        with io.BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "bash.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                thumb="resources/extras/ultroid.jpg",
                allow_cache=False,
                caption=f"`{cmd}`" if len(cmd) < 998 else None,
                reply_to=reply_to_id,
            )

            await xx.delete()
    else:
        await xx.edit(OUT)


p, pp = print, pprint  # ignore: pylint


@ultroid_cmd(pattern="eval", fullsudo=True, only_devs=True)
async def _(event):
    if len(event.text) > 5 and event.text[5] != " ":
        return
    xx = await eor(event, "`Processing ...`")
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await eor(xx, "`Give some python cmd`", time=5)
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    reply_to_id = event.message.id
    try:
        await aexec(cmd, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = (
        "__►__ **EVALPy**\n```{}``` \n\n __►__ **OUTPUT**: \n```{}``` \n".format(
            cmd,
            evaluation,
        )
    )
    if len(final_output) > 4096:
        ultd = final_output.replace("`", "").replace("**", "").replace("__", "")
        with io.BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "eval.txt"
            await event.client.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                thumb="resources/extras/ultroid.jpg",
                allow_cache=False,
                caption=f"```{cmd}```" if len(cmd) < 998 else None,
                reply_to=reply_to_id,
            )
            await xx.delete()
    else:
        await xx.edit(final_output)


async def aexec(code, event):
    exec(
        (
            (
                ("async def __aexec(e, client): " + "\n message = event = e")
                + "\n reply = await event.get_reply_message()"
            )
            + "\n chat = (await event.get_chat()).id"
        )
        + "".join(f"\n {l}" for l in code.split("\n"))
    )

    return await locals()["__aexec"](event, event.client)


DUMMY_CPP = """#include <iostream>
using namespace std;

int main(){
!code
}
"""


@ultroid_cmd(pattern="cpp", only_devs=True)
async def doie(e):
    match = e.text.split(" ", maxsplit=1)
    try:
        match = match[1]
    except IndexError:
        return await eor(e, "`Give Some C++ Code..`")
    msg = await eor(e, "`Processing...`")
    if "main(" not in match:
        new_m = ""
        for i in match.split("\n"):
            new_m += " " * 4 + i + "\n"
        match = DUMMY_CPP.replace("!code", new_m)
    open("cpp-ultroid.cpp", "w").write(match)
    m = await bash("g++ -o CppUltroid cpp-ultroid.cpp")
    o_cpp = f"• **Eval-Cpp**\n`{match}`"
    if m[1] != "":
        o_cpp += f"\n\n**• Error :**\n`{m[1]}`"
        if len(o_cpp) > 3000:
            with io.BytesIO(str.encode(o_cpp)) as out_file:
                out_file.name = "error.txt"
                return await msg.reply(f"`{match}`", file=out_file)
        return await eor(msg, o_cpp)
    m = await bash("./CppUltroid")
    if m[0] != "":
        o_cpp += f"\n\n**• Output :**\n`{m[0]}`"
    if m[1] != "":
        o_cpp += f"\n\n**• Error :**\n`{m[1]}`"
    if len(o_cpp) > 3000:
        with io.BytesIO(str.encode(o_cpp)) as out_file:
            out_file.name = "eval.txt"
            await msg.reply(f"`{match}`", file=out_file)
    else:
        await eor(msg, o_cpp)
    os.remove("CppUltroid")
    os.remove("cpp-ultroid.cpp")
