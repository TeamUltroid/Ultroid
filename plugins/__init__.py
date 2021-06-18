# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import time

from pyUltroid.dB import *
from pyUltroid.dB.core import *
from pyUltroid.functions.all import *
from pyUltroid.functions.asstcmd_db import *
from pyUltroid.functions.broadcast_db import *
from pyUltroid.functions.gban_mute_db import *
from pyUltroid.functions.nsfw_db import *
from pyUltroid.functions.sudos import *
from pyUltroid.utils import *
from telethon import Button
from telethon.tl import functions, types

from strings import get_string

try:
    import glitch_me
except ModuleNotFoundError:
    os.system(
        "git clone https://github.com/1Danish-00/glitch_me.git && pip install -e ./glitch_me"
    )


start_time = time.time()
ultroid_version = "v0.0.8.1"
OWNER_NAME = ultroid_bot.me.first_name
OWNER_ID = ultroid_bot.me.id

List = []
Dict = {}
N = 0


def grt(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "d"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += time_list.pop() + ", "

    time_list.reverse()
    up_time += ":".join(time_list)

    return up_time


_default = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]


_small_caps = [
    "ᴀ",
    "ʙ",
    "ᴄ",
    "ᴅ",
    "ᴇ",
    "ғ",
    "ɢ",
    "ʜ",
    "ɪ",
    "ᴊ",
    "ᴋ",
    "ʟ",
    "ᴍ",
    "ɴ",
    "ᴏ",
    "ᴘ",
    "ϙ",
    "ʀ",
    "s",
    "ᴛ",
    "ᴜ",
    "ᴠ",
    "ᴡ",
    "x",
    "ʏ",
    "ᴢ",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]

_monospace = [
    "𝚊",
    "𝚋",
    "𝚌",
    "𝚍",
    "𝚎",
    "𝚏",
    "𝚐",
    "𝚑",
    "𝚒",
    "𝚓",
    "𝚔",
    "𝚕",
    "𝚖",
    "𝚗",
    "𝚘",
    "𝚙",
    "𝚚",
    "𝚛",
    "𝚜",
    "𝚝",
    "𝚞",
    "𝚟",
    "𝚠",
    "𝚡",
    "𝚢",
    "𝚣",
    "𝙰",
    "𝙱",
    "𝙲",
    "𝙳",
    "𝙴",
    "𝙵",
    "𝙶",
    "𝙷",
    "𝙸",
    "𝙹",
    "𝙺",
    "𝙻",
    "𝙼",
    "𝙽",
    "𝙾",
    "𝙿",
    "𝚀",
    "𝚁",
    "𝚂",
    "𝚃",
    "𝚄",
    "𝚅",
    "𝚆",
    "𝚇",
    "𝚈",
    "𝚉",
]

_double_stroke = [
    "𝕒",
    "𝕓",
    "𝕔",
    "𝕕",
    "𝕖",
    "𝕗",
    "𝕘",
    "𝕙",
    "𝕚",
    "𝕛",
    "𝕜",
    "𝕝",
    "𝕞",
    "𝕟",
    "𝕠",
    "𝕡",
    "𝕢",
    "𝕣",
    "𝕤",
    "𝕥",
    "𝕦",
    "𝕧",
    "𝕨",
    "𝕩",
    "𝕪",
    "𝕫",
    "𝔸",
    "𝔹",
    "ℂ",
    "𝔻",
    "𝔼",
    "𝔽",
    "𝔾",
    "ℍ",
    "𝕀",
    "𝕁",
    "𝕂",
    "𝕃",
    "𝕄",
    "ℕ",
    "𝕆",
    "ℙ",
    "ℚ",
    "ℝ",
    "𝕊",
    "𝕋",
    "𝕌",
    "𝕍",
    "𝕎",
    "𝕏",
    "𝕐",
    "ℤ",
]

_script_royal = [
    "𝒶",
    "𝒷",
    "𝒸",
    "𝒹",
    "𝑒",
    "𝒻",
    "𝑔",
    "𝒽",
    "𝒾",
    "𝒿",
    "𝓀",
    "𝓁",
    "𝓂",
    "𝓃",
    "𝑜",
    "𝓅",
    "𝓆",
    "𝓇",
    "𝓈",
    "𝓉",
    "𝓊",
    "𝓋",
    "𝓌",
    "𝓍",
    "𝓎",
    "𝓏",
    "𝒜",
    "ℬ",
    "𝒞",
    "𝒟",
    "ℰ",
    "ℱ",
    "𝒢",
    "ℋ",
    "ℐ",
    "𝒥",
    "𝒦",
    "ℒ",
    "ℳ",
    "𝒩",
    "𝒪",
    "𝒫",
    "𝒬",
    "ℛ",
    "𝒮",
    "𝒯",
    "𝒰",
    "𝒱",
    "𝒲",
    "𝒳",
    "𝒴",
    "𝒵",
]


KANGING_STR = [
    "Using Witchery to kang this sticker...",
    "Plagiarising hehe...",
    "Inviting this sticker over to my pack...",
    "Kanging this sticker...",
    "Hey that's a nice sticker!\nMind if I kang?!..",
    "Hehe me stel ur stiker...",
    "Ay look over there (☉｡☉)!→\nWhile I kang this...",
    "Roses are red violets are blue, kanging this sticker so my pack looks cool",
    "Imprisoning this sticker...",
    "Mr.Steal-Your-Sticker is stealing this sticker... ",
]
