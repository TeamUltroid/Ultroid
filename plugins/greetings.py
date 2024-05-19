# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

---- Welcomes ----
• `{i}setwelcome <message/reply to message>`
    Set welcome message in the current chat.

• `{i}clearwelcome`
    Delete the welcome in the current chat.

• `{i}getwelcome`
    Get the welcome message in the current chat.

---- GoodByes ----
• `{i}setgoodbye <message/reply to message>`
    Set goodbye message in the current chat.

• `{i}cleargoodbye`
    Delete the goodbye in the current chat.

• `{i}getgoodbye`
    Get the goodbye message in the current chat.

• `{i}thankmembers on/off`
    Send a thank you sticker on hitting a members count of 100*x in your groups.
"""
import os, asyncio

from telegraph import upload_file as uf
from telethon.utils import pack_bot_file_id
from utilities.tools import create_tl_btn, format_btn, get_msg_button

from telethon import events
from ..basic._inline import something
from telethon.events import ChatAction
from . import (
    HNDLR,
    asst,
    eor,
    get_string,
    mediainfo,
    udB,
    ultroid_cmd,
    inline_mention,
    ultroid_bot,
)
from telethon.utils import get_display_name

Note = "\n\nNote: `{mention}`, `{group}`, `{count}`, `{name}`, `{fullname}`, `{username}`, `{userid}` can be used as formatting parameters.\n\n"


@ultroid_cmd(pattern="setwelcome", groups_only=True)
async def setwel(event):
    x = await event.eor(get_string("com_1"))
    r = await event.get_reply_message()
    btn = format_btn(r.buttons) if (r and r.buttons) else None
    try:
        text = event.text.split(maxsplit=1)[1]
    except IndexError:
        text = r.text if r else None
    client = "asst" if event.client.me.bot else "user"
    if r and r.media:
        wut = mediainfo(r.media)
        if wut.startswith(("pic", "gif")):
            dl = await r.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = f"https://graph.org{variable[0]}"
        elif wut == "video":
            if r.media.document.size > 8 * 1000 * 1000:
                return await eor(x, get_string("com_4"), time=5)
            dl = await r.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = f"https://graph.org{variable[0]}"
        elif wut == "web":
            m = None
        else:
            m = pack_bot_file_id(r.media)
        txt = r.text
        if txt and not btn:
            txt, btn = get_msg_button(r.text)
        add_welcome(event.chat_id, txt, m, btn, client)
        await eor(x, get_string("grt_1"))
    elif text:
        if not btn:
            txt, btn = get_msg_button(text)
        add_welcome(event.chat_id, txt, None, btn, client)
        return await eor(x, get_string("grt_1"))
    else:
        await eor(x, get_string("grt_3"), time=5)


@ultroid_cmd(pattern="clearwelcome$", groups_only=True)
async def clearwel(event):
    if not get_welcome(event.chat_id):
        return await event.eor(get_string("grt_4"), time=5)
    delete_welcome(event.chat_id)
    await event.eor(get_string("grt_5"), time=5)


@ultroid_cmd(pattern="getwelcome$", groups_only=True)
async def listwel(event):
    wel = get_welcome(event.chat_id)
    if not wel:
        return await event.eor(get_string("grt_4"), time=5)
    msgg, med = wel["welcome"], wel["media"]
    if wel.get("button"):
        btn = create_tl_btn(wel["button"])
        return await something(event, msgg, med, btn)
    await event.reply(f"**Welcome Note in this chat**\n\n`{msgg}`", file=med)
    await event.delete()


@ultroid_cmd(pattern="setgoodbye", groups_only=True)
async def setgb(event):
    x = await event.eor(get_string("com_1"))
    r = await event.get_reply_message()
    btn = format_btn(r.buttons) if (r and r.buttons) else None
    try:
        text = event.text.split(maxsplit=1)[1]
    except IndexError:
        text = r.text if r else None
    client = "asst" if event.client.me.bot else "user"
    if r and r.media:
        wut = mediainfo(r.media)
        if wut.startswith(("pic", "gif")):
            dl = await r.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = f"https://graph.org{variable[0]}"
        elif wut == "video":
            if r.media.document.size > 8 * 1000 * 1000:
                return await eor(x, get_string("com_4"), time=5)
            dl = await r.download_media()
            variable = uf(dl)
            os.remove(dl)
            m = f"https://graph.org{variable[0]}"
        elif wut == "web":
            m = None
        else:
            m = pack_bot_file_id(r.media)
        txt = r.text
        if txt and not btn:
            txt, btn = get_msg_button(txt)
        add_goodbye(event.chat_id, txt, m, btn, client)
        await eor(x, "`Goodbye note saved`")
    elif text:
        if not btn:
            txt, btn = get_msg_button(text)
        add_goodbye(event.chat_id, txt, None, btn, client)
        await eor(x, "`Goodbye note saved`")
    else:
        await eor(x, get_string("grt_7"), time=5)


@ultroid_cmd(pattern="cleargoodbye$", groups_only=True)
async def clearwgb(event):
    if not get_goodbye(event.chat_id):
        return await event.eor(get_string("grt_6"), time=5)
    delete_goodbye(event.chat_id)
    await event.eor("`Goodbye Note Deleted`", time=5)


@ultroid_cmd(pattern="getgoodbye$", groups_only=True)
async def listgd(event):
    wel = get_goodbye(event.chat_id)
    if not wel:
        return await event.eor(get_string("grt_6"), time=5)
    msgg = wel["goodbye"]
    med = wel["media"]
    if wel.get("button"):
        btn = create_tl_btn(wel["button"])
        return await something(event, msgg, med, btn)
    await event.reply(f"**Goodbye Note in this chat**\n\n`{msgg}`", file=med)
    await event.delete()


@ultroid_cmd(pattern="thankmembers (on|off)", groups_only=True)
async def thank_set(event):
    type_ = event.pattern_match.group(1).strip()
    if not type_ or type_ == "":
        await eor(
            event,
            f"**Current Chat Settings:**\n**Thanking Members:** `{must_thank(event.chat_id)}`\n\nUse `{HNDLR}thankmembers on` or `{HNDLR}thankmembers off` to toggle current settings!",
        )
        return
    chat = event.chat_id
    if type_.lower() == "on":
        add_thanks(chat, "asst" if event.client.me.bot else "user")
    elif type_.lower() == "off":
        remove_thanks(chat)
    await eor(
        event,
        f"**Done! Thank you members has been turned** `{type_.lower()}` **for this chat**!",
    )


def add_welcome(chat, msg, media, button, client="user"):
    ok = udB.get_key("WELCOME") or {}
    ok.update(
        {
            chat: {
                "welcome": msg,
                "media": media,
                "button": button,
                "client": client or "user",
            }
        }
    )
    return udB.set_key("WELCOME", ok)


def get_welcome(chat):
    ok = udB.get_key("WELCOME") or {}
    return ok.get(chat)


def get_goodbye(chat):
    ok = udB.get_key("WELCOME") or {}
    return ok.get(chat)


def delete_welcome(chat):
    ok = udB.get_key("WELCOME") or {}
    if chat in ok:
        ok.pop(chat)
        return udB.set_key("WELCOME", ok)


def add_goodbye(chat, msg, media, button, client="user"):
    ok = udB.get_key("GOODBYE")
    ok.update(
        {chat: {"goodbye": msg, "media": media, "button": button, "client": client}}
    )
    return udB.set_key("GOODBYE", ok)


def delete_goodbye(chat):
    ok = udB.get_key("GOODBYE") or {}
    if ok.get(chat):
        ok.pop(chat)
        return udB.set_key("GOODBYE", ok)


def add_thanks(chat, client="user"):
    x = udB.get_key("THANK_MEMBERS")
    x.update({chat: client or "user"})
    return udB.set_key("THANK_MEMBERS", x)


def remove_thanks(chat):
    x = udB.get_key("THANK_MEMBERS")
    if chat in x:
        x.pop(chat)
        return udB.set_key("THANK_MEMBERS", x)


def must_thank(chat):
    x = udB.get_key("THANK_MEMBERS")
    return x.get(chat)


async def handle_thank_member(ult):
        chat_count = (await ult.client.get_participants(ult.chat_id, limit=0)).total
        if chat_count % 100 == 0:
            stickers = [
                "CAADAQADeAIAAm_BZBQh8owdViocCAI",
                "CAADAQADegIAAm_BZBQ6j8GpKtnrSgI",
                "CAADAQADfAIAAm_BZBQpqC84n9JNXgI",
                "CAADAQADfgIAAm_BZBSxLmTyuHvlzgI",
                "CAADAQADgAIAAm_BZBQ3TZaueMkS-gI",
                "CAADAQADggIAAm_BZBTPcbJMorVVsQI",
                "CAADAQADhAIAAm_BZBR3lnMZRdsYxAI",
                "CAADAQADhgIAAm_BZBQGQRx4iaM4pQI",
                "CAADAQADiAIAAm_BZBRRF-cjJi_QywI",
                "CAADAQADigIAAm_BZBQQJwfzkqLM0wI",
                "CAADAQADjAIAAm_BZBQSl5GSAT0viwI",
                "CAADAQADjgIAAm_BZBQ2xU688gfHhQI",
                "CAADAQADkAIAAm_BZBRGuPNgVvkoHQI",
                "CAADAQADpgIAAm_BZBQAAZr0SJ5EKtQC",
                "CAADAQADkgIAAm_BZBTvuxuayqvjhgI",
                "CAADAQADlAIAAm_BZBSMZdWN2Yew1AI",
                "CAADAQADlQIAAm_BZBRXyadiwWGNkwI",
                "CAADAQADmAIAAm_BZBQDoB15A1jS1AI",
                "CAADAQADmgIAAm_BZBTnOLQ8_d72vgI",
                "CAADAQADmwIAAm_BZBTve1kgdG0Y5gI",
                "CAADAQADnAIAAm_BZBQUMyFiylJSqQI",
                "CAADAQADnQIAAm_BZBSMAe2V4pwhNgI",
                "CAADAQADngIAAm_BZBQ06D92QL_vywI",
                "CAADAQADnwIAAm_BZBRw7UAbr6vtEgI",
                "CAADAQADoAIAAm_BZBRkv9DnGPXh_wI",
                "CAADAQADoQIAAm_BZBQwI2NgQdyKlwI",
                "CAADAQADogIAAm_BZBRPHJF3XChVLgI",
                "CAADAQADowIAAm_BZBThpas7rZD6DAI",
                "CAADAQADpAIAAm_BZBQcC2DpZcCw1wI",
                "CAADAQADpQIAAm_BZBQKruTcEU4ntwI",
            ]

            stik_id = chat_count / 100 - 1
            sticker = stickers[stik_id]
            await ult.respond(file=sticker)

async def handleChatAction(ult):
    currentClient = "asst" if ult.client.me.bot else "user"

    # thank members
    if must_thank(ult.chat_id) == currentClient:
        await handle_thank_member(ult)

    if ult.user_joined or ult.added_by:
        user = await ult.get_user()
        chat = await ult.get_chat()

        # greetings
        if (wel := get_welcome(ult.chat_id)) and (wel["client"] == currentClient):
            title = chat.title or "this chat"
            count = (
                chat.participants_count
                or (await ult.client.get_participants(chat, limit=0)).total
            )
            mention = inline_mention(user)
            name = user.first_name
            fullname = get_display_name(user)
            uu = user.username
            username = f"@{uu}" if uu else mention
            msgg = wel["welcome"]
            med = wel["media"] or None
            userid = user.id
            msg = None
            if msgg:
                msg = msgg.format(
                    mention=mention,
                    group=title,
                    count=count,
                    name=name,
                    fullname=fullname,
                    username=username,
                    userid=userid,
                )
            if wel.get("button"):
                btn = create_tl_btn(wel["button"])
                await something(ult, msg, med, btn)
            elif msg:
                send = await ult.reply(
                    msg,
                    file=med,
                )
                await asyncio.sleep(150)
                await send.delete()
            else:
                await ult.reply(file=med)
    elif (ult.user_left or ult.user_kicked) and (wel := get_goodbye(ult.chat_id)) and (
        wel['client'] == currentClient
    ):
        user = await ult.get_user()
        chat = await ult.get_chat()
        title = chat.title or "this chat"
        count = (
            chat.participants_count
            or (await ult.client.get_participants(chat, limit=0)).total
        )
        mention = inline_mention(user)
        name = user.first_name
        fullname = get_display_name(user)
        uu = user.username
        username = f"@{uu}" if uu else mention
        msgg = wel["goodbye"]
        med = wel["media"]
        userid = user.id
        msg = None
        if msgg:
            msg = msgg.format(
                mention=mention,
                group=title,
                count=count,
                name=name,
                fullname=fullname,
                username=username,
                userid=userid,
            )
        if wel.get("button"):
            btn = create_tl_btn(wel["button"])
            await something(ult, msg, med, btn)
        elif msg:
            send = await ult.reply(
                msg,
                file=med,
            )
            await asyncio.sleep(150)
            await send.delete()
        else:
            await ult.reply(file=med)

ultroid_bot.add_handler(handleChatAction, ChatAction())
asst.add_handler(handleChatAction, ChatAction())
