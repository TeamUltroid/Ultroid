import re
from contextlib import suppress
from inspect import getmembers

from telethon import Button

from core.decorators._assistant import callback, in_pattern
from core.loader import PLUGINS
from core.remote import rm
from database._core import CMD_HELP, LIST, InlinePlugin, InlinePaths

from .. import HNDLR, LOGS, asst, get_string, inline_pic, udB, ultroid_bot, ultroid_cmd

_cache = {}


def split_list(List, index):
    new_ = []
    while List:
        new_.extend([List[:index]])
        List = List[index:]
    return new_


def get_help_buttons():
    row_1 = [Button.inline(get_string("help_4"), data="uh_basic_")]
    if filter_modules(
        "addons"
    ):  # (udB.get_config("ADDONS") or udB.get_key("LOAD_ALL"))
        row_1.append(Button.inline(get_string("help_5"), data="uh_addons_"))
    row_2 = []
    if udB.get_config("VCBOT"):
        row_2.append(Button.inline(get_string("help_6"), data="uh_vcbot_"))
    if InlinePlugin:
        row_2.append(Button.inline(get_string("help_7"), data="inlone"))
    if all(len(row) == 1 for row in [row_1, row_2]):
        row_1.append(row_2[0])
        row_2.clear()
    Markup = [row_1]
    if len(row_2) > 1:
        Markup.append(row_2)
    if udB.get_key("MANAGER"):
        button = Button.inline("Manager", "mngbtn")
        if len(row_1) == 1:
            row_1.append(button)
        elif len(row_2) == 1:
            row_2.insert(0, button)
        else:
            Markup.append([button])
    settingButton = Button.url(
        get_string("help_9"),
        url=f"https://t.me/{asst.me.username}?start=set",
    )
    if len(row_2) == 1:
        row_2.append(settingButton)
    else:
        Markup.append([settingButton])
    Markup.append(
        [Button.inline(get_string("help_10"), data="close")],
    )
    if row_2 and row_2 not in Markup:
        Markup.insert(1, row_2)
    return Markup


def _sort(type, modl):
    spli = modl.split(".")
    if type in spli and not spli[-1].startswith("_") and modl not in InlinePaths:
        return modl.split(".")[-1]


def filter_modules(type):
    """Get names of loaded plugins"""
    return sorted(
        list(filter(lambda e: e, map(lambda modl: _sort(type, modl), PLUGINS)))
    )  # type:ignore


def _get_module(name, type):
    check = [type] if type else ["basic", "addons"]
    for path in check:
        with suppress(KeyError):
            return PLUGINS[f"modules.{path}.{name}"]


def get_doc_from_module(name, type=""):
    if mod := _get_module(name, type):
        if not mod.__doc__:
            return get_from_funcs(mod, name)
        msg = f"Commands available in `{name}`-\n"
        msg += mod.__doc__.format(i=HNDLR)
        msg += "\n ©️ @TeamUltroid"
        return msg


def get_from_funcs(mod, name):
    handlers = list(map(lambda d: d[0], ultroid_bot.list_event_handlers()))
    funcs = list(
        filter(
            lambda d: (
                d[0].endswith(("_func", "_cmd")) and d[1] in handlers and d[1].__doc__
            ),
            getmembers(mod),
        )
    )
    if not funcs:
        return False
    msg = f"Command available in `{name}`-\n"
    for cmd in funcs:
        msg += f"\n• {cmd[1].__doc__.format(HNDLR)}\n"
    msg += "\n ©️ @TeamUltroid"
    return msg


def get_doc(module, type=""):
    msg = get_doc_from_module(module, type)
    if msg:
        return msg
    _get_info = rm.get_info(module)
    if _get_info and (cmds := _get_info.get("cmds")):
        msg = f"✘ Commands Available in `{module}` -"
        for cmd in cmds:
            msg += f"\n\n• `{HNDLR}{cmd}`\n {cmds[cmd]}"
    elif help := CMD_HELP.get(module):
        msg = f"Plugin Name: {module}\n\n"
        msg += help.format(i=HNDLR)
    elif help := LIST.get(module):
        msg = f"Plugin Name: {module}\n\n"
        for cmd in help:
            msg += f"- \n{HNDLR}{cmd}\n"
    if msg:
        msg += "\n ©️ @TeamUltroid"
    return msg


@ultroid_cmd("help($| (.*))")
async def help_cmd(event):
    module = event.pattern_match.group(1).strip()
    if not module:
        if event.client._bot:
            return await event.reply(
                get_string("inline_4").format(ultroid_bot.full_name, len(PLUGINS)),
                file=inline_pic(),
                buttons=get_help_buttons(),
                link_preview=False,
            )
        await event.delete()
        result = await event.client.inline_query(asst.me.username, "ultd")
        await result[0].click(event.chat_id)
        return
    if msg := get_doc(module):
        return await event.eor(msg)
    if not LIST.get(module):
        return await event.eor(f"`{module}` is not a valid plugin.")
    await event.eor(f"`{module} has no default help.`")


