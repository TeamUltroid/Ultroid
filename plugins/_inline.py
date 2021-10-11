# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import re
import time
from datetime import datetime
from math import ceil
from os import remove

from git import Repo
from pyUltroid.dB._core import HELP, LIST
from pyUltroid.functions.helper import gen_chlog, time_formatter, updater
from pyUltroid.misc import CMD_HELP, owner_and_sudos
from pyUltroid.misc._assistant import callback, in_pattern
from telethon import Button
from telethon.tl.types import InputWebDocument, Message
from telethon.utils import resolve_bot_file_id

from . import HNDLR, INLINE_PIC, LOGS, OWNER_NAME, asst, get_string, start_time, udB
from ._help import _main_help_menu

# ================================================#
notmine = f"This bot is for {OWNER_NAME}"

TLINK = INLINE_PIC or "https://telegra.ph/file/d9c9bc13647fa1d96e764.jpg"
helps = get_string("inline_1")

add_ons = udB.get("ADDONS")
if add_ons == "True" or add_ons is None:
    zhelps = get_string("inline_2")
else:
    zhelps = get_string("inline_3")


upage = 0
# ============================================#

# --------------------BUTTONS--------------------#

SUP_BUTTONS = [
    [
        Button.url("• Repo •", url="https://github.com/TeamUltroid/Ultroid"),
        Button.url("• Support •", url="t.me/UltroidSupport"),
    ],
]

# --------------------BUTTONS--------------------#


@in_pattern(owner=True, func=lambda x: not x.text)
async def inline_alive(o):
    MSG = "• **Ultroid Userbot •**"
    WEB0 = InputWebDocument(
        "https://telegra.ph/file/55dd0f381c70e72557cb1.jpg", 0, "image/jpg", []
    )
    RES = [
        await o.builder.article(
            type="photo",
            text=MSG,
            include_media=True,
            buttons=SUP_BUTTONS,
            title="Ultroid Userbot",
            description="Userbot | Telethon",
            url=TLINK,
            thumb=WEB0,
            content=InputWebDocument(TLINK, 0, "image/jpg", []),
        )
    ]
    await o.answer(RES, switch_pm="👥 ULTROID PORTAL", switch_pm_param="start")


@in_pattern("ultd", owner=True)
async def inline_handler(event):
    z = []
    PLUGINS = HELP["Official"] if "Official" in HELP.keys() else []
    ADDONS = HELP["Addons"] if "Addons" in HELP.keys() else []
    for x in LIST.values():
        for y in x:
            z.append(y)
    text = get_string("inline_4").format(
        OWNER_NAME,
        len(PLUGINS),
        len(ADDONS),
        len(z),
    )
    if INLINE_PIC:
        result = await event.builder.photo(
            file=INLINE_PIC,
            link_preview=False,
            text=text,
            buttons=_main_help_menu,
        )
    else:
        result = await event.builder.article(
            title="Ultroid Help Menu", text=text, buttons=_main_help_menu
        )
    await event.answer([result], gallery=True)


@in_pattern("pasta", owner=True)
async def _(event):
    ok = event.text.split("-")[1]
    link = "https://spaceb.in/" + ok
    raw = f"https://spaceb.in/api/v1/documents/{ok}/raw"
    result = await event.builder.article(
        title="Paste",
        text="Pasted to Spacebin 🌌",
        buttons=[
            [
                Button.url("SpaceBin", url=link),
                Button.url("Raw", url=raw),
            ],
        ],
    )
    await event.answer([result])


@callback("ownr", owner=True)
async def setting(event):
    z = []
    PLUGINS = HELP["Official"] if "Official" in HELP.keys() else []
    ADDONS = HELP["Addons"] if "Addons" in HELP.keys() else []
    for x in LIST.values():
        for y in x:
            z.append(y)
    await event.edit(
        get_string("inline_4").format(
            OWNER_NAME,
            len(PLUGINS),
            len(ADDONS),
            len(z),
        ),
        file=INLINE_PIC,
        link_preview=False,
        buttons=[
            [
                Button.inline("•Pɪɴɢ•", data="pkng"),
                Button.inline("•Uᴘᴛɪᴍᴇ•", data="upp"),
            ],
            [
                Button.inline("•Stats•", data="alive"),
                Button.inline("•Uᴘᴅᴀᴛᴇ•", data="doupdate"),
            ],
            [Button.inline("« Bᴀᴄᴋ", data="open")],
        ],
    )


