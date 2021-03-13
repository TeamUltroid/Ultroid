# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import random
import re
import time
from datetime import datetime
from math import ceil
from platform import python_version as pyver

from git import Repo
from support import *
from telethon import Button, __version__
from telethon.tl.types import InputWebDocument

from . import *

# ================================================#
notmine = "This bot is for {}".format(OWNER_NAME)
ULTROID_PIC = "https://telegra.ph/file/11245cacbffe92e5d5b14.jpg"
helps = get_string("inline_1")

add_ons = udB.get("ADDONS")
if add_ons:
    zhelps = get_string("inline_2")
else:
    zhelps = get_string("inline_3")
# ============================================#


@inline
@in_owner
async def e(o):
    if len(o.text) == 0:
        b = o.builder
        uptime = grt((time.time() - start_time))
        ALIVEMSG = get_string("alive_1").format(
            OWNER_NAME,
            ultroid_version,
            uptime,
            pyver(),
            __version__,
            Repo().active_branch,
        )
        res = [
                await b.article(
                title="Ultroid Userbot",
                url="https://t.me/TeamUltroid",
                description="Userbot | Telethon ",
                text=ALIVEMSG,
                thumb=InputWebDocument(ULTROID_PIC, 0, "image/jpeg", []),
                buttons=[
                    [Button.url(text="Support Group", url="t.me/UltroidSupport")],
                    [
                        Button.url(
                            text="Repo", url="https://github.com/Teamultroid/Ultroid"
                        )
                    ],
                ],
            )
        ]
        await o.answer(res, switch_pm=f"👥 ULTROID PORTAL", switch_pm_param="start")


