# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from pyUltroid.dB.core import *
from telethon.errors.rpcerrorlist import BotInlineDisabledError as dis
from telethon.errors.rpcerrorlist import BotMethodInvalidError
from telethon.errors.rpcerrorlist import BotResponseTimeoutError as rep

from . import *


@ultroid_cmd(pattern="help ?(.*)")
async def _help(ult):
    plug = ult.pattern_match.group(1)
    if plug:
        try:
            if plug in HELP:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP[plug]:
                    output += i
                output += "\n© @TeamUltroid"
                await eor(ult, output)
            elif plug in CMD_HELP:
                kk = f"Plugin Name-{plug}\n\n✘ Commands Available -\n\n"
                kk += str(CMD_HELP[plug])
                await eor(ult, kk)
            else:
                try:
                    x = f"Plugin Name-{plug}\n\n✘ Commands Available -\n\n"
                    for d in LIST[plug]:
                        x += HNDLR + d
                        x += "\n"
                    x += "\n© @TeamUltroid"
                    await eor(ult, x)
                except BaseException:
                    await eod(ult, get_string("help_1").format(plug), time=5)
        except BaseException:
            await eor(ult, "Error 🤔 occured.")
    else:
        tgbot = asst.me.username
        try:
            results = await ult.client.inline_query(tgbot, "ultd")
        except BotMethodInvalidError:
            z = []
            for x in LIST.values():
                for y in x:
                    z.append(y)
            cmd = len(z) + 10
            return await ult.client.send_message(
                ult.chat_id,
                get_string("inline_4").format(
                    OWNER_NAME,
                    len(PLUGINS) - 5,
                    len(ADDONS),
                    cmd,
                ),
                buttons=[
                    [
                        Button.inline("• Pʟᴜɢɪɴs", data="hrrrr"),
                        Button.inline("• Aᴅᴅᴏɴs", data="frrr"),
                    ],
                    [
                        Button.inline("Oᴡɴᴇʀ•ᴛᴏᴏʟꜱ", data="ownr"),
                        Button.inline("Iɴʟɪɴᴇ•Pʟᴜɢɪɴs", data="inlone"),
                    ],
                    [
                        Button.url(
                            "⚙️Sᴇᴛᴛɪɴɢs⚙️", url=f"https://t.me/{tgbot}?start=set"
                        ),
                    ],
                    [Button.inline("••Cʟᴏꜱᴇ••", data="close")],
                ],
            )
        except rep:
            return await eor(
                ult,
                get_string("help_2").format(HNDLR),
            )
        except dis:
            return await eor(ult, get_string("help_3"))
        await results[0].click(ult.chat_id, reply_to=ult.reply_to_msg_id, hide_via=True)
        await ult.delete()
