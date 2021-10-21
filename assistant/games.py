# Ultroid - UserBot
# Copyright (C) 2020 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.


import asyncio
import re
import operator
import uuid
from html import unescape
from random import shuffle

from pyUltroid.functions.helper import inline_mention
from pyUltroid.functions.tools import async_searcher
from telethon.events import Raw
from telethon.tl.types import InputMediaPoll, Poll, PollAnswer, UpdateMessagePollVote

from . import *


@asst_cmd(pattern="startgame", owner=True)
async def magic(event):
    buttons = [
        [Button.inline("Trivia Quiz", "trzia")],
        [Button.inline("Cancel ❌", "delit")],
    ]
    await event.reply("Choose The Game 🎮", buttons=buttons)


TR_BTS = {}
DIFI_KEYS = ["Easy", "Medium", "Hard"]
TRIVIA_CHATS = {}
POLLS = {}


@callback(re.compile("ctdown(.*)"), owner=True)
async def ct_spam(e):
    n = e.data_match.group(1).decode("utf-8")
    await e.answer(f"Wait {n} seconds..", alert=True)


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
            buttons.append([Button.inline("Cancel ❌", "delit")])
            TR_BTS.update({"category": buttons})
        text = "Choose Category!"
    elif match[0] == "d":
        cat = match[1:]
        buttons = [[Button.inline(i, f"trziac{cat}_{i}") for i in DIFI_KEYS]]
        buttons.append(get_back_button("trzia"))
        text = "Choose Difficulty Level"
    elif match[0] == "c":
        m = match[1:]
        buttons = [[Button.inline(str(i), f"trzias{m}_{i}") for i in range(10, 70, 20)]]
        buttons.append(get_back_button("trzia" + match))
        text = "Choose Number of Questions.."
    elif match[0] == "s":
        chat = event.chat_id
        cat, le, nu = match[2:].split("_")
        msg = await event.edit(
            f"**• Starting Quiz in 5secs.** \n**• Level :** {le}\n**• Qs :** {nu}"
        )
        for i in reversed(range(5)):
            msg = await msg.edit(buttons=Button.inline(str(i), f"ctdown{i}"))
            await asyncio.sleep(1)
        await msg.edit(
            msg.text + "\n\n• Send /cancel to stop the Quiz...", buttons=None
        )
        qsss = await async_searcher(
            f"https://opentdb.com/api.php?amount={nu}&category={cat}&difficulty={le.lower()}",
            re_json=True,
        )
        qs = qsss["results"]
        if not qs:
            await event.respond("Sorry, No Question Found for the given limit..")
            await event.delete()
            return
        TRIVIA_CHATS.update({chat: {}})
        for copper, q in enumerate(qs):
            ansi = str(uuid.uuid1()).split("-")[0].encode()
            opts = [PollAnswer(unescape(q["correct_answer"]), ansi)]
            [
                opts.append(
                    PollAnswer(unescape(a), str(uuid.uuid1()).split("-")[0].encode())
                )
                for a in q["incorrect_answers"]
            ]
            shuffle(opts)
            poll = InputMediaPoll(
                Poll(
                    0,
                    f"{copper+1}. " + unescape(q["question"]),
                    answers=opts,
                    public_voters=True,
                    quiz=True,
                    close_period=30,
                ),
                correct_answers=[ansi],
                solution="Join @TeamUltroid",
                solution_entities=[],
            )
            m_ = await event.client.send_message(chat, file=poll)
            POLLS.update({m_.poll.poll.id: {"chat": m_.chat_id, "answer": ansi}})
            await asyncio.sleep(30)
        if not TRIVIA_CHATS[chat]:
            await event.respond(
                "No-One Got Any Score in the Quiz!\nBetter Luck Next Time!"
            )
        else:
            LBD = "🎯 Scoreboard of the last Quiz.\n\n"
            TRC = TRIVIA_CHATS[chat]
            ignore_ = []
            for userid, user_score in dict(sorted(TRC.items(), key=operator.itemgetter(1),reverse=True)).items():
                if userid not in ignore_:
                    user = inline_mention(await event.client.get_entity(userid))
                    LBD += f"• {user} - {user_score}\n"
                    ignore_.append(userid)
            await event.respond(LBD)
        del TRIVIA_CHATS[chat]
        for key in POLLS.keys():
            if key["chat"] == chat:
                del POLLS[key]
        return
    await event.edit(text, buttons=buttons)


@asst.on(
    Raw(UpdateMessagePollVote, func=lambda x: TRIVIA_CHATS and POLLS.get(x.poll_id))
)
async def pollish(eve):
    if not POLLS.get(eve.poll_id)["chat"] in TRIVIA_CHATS.keys():
        return
    if POLLS[eve.poll_id]["answer"] != eve.options[0]:
        return
    chat = POLLS.get(eve.poll_id)["chat"]
    user = eve.user_id
    if not TRIVIA_CHATS.get(chat, {}).get(user):
        TRIVIA_CHATS[chat][user] = 1
    else:
        TRIVIA_CHATS[chat][user] = TRIVIA_CHATS[chat][user] + 1