if Var.BOT_USERNAME is not None and asst is not None:

    @inline
    @in_owner
    async def inline_handler(event):
        builder = event.builder
        result = None
        query = event.text
        if event.query.user_id in sed and query.startswith("ultd"):
            z = []
            for x in LIST.values():
                for y in x:
                    z.append(y)
            cmd = len(z) + 10
            bn = Var.BOT_USERNAME
            if bn.startswith("@"):
                bnn = bn.replace("@", "")
            else:
                bnn = bn
            result = builder.article(
                title="Help Menu",
                description="Help Menu - UserBot | Telethon ",
                url="https://t.me/TheUltroid",
                thumb=InputWebDocument(ULTROID_PIC, 0, "image/jpeg", []),
                text=get_string("inline_4").format(
                    OWNER_NAME, len(PLUGINS) - 5, len(ADDONS), cmd
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
                            "⚙️Sᴇᴛᴛɪɴɢs⚙️",
                            url=f"https://t.me/{bnn}?start={ultroid_bot.me.id}",
                        )
                    ],
                    [Button.inline("••Cʟᴏꜱᴇ••", data="close")],
                ],
            )
            await event.answer([result] if result else None)
        elif event.query.user_id in sed and query.startswith("paste"):
            ok = query.split("-")[1]
            link = f"https://nekobin.com/{ok}"
            link_raw = f"https://nekobin.com/raw/{ok}"
            result = builder.article(
                title="Paste",
                text="Pᴀsᴛᴇᴅ Tᴏ Nᴇᴋᴏʙɪɴ!",
                buttons=[
                    [
                        Button.url("NekoBin", url=f"{link}"),
                        Button.url("Raw", url=f"{link_raw}"),
                    ]
                ],
            )
            await event.answer([result] if result else None)

    @inline
    @in_owner
    @callback("ownr")
    @owner
    async def setting(event):
        await event.edit(
            buttons=[
                [
                    Button.inline("•Pɪɴɢ•", data="pkng"),
                    Button.inline("•Uᴘᴛɪᴍᴇ•", data="upp"),
                ],
                [Button.inline("•Rᴇsᴛᴀʀᴛ•", data="rstrt")],
                [Button.inline("<- Bᴀᴄᴋ", data="open")],
            ],
        )

    @callback("pkng")
    async def _(event):
        start = datetime.now()
        end = datetime.now()
        ms = (end - start).microseconds / 1000
        pin = f"🌋Pɪɴɢ = {ms}ms"
        await event.answer(pin, cache_time=0, alert=True)

    @callback("upp")
    async def _(event):
        uptime = grt((time.time() - start_time))
        pin = f"🙋Uᴘᴛɪᴍᴇ = {uptime}"
        await event.answer(pin, cache_time=0, alert=True)

    @callback("inlone")
    @owner
    async def _(e):
        button = [
            [
                Button.switch_inline(
                    "Sᴇɴᴅ Oғғɪᴄɪᴀʟ Pʟᴜɢɪɴs",
                    query="send",
                    same_peer=True,
                )
            ],
            [
                Button.switch_inline(
                    "Pʟᴀʏ Sᴛᴏʀᴇ Aᴘᴘs",
                    query="app telegram",
                    same_peer=True,
                ),
                Button.switch_inline(
                    "Mᴏᴅᴅᴇᴅ Aᴘᴘs",
                    query="mods minecraft",
                    same_peer=True,
                ),
            ],
            [
                Button.switch_inline(
                    "Sᴇᴀʀᴄʜ Oɴ Gᴏᴏɢʟᴇ",
                    query="go TeamUltroid",
                    same_peer=True,
                ),
                Button.switch_inline(
                    "Sᴇᴀʀᴄʜ Oɴ Yᴀʜᴏᴏ",
                    query="yahoo TeamUltroid",
                    same_peer=True,
                ),
            ],
            [
                Button.switch_inline(
                    "YᴏᴜTᴜʙᴇ Dᴏᴡɴʟᴏᴀᴅᴇʀ",
                    query="yt Ed Sheeran Perfect",
                    same_peer=True,
                )
            ],
            [
                Button.switch_inline(
                    "Rᴇx Tᴇsᴛᴇʀ",
                    query="rex",
                    same_peer=True,
                ),
                Button.switch_inline(
                    "CʟɪᴘAʀᴛ Sᴇᴀʀᴄʜ",
                    query="clipart frog",
                    same_peer=True,
                ),
            ],
            [
                Button.inline(
                    "<- Bᴀᴄᴋ",
                    data="open",
                )
            ],
        ]
        await e.edit(buttons=button, link_preview=False)

    @callback("hrrrr")
    @owner
    async def on_plug_in_callback_query_handler(event):
        xhelps = helps.format(OWNER_NAME, len(PLUGINS) - 5)
        buttons = paginate_help(0, PLUGINS, "helpme")
        await event.edit(f"{xhelps}", buttons=buttons, link_preview=False)

    @callback("frrr")
    @owner
    async def addon(event):
        halp = zhelps.format(OWNER_NAME, len(ADDONS))
        if len(ADDONS) > 0:
            buttons = paginate_addon(0, ADDONS, "addon")
            await event.edit(f"{halp}", buttons=buttons, link_preview=False)
        else:
            await event.answer(
                f"• Tʏᴘᴇ `{HNDLR}setredis ADDONS True`\n Tᴏ ɢᴇᴛ ᴀᴅᴅᴏɴs ᴘʟᴜɢɪɴs",
                cache_time=0,
                alert=True,
            )

    @callback("rstrt")
    @owner
    async def rrst(ult):
        await restart(ult)

    @callback(
        re.compile(
            rb"helpme_next\((.+?)\)",
        ),
    )
    @owner
    async def on_plug_in_callback_query_handler(event):
        current_page_number = int(event.data_match.group(1).decode("UTF-8"))
        buttons = paginate_help(current_page_number + 1, PLUGINS, "helpme")
        await event.edit(buttons=buttons, link_preview=False)

    @callback(
        re.compile(
            rb"helpme_prev\((.+?)\)",
        ),
    )
    @owner
    async def on_plug_in_callback_query_handler(event):
        current_page_number = int(event.data_match.group(1).decode("UTF-8"))
        buttons = paginate_help(current_page_number - 1, PLUGINS, "helpme")
        await event.edit(buttons=buttons, link_preview=False)

    @callback(
        re.compile(
            rb"addon_next\((.+?)\)",
        ),
    )
    @owner
    async def on_plug_in_callback_query_handler(event):
        current_page_number = int(event.data_match.group(1).decode("UTF-8"))
        buttons = paginate_addon(current_page_number + 1, ADDONS, "addon")
        await event.edit(buttons=buttons, link_preview=False)

    @callback(
        re.compile(
            rb"addon_prev\((.+?)\)",
        ),
    )
    @owner
    async def on_plug_in_callback_query_handler(event):
        current_page_number = int(event.data_match.group(1).decode("UTF-8"))
        buttons = paginate_addon(current_page_number - 1, ADDONS, "addon")
        await event.edit(buttons=buttons, link_preview=False)

    @callback("back")
    @owner
    async def backr(event):
        xhelps = helps.format(OWNER_NAME, len(PLUGINS) - 5)
        current_page_number = int(upage)
        buttons = paginate_help(current_page_number, PLUGINS, "helpme")
        await event.edit(f"{xhelps}", buttons=buttons, link_preview=False)

    @callback("buck")
    @owner
    async def backr(event):
        xhelps = zhelps.format(OWNER_NAME, len(ADDONS))
        current_page_number = int(addpage)
        buttons = paginate_addon(current_page_number, ADDONS, "addon")
        await event.edit(f"{xhelps}", buttons=buttons, link_preview=False)

    @callback("open")
    @owner
    async def opner(event):
        bn = Var.BOT_USERNAME
        if bn.startswith("@"):
            bnn = bn.replace("@", "")
        else:
            bnn = bn
        buttons = [
            [
                Button.inline("• Pʟᴜɢɪɴs ", data="hrrrr"),
                Button.inline("• Aᴅᴅᴏɴs", data="frrr"),
            ],
            [
                Button.inline("Oᴡɴᴇʀ•Tᴏᴏʟꜱ", data="ownr"),
                Button.inline("Iɴʟɪɴᴇ•Pʟᴜɢɪɴs", data="inlone"),
            ],
            [
                Button.url(
                    "⚙️Sᴇᴛᴛɪɴɢs⚙️", url=f"https://t.me/{bnn}?start={ultroid_bot.me.id}"
                )
            ],
            [Button.inline("••Cʟᴏꜱᴇ••", data="close")],
        ]
        z = []
        for x in LIST.values():
            for y in x:
                z.append(y)
        cmd = len(z) + 10
        await event.edit(
            get_string("inline_4").format(
                OWNER_NAME, len(PLUGINS) - 5, len(ADDONS), cmd
            ),
            buttons=buttons,
            link_preview=False,
        )

    @callback("close")
    @owner
    async def on_plug_in_callback_query_handler(event):
        await event.edit(
            get_string("inline_5"),
            buttons=Button.inline("Oᴘᴇɴ Mᴀɪɴ Mᴇɴᴜ Aɢᴀɪɴ", data="open"),
        )

    @callback(
        re.compile(
            b"us_plugin_(.*)",
        ),
    )
    @owner
    async def on_plug_in_callback_query_handler(event):
        plugin_name = event.data_match.group(1).decode("UTF-8")
        help_string = f"Plugin Name - `{plugin_name}`\n"
        try:
            for i in HELP[plugin_name]:
                help_string += i
        except BaseException:
            pass
        if help_string == "":
            reply_pop_up_alert = "{} has no detailed help...".format(plugin_name)
        else:
            reply_pop_up_alert = help_string
        reply_pop_up_alert += "\n© @TheUltroid"
        try:
            if event.query.user_id in sed:
                await event.edit(
                    reply_pop_up_alert,
                    buttons=[
                        Button.inline("<- Bᴀᴄᴋ", data="back"),
                        Button.inline("••Cʟᴏꜱᴇ••", data="close"),
                    ],
                )
            else:
                reply_pop_up_alert = notmine
                await event.answer(reply_pop_up_alert, cache_time=0)
        except BaseException:
            halps = "Do .help {} to get the list of commands.".format(plugin_name)
            await event.edit(halps)

    @callback(
        re.compile(
            b"add_plugin_(.*)",
        ),
    )
    @owner
    async def on_plug_in_callback_query_handler(event):
        plugin_name = event.data_match.group(1).decode("UTF-8")
        help_string = ""
        try:
            for i in HELP[plugin_name]:
                help_string += i
        except BaseException:
            try:
                for u in CMD_HELP[plugin_name]:
                    help_string = (
                        f"Plugin Name-{plugin_name}\n\n✘ Commands Available-\n\n"
                    )
                    help_string += str(CMD_HELP[plugin_name])
            except BaseException:
                try:
                    if plugin_name in LIST:
                        help_string = (
                            f"Plugin Name-{plugin_name}\n\n✘ Commands Available-\n\n"
                        )
                        for d in LIST[plugin_name]:
                            help_string += HNDLR + d
                            help_string += "\n"
                except BaseException:
                    pass
        if help_string == "":
            reply_pop_up_alert = "{} has no detailed help...".format(plugin_name)
        else:
            reply_pop_up_alert = help_string
        reply_pop_up_alert += "\n© @TheUltroid"
        try:
            if event.query.user_id in sed:
                await event.edit(
                    reply_pop_up_alert,
                    buttons=[
                        Button.inline("<- Bᴀᴄᴋ", data="buck"),
                        Button.inline("••Cʟᴏꜱᴇ••", data="close"),
                    ],
                )
            else:
                reply_pop_up_alert = notmine
                await event.answer(reply_pop_up_alert, cache_time=0)
        except BaseException:
            halps = "Do .help {} to get the list of commands.".format(plugin_name)
            await event.edit(halps)


