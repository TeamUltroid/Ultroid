import os
import time
from threading import Thread

from . import *


async def evalJs(
    event,
    startTime: float,
    command: str = "",
):
    os.system(f"node ecmaHelper/eval.d.js {command}")
    result = open("./ecmaHelper/evalJs.result.d.txt", encoding="utf-8")
    if str(result.read()) == "":
        await eor(
            event,
            f"**☞ evalJS\n\n• Command:**\n`{command}` \n\n• timeTaken:**\n`{time.time() - startTime:.2f}` \n\n**• Result: **\n`[Warning]: No Output`",
        )
    else:
        await eor(
            event,
            f"**☞ evalJS\n\n• Command:**\n`{command}` \n\n• timeTaken:**\n`{time.time() - startTime:.2f}` \n\n**• Result: **\n`{str(result.read())}`",
        )
    result.close()
    file = open("./ecmaHelper/evalJs.result.d.txt", encoding="utf-8")
    file.write("")
    file.close()


@ultroid_cmd(
    pattern="js",
)
async def _(event):
    start = time.time()
    if not event.out and not is_fullsudo(event.sender_id):
        return await eor(event, "`This Command Is Sudo Restricted.`")
    if Redis("I_JS_DEV") != "True":
        await eor(
            event,
            f"Developer Restricted!\nIf you know what this does, and want to proceed\n\n {HNDLR}setredis I_JS_DEV True\n\nThis Might Be Dangerous.",
        )
        return
    xx = await eor(event, "`Processing ...`")
    try:
        cmd = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await eod(xx, "`Give some js cmd`", time=7)
    if cmd and cmd != "":
        jsThread = Thread(
            target=await evalJs(
                event,
                command=cmd,
                startTime=start,
            )
        )
        jsThread.start()
