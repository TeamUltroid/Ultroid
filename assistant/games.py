# copyright aaja

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


@callback(re.compile("trzia(.*)"), owner=True)
async def choose_cata(event):
    match = event.data_match.group(1).decode("utf-8")
    if not match:
        if TR_BTS.get("category"):
            buttons = CAT_BTS["category"]
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
                buttons.append((btt[-1]))
            buttons.append(Button.inline("Cancel ❌", "delit"))
            CAT_BTS.update({"category": buttons})
        text = "Choose Category!"
    elif match[0] == "d":
        cat = match[1:]
        buttons = [Button.inline(i, f"trzias{cat}_{i[0]}") for i in DIFI_KEYS]
        buttons.append(get_back_button("trzia"))
        text = "Choose Difficulty Level"
    await event.edit(text, buttons=buttons)