@callback(data="vc_helper", owner=True)
async def on_vc_callback_query_handler(event):
    xhelps = get_string("inline_6").format(OWNER_NAME, len(HELP["VCBot"]))
    try:
        buttons = page_num(0, HELP["VCBot"].keys(), "vchelp", "vc")
    except (ZeroDivisionError, KeyError):
        return await event.answer("Vc not Active.")
    await event.edit(xhelps, file=INLINE_PIC, buttons=buttons, link_preview=False)


@callback(data="doupdate", owner=True)
async def _(event):
    if not updater():
        return await event.answer(get_string("inline_9"), cache_time=0, alert=True)
    if not INLINE_PIC:
        return await event.answer(f"Do {HNDLR}update")
    repo = Repo.init()
    ac_br = repo.active_branch
    changelog, tl_chnglog = gen_chlog(repo, f"HEAD..upstream/{ac_br}")
    changelog_str = changelog + "\n\n" + get_string("inline_8")
    if len(changelog_str) > 1024:
        await event.edit(get_string("upd_4"))
        with open("ultroid_updates.txt", "w+") as file:
            file.write(tl_chnglog)
        await event.edit(
            get_string("upd_5"),
            file="ultroid_updates.txt",
            buttons=[
                [Button.inline("• Uᴘᴅᴀᴛᴇ Nᴏᴡ •", data="updatenow")],
                [Button.inline("« Bᴀᴄᴋ", data="ownr")],
            ],
        )
        remove("ultroid_updates.txt")
    else:
        await event.edit(
            changelog_str,
            buttons=[
                [Button.inline("Update Now", data="updatenow")],
                [Button.inline("« Bᴀᴄᴋ", data="ownr")],
            ],
            parse_mode="html",
        )


@callback(data="pkng", owner=True)
async def _(event):
    start = datetime.now()
    end = datetime.now()
    ms = (end - start).microseconds
    pin = f"🌋Pɪɴɢ = {ms} microseconds"
    await event.answer(pin, cache_time=0, alert=True)


@callback(data="upp", owner=True)
async def _(event):
    uptime = time_formatter((time.time() - start_time) * 1000)
    pin = f"🙋Uᴘᴛɪᴍᴇ = {uptime}"
    await event.answer(pin, cache_time=0, alert=True)


@callback(data="inlone", owner=True)
async def _(e):
    button = [
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
                "Search on XDA",
                query="xda telegram",
                same_peer=True,
            ),
        ],
        [
            Button.switch_inline(
                "WʜɪSᴘᴇʀ",
                query="wspr @username Hello🎉",
                same_peer=True,
            ),
            Button.switch_inline(
                "YᴏᴜTᴜʙᴇ Dᴏᴡɴʟᴏᴀᴅᴇʀ",
                query="yt Ed Sheeran Perfect",
                same_peer=True,
            ),
        ],
        [
            Button.switch_inline(
                "Piston Eval",
                query="run javascript console.log('Hello Ultroid')",
                same_peer=True,
            ),
            Button.switch_inline(
                "OʀᴀɴɢᴇFᴏx🦊",
                query="ofox beryllium",
                same_peer=True,
            ),
        ],
        [
            Button.inline(
                "« Bᴀᴄᴋ",
                data="open",
            ),
        ],
    ]
    await e.edit(buttons=button, link_preview=False)


@callback(data="hrrrr", owner=True)
async def on_plug_in_callback_query_handler(event):
    xhelps = helps.format(OWNER_NAME, len(HELP["Official"]))
    buttons = page_num(0, HELP["Official"].keys(), "helpme", "def")
    await event.edit(f"{xhelps}", buttons=buttons, link_preview=False)


