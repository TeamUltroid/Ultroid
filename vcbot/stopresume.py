# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from . import *


@asst.on_message(
    filters.command(["stop", f"stop@{vcusername}"])
    & filters.user(VC_AUTHS())
    & ~filters.edited
)
async def stopvc(_, message):
    ms = message.text.split(" ", maxsplit=1)
    try:
        chat = (await Client.get_chat(ms[1])).id
    except IndexError:
        chat = message.chat.id
    except Exception as Ex:
        return await eor(message, str(Ex))
    CallsClient.pause_stream(chat)
    await eor(message, "Stopped Voice Call")


@Client.on_message(
    filters.command("stop", HNDLR) & filters.user(VC_AUTHS()) & ~filters.edited
)
async def ustop(_, message):
    await stopvc(_, message)


@asst.on_message(
    filters.command(["resume", f"resume@{vcusername}"])
    & filters.user(VC_AUTHS())
    & ~filters.edited
)
async def resume_vc(_, message):
    ms = message.text.split(" ", maxsplit=1)
    try:
        chat = (await Client.get_chat(ms[1])).id
    except IndexError:
        chat = message.chat.id
    except Exception as Ex:
        return await eor(message, str(Ex))
    CallsClient.resume_stream(chat)
    await eor(message, "Resumed VC")


@Client.on_message(
    filters.command("resume", HNDLR) & filters.user(VC_AUTHS()) & ~filters.edited
)
async def vcresume(_, message):
    await resume_vc(_, message)
