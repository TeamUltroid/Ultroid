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
from pyrogram.raw import functions
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytgcalls import StreamType
from pyUltroid import HNDLR, CallsClient
from pyUltroid import asst as tele_asst
from pyUltroid import udB, ultroid_bot
from pyUltroid import vcasst as asst
from pyUltroid.functions.all import bash, dler, time_formatter
from pyUltroid.misc import sudoers
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch

Client = CallsClient._app

LOG_CHANNEL = int(udB.get("LOG_CHANNEL"))
QUEUE = {}

_yt_base_url = "https://www.youtube.com/watch?v="
vcusername = tele_asst.me.username


def VC_AUTHS():
    _vc_sudos = udB.get("VC_SUDOS").split() if udB.get("VC_SUDOS") else ""
    A_AUTH = [udB["OWNER_ID"], *sudoers(), *_vc_sudos]
    AUTH = [int(x) for x in A_AUTH]
    return AUTH


def reply_markup(chat_id: int):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Pause", callback_data=f"vcp_{chat_id}"),
                InlineKeyboardButton("Skip", callback_data=f"skip_{chat_id}"),
            ],
            [InlineKeyboardButton("Exit", callback_data=f"ex_{chat_id}")],
        ]
    )


def add_to_queue(chat_id, song, song_name, from_user, duration):
    try:
        n = sorted(list(QUEUE[int(chat_id)].keys()))
        play_at = n[-1] + 1
    except BaseException:
        play_at = 1
    if QUEUE.get(int(chat_id)):
        QUEUE[int(chat_id)].update(
            {
                play_at: {
                    "song": song,
                    "title": song_name,
                    "from_user": from_user,
                    "duration": duration,
                }
            }
        )
    else:
        QUEUE.update(
            {
                int(chat_id): {
                    play_at: {
                        "song": song,
                        "title": song_name,
                        "from_user": from_user,
                        "duration": duration,
                    }
                }
            }
        )
    return QUEUE[int(chat_id)]


def list_queue(chat):
    if QUEUE.get(chat):
        txt, n = "", 0
        for x in list(QUEUE[chat].keys()):
            n += 1
            data = QUEUE[chat][x]
            txt += f'**{n}.{data["title"]}** : __By {data["from_user"]}__\n'
        return txt


def get_from_queue(chat_id):
    play_this = list(QUEUE[int(chat_id)].keys())[0]
    info = QUEUE[int(chat_id)][play_this]
    song = info["song"]
    title = info["title"]
    from_user = info["from_user"]
    duration = info["duration"]
    return song, title, from_user, play_this, duration


async def eor(message, text, *args, **kwargs):
    if message.outgoing:
        return await message.edit_text(text, *args, **kwargs)
    return await message.reply_text(text, *args, **kwargs)


async def download(event, query, chat, ts):
    song = f"VCSONG_{chat}_{ts}.raw"
    search = VideosSearch(query, limit=1).result()
    noo = search["result"][0]
    vid_id = noo["id"]
    link = _yt_base_url + vid_id
    opts = {
        "format": "bestaudio",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "outtmpl": "%(id)s.mp3",
        "quiet": True,
        "logtostderr": False,
    }
    ytdl_data = await dler(event, link)
    YoutubeDL(opts).download([link])
    dl = vid_id + ".mp3"
    title = ytdl_data["title"]
    duration = ytdl_data["duration"]
    thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"
    await bash(f'ffmpeg -i "{dl}" -f s16le -ac 1 -acodec pcm_s16le -ar 48000 {song} -y')
    return song, thumb, title, duration


async def vc_check(chat, chat_type):
    if chat_type in ["supergroup", "channel"]:
        chat = await Client.send(
            functions.channels.GetFullChannel(channel=await Client.resolve_peer(chat))
        )
    elif chat_type == "group":
        chat = await Client.send(functions.messages.GetFullChat(chat_id=chat))
    else:
        return False
    if not chat.full_chat.call:
        return False
    return True