@callback(data="frrr", owner=True)
async def addon(event):
    if HELP.get("Addons"):
        halp = zhelps.format(OWNER_NAME, len(HELP["Addons"]))
        buttons = page_num(0, HELP["Addons"].keys(), "addon", "add")
        await event.edit(halp, buttons=buttons, link_preview=False)
    else:
        await event.answer(
            f"• Tʏᴘᴇ {HNDLR}setredis ADDONS True\n Tᴏ ɢᴇᴛ ᴀᴅᴅᴏɴs ᴘʟᴜɢɪɴs",
            cache_time=0,
            alert=True,
        )


@callback(
    data=re.compile(
        rb"helpme_next\((.+?)\)",
    ),
    owner=True,
)
async def on_plug_in_callback_query_handler(event):
    current_page_number = int(event.data_match.group(1).decode("UTF-8"))
    buttons = page_num(
        current_page_number + 1, HELP["Official"].keys(), "helpme", "def"
    )
    await event.edit(buttons=buttons, link_preview=False)


@callback(
    data=re.compile(
        rb"helpme_prev\((.+?)\)",
    ),
    owner=True,
)
async def on_plug_in_callback_query_handler(event):
    current_page_number = int(event.data_match.group(1).decode("UTF-8"))
    buttons = page_num(
        current_page_number - 1, list(HELP["Official"].keys()), "helpme", "def"
    )
    await event.edit(buttons=buttons, link_preview=False)


@callback(
    data=re.compile(
        rb"addon_next\((.+?)\)",
    ),
    owner=True,
)
async def on_plug_in_callback_query_handler(event):
    current_page_number = int(event.data_match.group(1).decode("UTF-8"))
    buttons = page_num(
        current_page_number + 1, list(HELP["Addons"].keys()), "addon", "add"
    )
    await event.edit(buttons=buttons, link_preview=False)


@callback(
    data=re.compile(
        rb"addon_prev\((.+?)\)",
    ),
    owner=True,
)
async def on_plug_in_callback_query_handler(event):
    current_page_number = int(event.data_match.group(1).decode("UTF-8"))
    buttons = page_num(
        current_page_number - 1, list(HELP["Addons"].keys()), "addon", "add"
    )
    await event.edit(buttons=buttons, link_preview=False)


@callback(data="back", owner=True)
async def backr(event):
    xhelps = helps.format(OWNER_NAME, len(HELP["Official"]))
    current_page_number = int(upage)
    buttons = page_num(
        current_page_number, list(HELP["Official"].keys()), "helpme", "def"
    )
    await event.edit(
        xhelps,
        file=INLINE_PIC,
        buttons=buttons,
        link_preview=False,
    )


@callback(data="buck", owner=True)
async def backr(event):
    xhelps = zhelps.format(OWNER_NAME, len(HELP["Addons"]))
    current_page_number = int(upage)
    buttons = page_num(current_page_number, list(HELP["Addons"].keys()), "addon", "add")
    await event.edit(
        xhelps,
        file=INLINE_PIC,
        buttons=buttons,
        link_preview=False,
    )


@callback(data="open", owner=True)
async def opner(event):
    z = []
    PLUGINS = HELP["Official"] if "Official" in HELP.keys() else []
    ADDONS = HELP["Addons"] if "Addons" in HELP.keys() else []
    for x in LIST.values():
        for y in x:
            z.append(y)
    await event.edit(
        get_string("inline_4").format(
            OWNER_NAME,
            len(PLUGINS),
            len(ADDONS),
            len(z),
        ),
        buttons=_main_help_menu,
        link_preview=False,
    )


@callback(data="close", owner=True)
async def on_plug_in_callback_query_handler(event):
    await event.edit(
        get_string("inline_5"),
        buttons=Button.inline("Oᴘᴇɴ Aɢᴀɪɴ", data="open"),
    )