def paginate_help(page_number, loaded_plugins, prefix):
    number_of_rows = 5
    number_of_cols = 2
    emoji = Redis("EMOJI_IN_HELP")
    if emoji:
        multi, mult2i = emoji, emoji
    else:
        multi, mult2i = "✘", "✘"
    helpable_plugins = []
    global upage
    upage = page_number
    for p in loaded_plugins:
        if not p.startswith("_"):
            helpable_plugins.append(p)
    helpable_plugins = sorted(helpable_plugins)
    modules = [
        Button.inline(
            "{} {} {}".format(
                random.choice(list(multi)), x, random.choice(list(mult2i))
            ),
            data="us_plugin_{}".format(x),
        )
        for x in helpable_plugins
    ]
    pairs = list(zip(modules[::number_of_cols], modules[1::number_of_cols]))
    if len(modules) % number_of_cols == 1:
        pairs.append((modules[-1],))
    max_num_pages = ceil(len(pairs) / number_of_rows)
    modulo_page = page_number % max_num_pages
    if len(pairs) > number_of_rows:
        pairs = pairs[
            modulo_page * number_of_rows : number_of_rows * (modulo_page + 1)
        ] + [
            (
                Button.inline(
                    "<- Pʀᴇᴠɪᴏᴜs", data="{}_prev({})".format(prefix, modulo_page)
                ),
                Button.inline("-Bᴀᴄᴋ-", data="open"),
                Button.inline(
                    "Nᴇxᴛ ->", data="{}_next({})".format(prefix, modulo_page)
                ),
            )
        ]
    else:
        pairs = pairs[
            modulo_page * number_of_rows : number_of_rows * (modulo_page + 1)
        ] + [(Button.inline("-Bᴀᴄᴋ-", data="open"),)]
    return pairs


