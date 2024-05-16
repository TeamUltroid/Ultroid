import asyncio
import operator
import re
import uuid
from html import unescape
from random import choice, shuffle

from core.decorators._assistant import asst_cmd, callback
from telethon import TelegramClient
from telethon.errors import ChatSendStickersForbiddenError
from telethon.events import CallbackQuery, Raw
from telethon.tl.functions.messages import SendMediaRequest
from telethon.tl.types import (InputMediaPoll, Poll, PollAnswer,
                               UpdateMessagePollVote)

from .. import Button, asst, async_searcher, get_string, inline_mention


@asst_cmd(pattern="startgame", owner=True)
async def magic(event):
    buttons = [
        [Button.inline("Trivia Quiz", "trzia")],
        [Button.inline("Cancel ❌", "delit")],
    ]
    await event.reply(
        get_string("games_1"),
        file="https://graph.org/file/1c51015bae5205a65fd69.jpg",
        buttons=buttons,
    )


TR_BTS = {}
DIFI_KEYS = ["Easy", "Medium", "Hard"]
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


@callback("delit", owner=True)
async def delete_it(event):
    await event.delete()


@callback(re.compile("ctdown(.*)"), owner=True)
async def ct_spam(e):
    n = e.data_match.group(1).decode("utf-8")
    await e.answer(f"Wait {n} seconds..", alert=True)


@callback(re.compile("trzia(.*)"), owner=True)
async def choose_cata(event: CallbackQuery.Event):
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
        text = get_string("games_2")
    elif match[0] == "d":
        cat = match[1:]
        buttons = [[Button.inline(i, f"trziac{cat}_{i}") for i in DIFI_KEYS]]
        buttons.append([Button.inline("Back", "trzia")])
        text = get_string("games_3")
    elif match[0] == "c":
        m = match[1:]
        buttons = [
            [Button.inline(str(i), f"trziat{m}_{i}") for i in range(10, 70, 20)]]
        text = get_string("games_4")
    elif match[0] == "t":
        m_ = match[1:]
        buttons = [
            [Button.inline(str(i), f"trzias{m_}_{i}")
             for i in [10, 30, 60, 120]]
        ]
        text = get_string("games_5")
    elif match[0] == "s":
        chat = event.chat_id
        cat, le, nu, in_ = match[2:].split("_")
        msg = await event.edit(get_string("games_6").format(le, nu))
        for i in reversed(range(5)):
            msg = await msg.edit(buttons=Button.inline(f"{i} ⏰", f"ctdown{i}"))
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
            await event.respond("Sorry, No Question Found for the given Criteria..")
            await event.delete()
            return
        TRIVIA_CHATS.update({chat: {}})
        for copper, q in enumerate(qs):
            if TRIVIA_CHATS[chat].get("cancel") is not None:
                break
            ansi = str(uuid.uuid1()).split("-")[0].encode()
            opts = [PollAnswer(unescape(q["correct_answer"]), ansi)]
            [
                opts.append(
                    PollAnswer(
                        unescape(a), str(
                            uuid.uuid1()).split("-")[0].encode())
                )
                for a in q["incorrect_answers"]
            ]
            shuffle(opts)
            poll = InputMediaPoll(
                Poll(
                    0,
                    f"[{copper+1}].  " + unescape(q["question"]),
                    answers=opts,
                    public_voters=True,
                    quiz=True,
                    close_period=int(in_),
                ),
                correct_answers=[ansi],
                solution="Join @TeamUltroid",
                solution_entities=[],
            )
            m_ = await event.client(SendMediaRequest(chat, media=poll,
                                                     message=""))
            client: TelegramClient = event.client
            input_chat = await event.get_input_chat()
            m_ = client._get_response_message(None, m_, input_chat)
            POLLS.update(
                {m_.poll.poll.id: {"chat": m_.chat_id, "answer": ansi}})
            await asyncio.sleep(int(in_))
        if not TRIVIA_CHATS[chat]:
            await event.respond(
                "No-One Got Any Score in the Quiz!\nBetter Luck Next Time!"
            )
        else:
            try:
                await event.respond(file=choice(CONGO_STICKER))
            except ChatSendStickersForbiddenError:
                pass
            LBD = "🎯 **Scoreboard of the Quiz.**\n\n"
            TRC = TRIVIA_CHATS[chat]
            if "cancel" in TRC.keys():
                del TRC["cancel"]
            for userid, user_score in dict(
                sorted(TRC.items(), key=operator.itemgetter(1), reverse=True)
            ).items():
                user = inline_mention(await event.client.get_entity(userid))
                LBD += f"••• {user} - {user_score}\n"
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
async def pollish(eve):
    if POLLS.get(eve.poll_id)["chat"] not in TRIVIA_CHATS.keys():
        return
    if POLLS[eve.poll_id]["answer"] != eve.options[0]:
        return
    chat = POLLS.get(eve.poll_id)["chat"]
    user = eve.user_id
    if not TRIVIA_CHATS.get(chat, {}).get(user):
        TRIVIA_CHATS[chat][user] = 1
    else:
        TRIVIA_CHATS[chat][user] += 1


@asst_cmd("cancel", owner=True, func=lambda x: TRIVIA_CHATS.get(x.chat_id))
async def cancelish(event):
    chat = TRIVIA_CHATS.get(event.chat_id)
    chat.update({"cancel": True})
    await event.respond("Cancelled!")
