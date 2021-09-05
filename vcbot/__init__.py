# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import asyncio
import re
from os import remove
from time import time

from pytgcalls import GroupCallFactory
from pyUltroid import HNDLR, LOGS, asst, udB, vcClient
from pyUltroid.functions.all import (
    bash,
    downloader,
    get_user_id,
    inline_mention,
    mediainfo,
    time_formatter,
)
from pyUltroid.functions.vc_group import check_vcauth
from pyUltroid.functions.vc_group import get_chats as get_vc
from pyUltroid.misc import owner_and_sudos, sudoers
from pyUltroid.misc._assistant import admin_check, in_pattern
from pyUltroid.misc._wrappers import eod, eor
from telethon import events
from telethon.tl import types
from youtubesearchpython import ResultMode, Video, VideosSearch

from strings import get_string

asstUserName = asst.me.username
LOG_CHANNEL = int(udB["LOG_CHANNEL"])
ACTIVE_CALLS, VC_QUEUE = [], {}
MSGID_CACHE, VIDEO_ON = {}, {}
CLIENTS = {}


def VC_AUTHS():
    _vc_sudos = udB.get("VC_SUDOS").split() if udB.get("VC_SUDOS") else ""
    A_AUTH = [*owner_and_sudos(), *_vc_sudos]
    return A_AUTH


# --------------------------------------------------


class Player:
    def __init__(self, chat, event=None, video=False):
        self._chat = chat
        self._current_chat = event.chat_id if event else LOG_CHANNEL
        self._video = video
        if CLIENTS.get(chat):
            self.group_call = CLIENTS[chat]
        else:
            _client = GroupCallFactory(
                vcClient, GroupCallFactory.MTPROTO_CLIENT_TYPE.TELETHON
            )
            self.group_call = _client.get_group_call()
            CLIENTS.update({chat: self.group_call})

    async def startCall(self):
        if VIDEO_ON:
            for chats in VIDEO_ON:
                await VIDEO_ON[chats].stop()
            VIDEO_ON.clear()
            await asyncio.sleep(3)
        if self._video:
            for chats in CLIENTS:
                if chats != self._chat:
                    await CLIENTS[chats].stop()
                    del CLIENTS[chats]
            VIDEO_ON.update({self._chat: self.group_call})
        if self._chat not in ACTIVE_CALLS:
            try:
                self.group_call.on_network_status_changed(self.on_network_changed)
                # self.group_call.on_playout_ended(self.playout_ended_handler)
                await self.group_call.join(self._chat)
            except Exception as e:
                return False, e
        return True, None

    async def on_network_changed(self, call, is_connected):
        chat = self._chat
        if is_connected:
            if chat not in ACTIVE_CALLS:
                ACTIVE_CALLS.append(chat)
        else:
            if chat in ACTIVE_CALLS:
                ACTIVE_CALLS.remove(chat)

    async def playout_ended_handler(self, call, __):
        await self.play_from_queue()

    async def play_from_queue(self):
        chat_id = self._chat
        if chat_id in VIDEO_ON:
            await self.startCall()
        try:
            song, title, thumb, from_user, pos, dur = get_from_queue(chat_id)
            await self.group_call.start_audio(song)
            if MSGID_CACHE.get(chat_id):
                await MSGID_CACHE[chat_id].delete()
                del MSGID_CACHE[chat_id]
            xx = await vcClient.send_message(
                self._current_chat,
                "🎧 **Now playing #{}**: `{}`\n⏰ **Duration:** `{}`\n👤 **Requested by:** {}".format(
                    pos, title, dur, from_user
                ),
                file=thumb,
            )
            MSGID_CACHE.update({chat_id: xx})
            VC_QUEUE[chat_id].pop(pos)
            if not VC_QUEUE[chat_id]:
                VC_QUEUE.pop(chat_id)

        except (IndexError, KeyError):
            await self.group_call.stop()
            del CLIENTS[self._chat]
            await vcClient.send_message(
                self._current_chat, f"• Successfully Left Vc : `{chat_id}` •"
            )
        except Exception as er:
            await vcClient.send_message(self._current_chat, f"**ERROR:** {er}")

    async def vc_joiner(self):
        done, err = await self.startCall()
        chat_id = self._chat
        if done:
            await vcClient.send_message(
                self._current_chat, "• Joined VC in {}".format(chat_id)
            )
            return True
        await vcClient.send_message(
            self._current_chat, f"**ERROR while Joining Vc - `{chat_id}` :**\n{err}"
        )
        return False