@in_pattern("ultd", owner=True)
async def inline_handler(event):
    text = get_string("inline_4").format(ultroid_bot.full_name, len(PLUGINS))
    if inline_pic():
        result = await event.builder.photo(
            file=inline_pic(),
            link_preview=False,
            text=text,
            buttons=get_help_buttons(),
        )
    else:
        result = await event.builder.article(
            title="Ultroid Help Menu", text=text, buttons=get_help_buttons()
        )
    await event.answer([result], private=True, cache_time=300, gallery=True)


@callback(re.compile("uh_(.*)"), owner=True)
async def help_func(ult):
    key, count = ult.data_match.group(1).decode("utf-8").split("_")
    plugs = filter_modules(key)
    if key == "vcbot" and not plugs:
        return await ult.answer(get_string("help_12"), alert=True)
    elif key == "addons" and not plugs:
        return await ult.answer(get_string("help_13").format(HNDLR), alert=True)
    if "|" in count:
        _, count = count.split("|")
    count = int(count) if count else 0
    _strings = {
        "vcbot": "inline_6",
        "addons": "inline_3" if udB.get_key("ADDONS") else "inline_2",
        "basic": "inline_1",
    }
    text = get_string(_strings.get(key, "")).format(ultroid_bot.full_name, len(plugs))
    await ult.edit(text, buttons=page_num(count, key), link_preview=False)


@callback(data="open", owner=True)
async def opner(event):
    await event.edit(
        get_string("inline_4").format(
            ultroid_bot.full_name,
            len(PLUGINS),
        ),
        buttons=get_help_buttons(),
        link_preview=False,
    )


@callback(data="close", owner=True)
async def on_plug_in_callback_query_handler(event):
    await event.edit(
        get_string("inline_5"),
        buttons=Button.inline("Oᴘᴇɴ Aɢᴀɪɴ", data="open"),
    )


@callback(data="inlone", owner=True)
async def _(e):
    if not InlinePlugin:
        return await e.answer("You dont have Inline Plugins loaded!", alert=True)
    _InButtons = [
        Button.switch_inline(key, query=InlinePlugin[key], same_peer=True)
        for key in InlinePlugin
    ]
    InButtons = split_list(_InButtons, 2)

    button = InButtons.copy()
    button.append(
        [
            Button.inline("« Bᴀᴄᴋ", data="open"),
        ],
    )
    await e.edit(buttons=button, link_preview=False)


def _get_buttons(key, index):
    rows = udB.get_key("HELP_ROWS") or 5
    cols = udB.get_key("HELP_COLUMNS") or 2
    emoji = udB.get_key("EMOJI_IN_HELP") or "✘"
    loaded = filter_modules(key)
    cindex = 0
    NList = []
    tl = rows * cols
    for plugs in split_list(loaded, tl):
        MList = []
        for ps in split_list(plugs, rows):
            for p in ps:
                MList.append(
                    Button.inline(
                        f"{emoji} {p} {emoji}", data=f"uplugin_{key}_{p}|{cindex}"
                    )
                )
        NList.append(split_list(MList, cols))
        cindex += 1
    if _cache.get("help") is None:
        _cache["help"] = {}
    _cache["help"][key] = NList
    return NList


def page_num(index, key):
    fl_ = _cache.get("help", {}).get(key)
    if not fl_:
        fl_ = _get_buttons(key, index)
    try:
        new_ = fl_[index].copy()
    except IndexError:
        new_ = fl_[0].copy() if fl_ else []
        index = 0
    if index == 0 and len(fl_) == 1:
        new_.append([Button.inline("« Bᴀᴄᴋ »", data="open")])
    else:
        new_.append(
            [
                Button.inline(
                    "« Pʀᴇᴠɪᴏᴜs",
                    data=f"uh_{key}_{index-1}",
                ),
                Button.inline("« Bᴀᴄᴋ »", data="open"),
                Button.inline(
                    "Nᴇxᴛ »",
                    data=f"uh_{key}_{index+1}",
                ),
            ]
        )

    return new_


@callback(re.compile("uplugin_(.*)"), owner=True)
async def uptd_plugin(event):
    key, file = event.data_match.group(1).decode("utf-8").split("_")
    index = None
    if "|" in file:
        file, index = file.split("|")
    help_ = get_doc(file, key)
    if not help_:
        help_ = f"{file} has no Detailed Help!"
        help_ += "\n© @TeamUltroid"
    buttons = []
    if inline_pic():
        data = f"sndplug_{key}_{file}"
        if index is not None:
            data += f"|{index}"
        buttons.append(
            [
                Button.inline(
                    "« Sᴇɴᴅ Pʟᴜɢɪɴ »",
                    data=data,
                )
            ]
        )
    data = f"uh_{key}_"
    if index is not None:
        data += f"|{index}"
    buttons.append(
        [
            Button.inline("« Bᴀᴄᴋ", data=data),
        ]
    )
    try:
        await event.edit(help_, buttons=buttons)
    except Exception as er:
        LOGS.exception(er)
        help = f"Do `{HNDLR}help {key}` to get list of commands."
        await event.edit(help, buttons=buttons)
