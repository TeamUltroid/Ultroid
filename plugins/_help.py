# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


from pyUltroid.dB._core import HELP, LIST
from telethon.errors.rpcerrorlist import (
    BotInlineDisabledError,
    BotMethodInvalidError,
    BotResponseTimeoutError,
)
from telethon.tl.custom import Button

from . import *

_main_help_menu = [
    [
        Button.inline(get_string("help_4"), data="hrrrr"),
        Button.inline(get_string("help_5"), data="frrr"),
    ],
    [
        Button.inline(get_string("help_6"), data="vc_helper"),
        Button.inline(get_string("help_7"), data="inlone"),
    ],
    [
        Button.inline(get_string("help_8"), data="ownr"),
        Button.url(
            get_string("help_9"), url=f"https://t.me/{asst.me.username}?start=set"
        ),
    ],
    [Button.inline(get_string("help_10"), data="close")],
]


@ultroid_cmd(pattern="help ?(.*)")
async def _help(ult):
    plug = ult.pattern_match.group(1)
    if plug:
        try:
            if plug in HELP["Official"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["Official"][plug]:
                    output += i
                output += "\n© @TeamUltroid"
                await eor(ult, output)
            elif HELP.get("Addons") and plug in HELP["Addons"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["Addons"][plug]:
                    output += i
                output += "\n© @TeamUltroid"
                await eor(ult, output)
            elif HELP.get("VCBot") and plug in HELP["VCBot"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["VCBot"][plug]:
                    output += i
                output += "\n© @TeamUltroid"
                await eor(ult, output)
            else:
                try:
                    x = get_string("help_11").format(plug)
                    for d in LIST[plug]:
                        x += HNDLR + d
                        x += "\n"
                    x += "\n© @TeamUltroid"
                    await eor(ult, x)
                except BaseException:
                    await eor(ult, get_string("help_1").format(plug), time=5)
        except BaseException as er:
            LOGS.exception(er)
            await eor(ult, "Error 🤔 occured.")
    else:
        try:
            results = await ult.client.inline_query(asst.me.username, "ultd")
        except BotMethodInvalidError:
            z = []
            for x in LIST.values():
                for y in x:
                    z.append(y)
            cmd = len(z) + 10
            if udB.get("MANAGER") and udB.get("DUAL_HNDLR") == "/":
                _main_help_menu[2:3] = [[Button.inline("• Manager Help •", "mngbtn")]]
            return await ult.reply(
                get_string("inline_4").format(
                    OWNER_NAME,
                    len(HELP["Official"]) - 5,
                    len(HELP["Addons"] if "Addons" in HELP else []),
                    cmd,
                ),
                file=INLINE_PIC,
                buttons=_main_help_menu,
            )
        except BotResponseTimeoutError:
            return await eor(
                ult,
                get_string("help_2").format(HNDLR),
            )
        except BotInlineDisabledError:
            return await eor(ult, get_string("help_3"))
        await results[0].click(ult.chat_id, reply_to=ult.reply_to_msg_id, hide_via=True)
        await ult.delete()