@callback(
    data=re.compile(
        b"def_plugin_(.*)",
    ),
    owner=True,
)
async def on_plug_in_callback_query_handler(event):
    plugin_name = event.data_match.group(1).decode("UTF-8")
    help_string = f"Plugin Name - `{plugin_name}`\n"
    try:
        for i in HELP["Official"][plugin_name]:
            help_string += i
    except BaseException:
        pass
    if help_string == "":
        reply_pop_up_alert = f"{plugin_name} has no detailed help..."
    else:
        reply_pop_up_alert = help_string
    reply_pop_up_alert += "\n© @TeamUltroid"
    buttons = []
    if INLINE_PIC:
        buttons.append(
            [
                Button.inline(
                    "« Sᴇɴᴅ Pʟᴜɢɪɴ »",
                    data=f"sndplug_{(event.data).decode('UTF-8')}",
                )
            ]
        )
    buttons.append(
        [
            Button.inline("« Bᴀᴄᴋ", data="back"),
        ]
    )
    try:
        if str(event.query.user_id) in owner_and_sudos():
            await event.edit(
                reply_pop_up_alert,
                buttons=buttons,
            )
        else:
            reply_pop_up_alert = notmine
            await event.answer(reply_pop_up_alert, cache_time=0)
    except BaseException:
        await event.edit(get_string("inline_7").format(plugin_name), buttons=buttons)


@callback(
    data=re.compile(
        b"vc_plugin_(.*)",
    ),
    owner=True,
)
async def on_vc_plg_callback_query_handler(event):
    plugin_name = event.data_match.group(1).decode("UTF-8")
    help_string = f"Plugin Name - `{plugin_name}`\n"
    try:
        for i in HELP["VCBot"][plugin_name]:
            help_string += i
    except BaseException:
        pass
    if help_string == "**Commands Available:**\n\n":
        reply_pop_up_alert = f"{plugin_name} has no detailed help..."
    else:
        reply_pop_up_alert = help_string
    reply_pop_up_alert += "\n© @TeamUltroid"
    buttons = []
    if INLINE_PIC:
        buttons.append(
            [
                Button.inline(
                    "« Sᴇɴᴅ Pʟᴜɢɪɴ »",
                    data=f"sndplug_{(event.data).decode('UTF-8')}",
                )
            ]
        )
    buttons.append(
        [
            Button.inline("« Bᴀᴄᴋ", data="vc_helper"),
        ]
    )
    try:
        if str(event.query.user_id) in owner_and_sudos():
            await event.edit(
                reply_pop_up_alert,
                buttons=buttons,
            )
        else:
            reply_pop_up_alert = notmine
            await event.answer(reply_pop_up_alert, cache_time=0)
    except BaseException:
        halps = f"Do .help {plugin_name} to get the list of commands."
        await event.edit(halps, buttons=buttons)


@callback(
    data=re.compile(
        b"add_plugin_(.*)",
    ),
    owner=True,
)
async def on_plug_in_callback_query_handler(event):
    plugin_name = event.data_match.group(1).decode("UTF-8")
    help_string = ""
    try:
        for i in HELP["Addons"][plugin_name]:
            help_string += i
    except BaseException:
        try:
            for u in CMD_HELP[plugin_name]:
                help_string = get_string("help_11").format(plugin_name)
                help_string += str(CMD_HELP[plugin_name])
        except BaseException:
            try:
                if plugin_name in LIST:
                    help_string = get_string("help_11").format(plugin_name)
                    for d in LIST[plugin_name]:
                        help_string += HNDLR + d
                        help_string += "\n"
            except BaseException:
                pass
    if help_string == "":
        reply_pop_up_alert = f"{plugin_name} has no detailed help..."
    else:
        reply_pop_up_alert = help_string
    reply_pop_up_alert += "\n© @TeamUltroid"
    buttons = []
    if INLINE_PIC:
        buttons.append(
            [
                Button.inline(
                    "« Sᴇɴᴅ Pʟᴜɢɪɴ »",
                    data=f"sndplug_{(event.data).decode('UTF-8')}",
                )
            ]
        )
    buttons.append(
        [
            Button.inline("« Bᴀᴄᴋ", data="buck"),
        ]
    )
    try:
        if str(event.query.user_id) in owner_and_sudos():
            await event.edit(
                reply_pop_up_alert,
                buttons=buttons,
            )
        else:
            reply_pop_up_alert = notmine
            await event.answer(reply_pop_up_alert, cache_time=0)
    except BaseException:
        halps = get_string("inline_7").format(plugin_name)
        await event.edit(halps, buttons=buttons)


