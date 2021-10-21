# copyright aaja

import asyncio
import re

from pyUltroid.functions.tools import async_searcher

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
        cat, le, nu = match[2:].split("_")
        msg = await event.edit(
            f"**• Starting Quiz in 5secs.** \n**• Level :** {le}\n**• Qs :** {nu}"
        )
        for i in reversed(range(5)):
            msg = await msg.edit(buttons=Button.inline(str(i), f"ctdown{i}"))
            await asyncio.sleep(1)
        await msg.edit(msg.text + "\n\n• Send /cancel to stop the Quiz...")
        return
    await event.edit(text, buttons=buttons)
