import os
import time

from . import *


async def evalJs(
    event,
    startTime: float,
    command: str = "",
):
    finalCommand = str(command).replace('"', "'")
    os.system(f'node ./ecmaHelper/eval.d.js "{finalCommand}"')
    if not os.path.exists("./ecmaHelper/evalJs.result.d.txt"):
        return await eor(
            event,
            f"**☞ evalJS\n\n• Command:**\n`{command}` \n\n• timeTaken:**\n`{time.time() - startTime:.2f}` \n\n**• Result: **\n`[Warning]: No Output`",
        )
    result = open("./ecmaHelper/evalJs.result.d.txt", encoding="utf-8", mode="r")
    print('here is result:', result)
    if str(result.read()) == "":
        await eor(
            event,
            f"**☞ evalJS\n\n• Command:**\n`{command}` \n\n• timeTaken:**\n`{time.time() - startTime:.2f}` \n\n**• Result: **\n`[Warning]: No Output`",
        )
    else:
        await eor(
            event,
            f"**☞ evalJS\n\n• Command:**\n`{command}` \n\n• timeTaken:**\n`{time.time() - startTime:.2f}` \n\n**• Result:**\n`{result.read()}`",
        )
    result.close()
    file = open("./ecmaHelper/evalJs.result.d.txt", encoding="utf-8", mode="w")
    file.write("'use-strict';\n")
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
        await evalJs(
            event,
            command=cmd,
            startTime=start,
        )