def page_num(page_number, loaded_plugins, prefix, type_):
    number_of_rows = 5
    number_of_cols = 2
    emoji = udB.get("EMOJI_IN_HELP")
    multi = emoji or "✘"
    global upage
    upage = page_number
    helpable_plugins = [p for p in loaded_plugins]
    helpable_plugins = sorted(helpable_plugins)
    modules = [
        Button.inline(
            "{} {} {}".format(
                multi,
                x,
                multi,
            ),
            data=f"{type_}_plugin_{x}",
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
                    "« Pʀᴇᴠɪᴏᴜs",
                    data=f"{prefix}_prev({modulo_page})",
                ),
                Button.inline("« Bᴀᴄᴋ »", data="open"),
                Button.inline(
                    "Nᴇxᴛ »",
                    data=f"{prefix}_next({modulo_page})",
                ),
            ),
        ]
    else:
        pairs = pairs[
            modulo_page * number_of_rows : number_of_rows * (modulo_page + 1)
        ] + [(Button.inline("« Bᴀᴄᴋ »", data="open"),)]
    return pairs


# --------------------------------------------------------------------------------- #

STUFF = {}


@in_pattern("stf(.*)", owner=True)
async def ibuild(e):
    n = e.pattern_match.group(1)
    builder = e.builder
    if not (n and n.isdigit()):
        return
    ok = STUFF.get(int(n))
    txt = ok.get("msg") or None
    pic = ok.get("media") or None
    btn = ok.get("button") or None
    if not (pic or txt):
        txt = "Hey!"
    if pic:
        try:
            include_media = True
            mime_type, _pic = None, None
            cont, results = None, None
            try:
                ext = str(pic).split(".")[-1].lower()
            except BaseException:
                ext = None
            if ext in ["img", "jpg", "png"]:
                _type = "photo"
                mime_type = "image/jpg"
            elif ext in ["mp4", "mkv", "gif"]:
                mime_type = "video/mp4"
                _type = "gif"
            else:
                try:
                    if "telethon.tl.types" in str(type(pic)):
                        _pic = pic
                    else:
                        _pic = resolve_bot_file_id(pic)
                except BaseException:
                    pass
                if _pic:
                    results = [
                        await builder.document(
                            _pic,
                            title="Ultroid Op",
                            text=txt,
                            description="@TheUltroid",
                            buttons=btn,
                            link_preview=False,
                        )
                    ]
                else:
                    _type = "article"
                    include_media = False
            if not results:
                if include_media:
                    cont = InputWebDocument(pic, 0, mime_type, [])
                results = [
                    await builder.article(
                        title="Ultroid Op",
                        type=_type,
                        text=txt,
                        description="@TeamUltroid",
                        include_media=include_media,
                        buttons=btn,
                        thumb=cont,
                        content=cont,
                        link_preview=False,
                    )
                ]
            return await e.answer(results)
        except Exception as er:
            LOGS.exception(er)
    result = [
        await builder.article("Ultroid Op", text=txt, link_preview=False, buttons=btn)
    ]
    await e.answer(result)


async def something(e, msg, media, button, reply=True, chat=None):
    if e.client._bot:
        return await e.reply(msg, file=media, buttons=button)
    num = len(STUFF) + 1
    STUFF.update({num: {"msg": msg, "media": media, "button": button}})
    try:
        res = await e.client.inline_query(asst.me.username, f"stf{num}")
        return await res[0].click(
            chat or e.chat_id,
            reply_to=bool(isinstance(e, Message) and reply),
            hide_via=True,
            silent=True,
        )

    except Exception as er:
        LOGS.info(er)
