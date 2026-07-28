# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
• `{i}akinator` | `/akinator`
    Start akinator game from Userbot/Assistant

• `/startgame`
    Open Portal for Games
"""

import asyncio
import operator
import re
import uuid
from html import unescape
from logging import getLogger
from random import choice, shuffle

from akipy.async_akipy import Akinator
from telethon.errors import ChatSendStickersForbiddenError
from telethon.errors.rpcerrorlist import BotMethodInvalidError
from telethon.events import Raw
from telethon.tl.types import (
    InputMediaPoll,
    InputWebDocument,
    Poll,
    PollAnswer,
    TextWithEntities,
    UpdateMessagePollVote,
)

from pyUltroid._misc._decorators import ultroid_cmd
from pyUltroid.fns.helper import inline_mention
from pyUltroid.fns.tools import async_searcher

from . import *

games = {}
aki_photo = "https://graph.org/file/3cc8825c029fd0cab9edc.jpg"
GIMAGE = "https://graph.org/file/1c51015bae5205a65fd69.jpg"

akipyLOGS = getLogger("akipy")

TR_BTS = {}
RAW_DIFI_KEYS = ["Easy", "Medium", "Hard"]
TRIVIA_CHATS = {}
POLLS = {}
CONGO_STICKER = [
    "CAADAgADSgIAAladvQrJasZoYBh68AI",
    "CAADAgADXhIAAuyZKUl879mlR_dkOwI",
    "CAADAgADpQAD9wLID-xfZCDwOI5LAg",
    "CAADAgADjAADECECEFZM-SrKO9GgAg",
    "CAADAgADSwIAAj-VzArAzNCDiGWAHAI",
    "CAADAgADhQADwZxgDIuMHR9IU10iAg",
    "CAADAgADiwMAAsSraAuoe2BwYu1sdQI",
]


@ultroid_cmd(pattern="akinator")
async def akina(e):
    sta = Akinator()
    games[e.chat_id] = {e.id: sta}
    LOGS.info(f"Game started for chat {e.chat_id} with ID {e.id}.")
    try:
        m = await e.client.inline_query(asst.me.username, f"aki_{e.chat_id}_{e.id}")
        await m[0].click(e.chat_id)
        akipyLOGS.info(f"Clicked inline result for chat {e.chat_id}")
    except BotMethodInvalidError as err:
        akipyLOGS.error(f"BotMethodInvalidError: {err}")
        await asst.send_file(
            e.chat_id,
            aki_photo,
            buttons=Button.inline(get_string("aki_2"), data=f"aki_{e.chat_id}_{e.id}"),
        )
    except Exception as er:
        akipyLOGS.error(f"Unexpected error: {er}")
        return await e.eor(f"ERROR : {er}")
    if e.out:
        await e.delete()


@asst_cmd(pattern="akinator", owner=True)
async def _akokk(e):
    await akina(e)


@callback(re.compile("aki_(.*)"), owner=True)
async def doai(e):
    adt = e.pattern_match.group(1).strip().decode("utf-8")
    dt = adt.split("_")
    ch = int(dt[0])
    mid = int(dt[1])
    await e.edit(get_string("com_1"))
    try:
        await games[ch][mid].start_game(child_mode=False)
        bts = [
            [Button.inline(o, f"aka_{adt}_{o}") for o in ["Yes", "No", "Idk"]],
            [Button.inline(o, f"aka_{adt}_{o}") for o in ["Probably", "Probably Not"]],
        ]
        await e.edit(f"❓ **Qᴜᴇsᴛɪᴏɴ:** {games[ch][mid].question}", buttons=bts)
    except KeyError:
        return await e.answer(get_string("aki_1"), alert=True)


@callback(re.compile("aka_(.*)"), owner=True)
async def okah(e):
    try:
        mk = e.pattern_match.group(1).decode("utf-8").split("_")

        if len(mk) < 3:
            akipyLOGS.error("Pattern match did not return enough parts.")
            return await e.answer("Invalid data received.", alert=True)

        ch = int(mk[0])
        mid = int(mk[1])
        ans = mk[2]

        gm = games[ch][mid]
        await gm.answer(ans)

        if gm.name_proposition and gm.description_proposition:
            gm.win = True
            text = (
                "🔮 **Aᴋɪɴᴀᴛᴏʀ's Gᴜᴇss:**\n\n"
                f"🎯 **Nᴀᴍᴇ:** `{gm.name_proposition}`\n"
                f"📝 **Dᴇsᴄʀɪᴘᴛɪᴏɴ:** `{gm.description_proposition}`"
            )
            await e.edit(text, file=gm.photo)
        else:
            buttons = [
                [Button.inline(o, f"aka_{ch}_{mid}_{o}") for o in ["Yes", "No", "Idk"]],
                [Button.inline(o, f"aka_{ch}_{mid}_{o}") for o in ["Probably", "Probably Not"]],
            ]
            await e.edit(f"❓ **Qᴜᴇsᴛɪᴏɴ:** {gm.question}", buttons=buttons)

    except KeyError:
        await e.answer(get_string("aki_3"))
    except Exception as ex:
        akipyLOGS.error(f"An unexpected error occurred: {ex}")


@in_pattern(re.compile("aki_?(.*)"), owner=True)
async def eiagx(e):
    bts = Button.inline(get_string("aki_2"), data=e.text)
    ci = InputWebDocument(aki_photo, 0, "image/jpeg", [])
    ans = [
        await e.builder.article(
            "Akinator",
            type="photo",
            content=ci,
            text="Akinator",
            thumb=ci,
            buttons=bts,
            include_media=True,
        )
    ]
    await e.answer(ans)


@asst_cmd(pattern="startgame", owner=True)
async def magic(event):
    buttons = [
        [Button.inline("🎲 Tʀɪᴠɪᴀ Qᴜɪᴢ", "trzia")],
        [Button.inline("❌ Cᴀɴᴄᴇʟ", "delit")],
    ]
    await event.reply(
        get_string("games_1"),
        file=GIMAGE,
        buttons=buttons,
    )


@callback("delit", owner=True)
async def delete_it(event):
    await event.delete()


@callback(re.compile("ctdown(.*)"), owner=True)
async def ct_spam(e):
    n = e.data_match.group(1).decode("utf-8")
    await e.answer(f"⏳ Please wait {n} seconds...", alert=True)


@callback(re.compile("trzia(.*)"), owner=True)
async def choose_cata(event):
    match = event.data_match.group(1).decode("utf-8")
    if not match:
        if TR_BTS.get("category"):
            buttons = TR_BTS["category"]
        else:
            req = (
                await async_searcher(
                    "https://opentdb.com/api_category.php", re_json=True
                )
            )["trivia_categories"]
            btt = []
            for i in req:
                name = i["name"]
                if ":" in name:
                    name = name.split(":")[1]
                btt.append(Button.inline(name, f"trziad_{i['id']}"))
            buttons = list(zip(btt[::2], btt[1::2]))
            if len(btt) % 2 == 1:
                buttons.append((btt[-1],))
            buttons.append([Button.inline("❌ Cᴀɴᴄᴇʟ", "delit")])
            TR_BTS.update({"category": buttons})
        text = get_string("games_2")
    elif match[0] == "d":
        cat = match[1:]
        buttons = [
            [
                Button.inline(RAW_DIFI_KEYS[idx], f"trziac{cat}_{RAW_DIFI_KEYS[idx]}")
                for idx in range(len(RAW_DIFI_KEYS))
            ]
        ]
        buttons.append(get_back_button("trzia"))
        text = get_string("games_3")
    elif match[0] == "c":
        m = match[1:]
        buttons = [[Button.inline(f"🔢 {i}", f"trziat{m}_{i}") for i in range(10, 70, 20)]]
        text = get_string("games_4")
    elif match[0] == "t":
        m_ = match[1:]
        buttons = [
            [Button.inline(f"⏱ {i}s", f"trzias{m_}_{i}") for i in [10, 30, 60, 120]]
        ]
        text = get_string("games_5")
    elif match[0] == "s":
        chat = event.chat_id
        cat, le, nu, in_ = match[2:].split("_")
        msg = await event.edit(get_string("games_6").format(le, nu))
        for i in reversed(range(5)):
            msg = await msg.edit(buttons=Button.inline(f"⏰ {i}s", f"ctdown{i}"))
            await asyncio.sleep(1)
        await msg.edit(
            msg.text + "\n\n• Send `/cancel` to stop the Quiz...", buttons=None
        )
        qsss = await async_searcher(
            f"https://opentdb.com/api.php?amount={nu}&category={cat}&difficulty={le.lower()}",
            re_json=True,
        )
        qs = qsss.get("results", [])
        if not qs:
            await event.respond("❌ **Sorry, no questions found for the given criteria.**")
            await event.delete()
            return
        TRIVIA_CHATS.update({chat: {}})
        for copper, q in enumerate(qs):
            if TRIVIA_CHATS[chat].get("cancel") is not None:
                break
            ansi = str(uuid.uuid1()).split("-")[0].encode()
            opts = [PollAnswer(TextWithEntities(unescape(q["correct_answer"]), entities=[]), ansi)]
            for a in q["incorrect_answers"]:
                opts.append(
                    PollAnswer(TextWithEntities(unescape(a), entities=[]), str(uuid.uuid1()).split("-")[0].encode())
                )
            shuffle(opts)
            poll = InputMediaPoll(
                Poll(
                    0,
                    TextWithEntities(
                        f"[{copper + 1}].  " + unescape(q["question"]),
                        entities=[]
                    ),
                    answers=opts,
                    public_voters=True,
                    quiz=True,
                    close_period=int(in_),
                ),
                correct_answers=[ansi],
                solution="Join @TeamUltroid",
                solution_entities=[],
            )
            m_ = await event.client.send_message(chat, file=poll)
            POLLS.update({m_.poll.poll.id: {"chat": m_.chat_id, "answer": ansi}})
            await asyncio.sleep(int(in_))
        if not TRIVIA_CHATS[chat]:
            await event.respond(
                "😔 **No one scored any points in the quiz!**\nBetter luck next time!"
            )
        else:
            try:
                await event.respond(file=choice(CONGO_STICKER))
            except ChatSendStickersForbiddenError:
                pass
            LBD = "🏆 **Sᴄᴏʀᴇʙᴏᴀʀᴅ ᴏғ ᴛʜᴇ Qᴜɪᴢ**\n\n"
            TRC = TRIVIA_CHATS[chat]
            if "cancel" in TRC.keys():
                del TRC["cancel"]
            for userid, user_score in dict(
                sorted(TRC.items(), key=operator.itemgetter(1), reverse=True)
            ).items():
                user = inline_mention(await event.client.get_entity(userid))
                LBD += f"• {user} ➔ `{user_score}` pts\n"
            await event.respond(LBD)
        del TRIVIA_CHATS[chat]
        list_ = list(POLLS.copy().keys())
        for key in list_:
            if POLLS[key]["chat"] == chat:
                del POLLS[key]
        return
    await event.edit(text, buttons=buttons)


@asst.on(
    Raw(UpdateMessagePollVote, func=lambda x: TRIVIA_CHATS and POLLS.get(x.poll_id))
)
async def pollish(eve: UpdateMessagePollVote):
    if POLLS.get(eve.poll_id)["chat"] not in TRIVIA_CHATS.keys():
        return
    if not eve.options:
        chat = POLLS.get(eve.poll_id)["chat"]
        user = eve.peer.user_id
        if not TRIVIA_CHATS.get(chat, {}).get(user):
            TRIVIA_CHATS[chat][user] = 1
        else:
            TRIVIA_CHATS[chat][user] += 1
        return
    if POLLS[eve.poll_id]["answer"] != eve.options[0]:
        return
    chat = POLLS.get(eve.poll_id)["chat"]
    user = eve.peer.user_id
    if not TRIVIA_CHATS.get(chat, {}).get(user):
        TRIVIA_CHATS[chat][user] = 1
    else:
        TRIVIA_CHATS[chat][user] += 1


@asst_cmd("cancel", owner=True, func=lambda x: TRIVIA_CHATS.get(x.chat_id))
async def cancelish(event):
    chat = TRIVIA_CHATS.get(event.chat_id)
    chat.update({"cancel": True})
    await event.respond("❌ **Tʀɪᴠɪᴀ Qᴜɪᴢ Cᴀɴᴄᴇʟʟᴇᴅ!**")