def paginate_addon(page_number, loaded_plugins, prefix):
    number_of_rows = 5
    number_of_cols = 2
    emoji = Redis("EMOJI_IN_HELP")
    if emoji:
        multi, mult2i = emoji, emoji
    else:
        multi, mult2i = "✘", "✘"
    helpable_plugins = []
    global addpage
    addpage = page_number
    for p in loaded_plugins:
        if not p.startswith("_"):
            helpable_plugins.append(p)
    helpable_plugins = sorted(helpable_plugins)
    modules = [
        Button.inline(
            "{} {} {}".format(
                random.choice(list(multi)), x, random.choice(list(mult2i))
            ),
            data="add_plugin_{}".format(x),
        )
        for x in helpable_plugins
    ]
    pairs = list(zip(modules[::number_of_cols], modules[1::number_of_cols]))
    if len(modules) % number_of_cols == 1:
        pairs.append((modules[-1],))
    max_num_pages = ceil(len(pairs) / number_of_rows)
    modulo_page = page_number % max_num_pages
    if len(pairs) > number_of_rows:
        pairs = pairs[
            modulo_page * number_of_rows : number_of_rows * (modulo_page + 1)
        ] + [
            (
                Button.inline(
                    "<- Pʀᴇᴠɪᴏᴜs", data="{}_prev({})".format(prefix, modulo_page)
                ),
                Button.inline("-Bᴀᴄᴋ-", data="open"),
                Button.inline(
                    "Nᴇxᴛ ->", data="{}_next({})".format(prefix, modulo_page)
                ),
            )
        ]
    else:
        pairs = pairs[
            modulo_page * number_of_rows : number_of_rows * (modulo_page + 1)
        ] + [(Button.inline("-Bᴀᴄᴋ-", data="open"),)]
    return pairs
