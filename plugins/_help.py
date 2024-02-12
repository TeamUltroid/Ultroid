# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

from telethon.errors.rpcerrorlist import (
    BotInlineDisabledError,
    BotMethodInvalidError,
    BotResponseTimeoutError,
)
from telethon.tl.custom import Button

from pyUltroid.dB._core import HELP, LIST
from pyUltroid.fns.tools import cmd_regex_replace

from . import HNDLR, LOGS, OWNER_NAME, asst, get_string, inline_pic, udB, ultroid_cmd

_main_help_menu = [
    [
        Button.inline(get_string("help_4"), data="uh_Official_"),
        Button.inline(get_string("help_5"), data="uh_Addons_"),
    ],
    [
        Button.inline(get_string("help_6"), data="uh_VCBot_"),
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


@ultroid_cmd(pattern="help( (.*)|$)")
async def _help(ult):
    plug = ult.pattern_match.group(1).strip()
    chat = await ult.get_chat()
    if plug:
        try:
            if plug in HELP["Official"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["Official"][plug]:
                    output += i
                output += "\n© @TeamUltroid"
                await ult.eor(output)
            elif HELP.get("Addons") and plug in HELP["Addons"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["Addons"][plug]:
                    output += i
                output += "\n© @TeamUltroid"
                await ult.eor(output)
            elif HELP.get("VCBot") and plug in HELP["VCBot"]:
                output = f"**Plugin** - `{plug}`\n"
                for i in HELP["VCBot"][plug]:
                    output += i
                output += "\n© @TeamUltroid"
                await ult.eor(output)
            else:
                try:
                    x = get_string("help_11").format(plug)
                    for d in LIST[plug]:
                        x += HNDLR + d
                        x += "\n"
                    x += "\n© @TeamUltroid"
                    await ult.eor(x)
                except BaseException:
                    file = None
                    compare_strings = []
                    for file_name in LIST:
                        compare_strings.append(file_name)
                        value = LIST[file_name]
                        for j in value:
                            j = cmd_regex_replace(j)
                            compare_strings.append(j)
                            if j.strip() == plug:
                                file = file_name
                                break
                    if not file:
                        # the enter command/plugin name is not found
                        text = f"`{plug}` is not a valid plugin!"
                        best_match = None
                        for _ in compare_strings:
                            if plug in _ and not _.startswith("_"):
                                best_match = _
                                break
                        if best_match:
                            text += f"\nDid you mean `{best_match}`?"
                        return await ult.eor(text)
                    output = f"**Command** `{plug}` **found in plugin** - `{file}`\n"
                    if file in HELP["Official"]:
                        for i in HELP["Official"][file]:
                            output += i
                    elif HELP.get("Addons") and file in HELP["Addons"]:
                        for i in HELP["Addons"][file]:
                            output += i
                    elif HELP.get("VCBot") and file in HELP["VCBot"]:
                        for i in HELP["VCBot"][file]:
                            output += i
                    output += "\n© @TeamUltroid"
                    await ult.eor(output)
        except BaseException as er:
            LOGS.exception(er)
            await ult.eor("Error 🤔 occured.")
    else:
        try:
            load = await ult.eor("✨")
            results = await ult.client.inline_query(asst.me.username, "ultd")
        except BotMethodInvalidError:
            z = []
            for x in LIST.values():
                z.extend(x)
            cmd = len(z) + 10
            if udB.get_key("MANAGER") and udB.get_key("DUAL_HNDLR") == "/":
                _main_help_menu[2:3] = [[Button.inline("• Manager Help •", "mngbtn")]]
            return await ult.reply(
                get_string("inline_4").format(
                    OWNER_NAME,
                    len(HELP["Official"]),
                    len(HELP["Addons"] if "Addons" in HELP else []),
                    cmd,
                ),
                file=inline_pic(),
                buttons=_main_help_menu,
            )
        except BotResponseTimeoutError:
            return await ult.eor(
                get_string("help_2").format(HNDLR),
            )
        except BotInlineDisabledError:
            return await ult.eor(get_string("help_3"))
        await load.delete()
        await results[0].click(chat.id, reply_to=ult.reply_to_msg_id, hide_via=True)
