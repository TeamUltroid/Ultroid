# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

""" Imports Folder """

import asyncio
import os
import re
from datetime import datetime as dt

import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls import StreamType
from pyUltroid import HNDLR, CallsClient, udB
from pyUltroid import vcasst as asst
from pyUltroid import vcClient as Client
from pyUltroid.functions.all import bash
from pyUltroid.misc import sudoers

LOG_CHANNEL = int(udB.get("LOG_CHANNEL"))
QUEUE = {}
_vc_sudos = udB.get("VC_SUDOS").split() if udB.get("VC_SUDOS") else ""
A_AUTH = [udB["OWNER_ID"], *sudoers(), *_vc_sudos]
AUTH = [int(x) for x in A_AUTH]


def add_to_queue(chat_id, song, song_name, from_user):
    try:
        play_at = len(QUEUE[int(chat_id)]) + 1
    except BaseException:
        play_at = 1
    QUEUE.update(
        {
            int(chat_id): {
                play_at: {"song": song, "title": song_name, "from_user": from_user}
            }
        }
    )
    return QUEUE[int(chat_id)]


def get_from_queue(chat_id):
    try:
        play_this = list(QUEUE[int(chat_id)].keys())[0]
    except KeyError:
        raise KeyError
    info = QUEUE[int(chat_id)][play_this]
    song = info["song"]
    title = info["title"]
    from_user = info["from_user"]
    return song, title, from_user


async def eor(message, text, *args, **kwargs):
    if message.outgoing:
        return await message.edit_text(text, *args, **kwargs)
    return await message.reply_text(text, *args, **kwargs)


async def download(query, chat, ts):
    song = f"VCSONG_{chat}_{ts}.raw"
    if ("youtube.com" or "youtu.be") in query:
        await bash(
            f"""youtube-dl -x --audio-format best --audio-quality 1 --postprocessor-args "-f s16le -ac 1 -acodec pcm_s16le -ar 48000 '{song}' -y" {query}"""
        )
    else:
        await bash(
            f"""youtube-dl -x --audio-format best --audio-quality 1 --postprocessor-args "-f s16le -ac 1 -acodec pcm_s16le -ar 48000 '{song}' -y" ytsearch:'{query}'"""
        )
    return song