# --------------------------------------------------


def vc_asst(dec, from_users=VC_AUTHS(), vc_auth=True):
    def ult(func):
        handler = udB["VC_HNDLR"] if udB.get("VC_HNDLR") else HNDLR

        async def vc_handler(e):
            VCAUTH = list(get_vc().keys())
            if not (
                (e.out)
                or (str(e.sender_id) in from_users)
                or (vc_auth and e.chat_id in VCAUTH)
            ):
                return
            if vc_auth:
                cha, adm = check_vcauth(e.chat_id)
                if adm and not (await admin_check(e)):
                    return
            try:
                await func(e)
            except Exception as er:
                LOGS.info(f"VC Error - {e.chat_id} - {er}")

        vcClient.add_event_handler(
            vc_handler,
            events.NewMessage(
                pattern=re.compile(f"\\{handler}" + dec),
                func=lambda e: not e.is_private and not e.via_bot_id,
            ),
        )

    return ult


# --------------------------------------------------


def add_to_queue(chat_id, song, song_name, thumb, from_user, duration):
    try:
        n = sorted(list(VC_QUEUE[chat_id].keys()))
        play_at = n[-1] + 1
    except BaseException:
        play_at = 1
    stuff = {
        play_at: {
            "song": song,
            "title": song_name,
            "thumb": thumb,
            "from_user": from_user,
            "duration": duration,
        }
    }
    if VC_QUEUE.get(chat_id):
        VC_QUEUE[int(chat_id)].update(stuff)
    else:
        VC_QUEUE.update({chat_id: stuff})
    return VC_QUEUE[chat_id]


def list_queue(chat):
    if VC_QUEUE.get(chat):
        txt, n = "", 0
        for x in list(VC_QUEUE[chat].keys()):
            n += 1
            data = VC_QUEUE[chat][x]
            txt += f'**{n}.{data["title"]}** : __By {data["from_user"]}__\n'
        return txt


def get_from_queue(chat_id):
    play_this = list(VC_QUEUE[int(chat_id)].keys())[0]
    info = VC_QUEUE[int(chat_id)][play_this]
    song = info["song"]
    title = info["title"]
    thumb = info["thumb"]
    from_user = info["from_user"]
    duration = info["duration"]
    return song, title, thumb, from_user, play_this, duration


# --------------------------------------------------


async def download(query):
    search = VideosSearch(query, limit=1).result()
    data = search["result"][0]
    link = data["link"]
    dl = await bash(f"youtube-dl -x -g {link}")
    title = data["title"]
    duration = data["duration"] or "♾"
    thumb = data["thumbnails"][-1]["url"] + ".jpg"
    return dl[0], thumb, title, duration


async def live_dl(link):
    dl = await bash(f"youtube-dl -x -g {link}")
    info = eval(Video.getInfo(link, mode=ResultMode.json))
    title = info["title"]
    thumb = info["thumbnails"][-1]["url"] + ".jpg"
    duration = "♾"
    return dl[0], thumb, title, duration

async def vid_download(query):
    search = VideosSearch(query, limit=1).result()
    data = search["result"][0]
    link = data["link"]
    vid, aud = (await bash(f"youtube-dl -g {link}"))[0].split()
    title = data["title"]
    thumb = data["thumbnails"][-1]["url"] + ".jpg"
    duration = data["duration"] or "♾"
    return vid, aud, thumb, title, duration

async def file_download(event, reply, fast_download=True):
    thumb = None
    title = reply.file.title or reply.file.name
    if fast_download:
        dl = await downloader(
            "resources/downloads/" + reply.file.name,
            reply.media.document,
            event,
            time(),
            "Downloading " + title + "...",
        )
        dl = dl.name
    else:
        dl = await reply.download_media()
    duration = time_formatter(reply.file.duration * 1000)
    if reply.document.thumbs:
        thumb = await reply.download_media("vcbot/downloads/", thumb=-1)
    return dl, thumb, title, duration


# --------------------------------------------------
