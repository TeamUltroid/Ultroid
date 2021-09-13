# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# ----------------------------------------------------------#
#                                                           #
#    _   _ _   _____ ____   ___ ___ ____   __     ______    #
#   | | | | | |_   _|  _ \ / _ \_ _|  _ \  \ \   / / ___|   #
#   | | | | |   | | | |_) | | | | || | | |  \ \ / / |       #
#   | |_| | |___| | |  _ <| |_| | || |_| |   \ V /| |___    #
#    \___/|_____|_| |_| \_\\___/___|____/     \_/  \____|   #
#                                                           #
# ----------------------------------------------------------#


import asyncio
import os
import re
import traceback
from time import time
from traceback import format_exc

from pytgcalls import GroupCallFactory
from pytgcalls.exceptions import GroupCallNotFoundError
from pyUltroid import HNDLR, LOGS, asst, udB, vcClient
from pyUltroid.functions.all import (
    bash,
    downloader,
    get_user_id,
    get_videos_link,
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
from telethon.tl import functions, types
from telethon.utils import get_display_name
from youtube_dl import YoutubeDL
from youtubesearchpython import Playlist, ResultMode, Video, VideosSearch

from strings import get_string

asstUserName = asst.me.username
LOG_CHANNEL = int(udB["LOG_CHANNEL"])
ACTIVE_CALLS, VC_QUEUE = [], {}
MSGID_CACHE, VIDEO_ON = {}, {}
CLIENTS = {}


def html_mention(event, sender_id=None, full_name=None):
    if not full_name:
        full_name = get_display_name(event.sender)
    if not sender_id:
        sender_id = event.sender_id
    return "<a href={}>{}</a>".format(f"tg://user?id={sender_id}", full_name)


def VC_AUTHS():
    _vc_sudos = udB.get("VC_SUDOS").split() if udB.get("VC_SUDOS") else ""
    A_AUTH = [*owner_and_sudos(), *_vc_sudos]
    return A_AUTH


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

    async def make_vc_active(self):
        try:
            await vcClient(
                functions.phone.CreateGroupCallRequest(
                    self._chat, title="🎧 Ultroid Music 🎶"
                )
            )
        except Exception as e:
            return False, e
        return True, None

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
                self.group_call.on_playout_ended(self.playout_ended_handler)
                await self.group_call.join(self._chat)
            except GroupCallNotFoundError:
                dn, err = await self.make_vc_active()
                if err:
                    return False, err
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

    async def playout_ended_handler(self, call, source, mtype):
        if os.path.exists(source):
            os.remove(source)
        await self.play_from_queue()

    async def play_from_queue(self):
        chat_id = self._chat
        if chat_id in VIDEO_ON:
            await self.group_call.stop_video()
            VIDEO_ON.pop(chat_id)
        try:
            song, title, link, thumb, from_user, pos, dur = await get_from_queue(
                chat_id
            )
            await self.group_call.start_audio(song)
            if MSGID_CACHE.get(chat_id):
                await MSGID_CACHE[chat_id].delete()
                del MSGID_CACHE[chat_id]
            xx = await vcClient.send_message(
                self._current_chat,
                "<strong>🎧 Now playing #{}: <a href={}>{}</a>\n⏰ Duration:</strong> <code>{}</code>\n👤 <strong>Requested by:</strong> {}".format(
                    pos, link, title, dur, from_user
                ),
                file=thumb,
                link_preview=False,
                parse_mode="html",
            )
            MSGID_CACHE.update({chat_id: xx})
            VC_QUEUE[chat_id].pop(pos)
            if not VC_QUEUE[chat_id]:
                VC_QUEUE.pop(chat_id)

        except (IndexError, KeyError):
            await self.group_call.stop()
            del CLIENTS[self._chat]
            await vcClient.send_message(
                self._current_chat,
                f"• Successfully Left Vc : <code>{chat_id}</code> •",
                parse_mode="html",
            )
        except Exception:
            await vcClient.send_message(
                self._current_chat,
                f"<strong>ERROR:</strong> <code>{format_exc()}</code>",
                parse_mode="html",
            )

    async def vc_joiner(self):
        chat_id = self._chat
        done, err = await self.startCall()

        if done:
            await vcClient.send_message(
                self._current_chat,
                "• Joined VC in <code>{}</code>".format(chat_id),
                parse_mode="html",
            )
            return True
        await vcClient.send_message(
            self._current_chat,
            f"<strong>ERROR while Joining Vc -</strong> <code>{chat_id}</code> :\n<code>{err}</code>",
            parse_mode="html",
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
            except Exception:
                LOGS.exception(Exception)
                await asst.send_message(
                    LOG_CHANNEL,
                    f"VC Error - <code>{e.chat_id}</code>\n\n<code>{format_exc()}</code>",
                    parse_mode="html",
                )

        vcClient.add_event_handler(
            vc_handler,
            events.NewMessage(
                pattern=re.compile(f"\\{handler}" + dec),
                func=lambda e: not e.is_private and not e.via_bot_id,
            ),
        )

    return ult


# --------------------------------------------------


def add_to_queue(chat_id, song, song_name, link, thumb, from_user, duration):
    try:
        n = sorted(list(VC_QUEUE[chat_id].keys()))
        play_at = n[-1] + 1
    except BaseException:
        play_at = 1
    stuff = {
        play_at: {
            "song": song,
            "title": song_name,
            "link": link,
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
        for x in list(VC_QUEUE[chat].keys())[:18]:
            n += 1
            data = VC_QUEUE[chat][x]
            txt += f'<strong>{n}. <a href={data["link"]}>{data["title"]}</a> :</strong> <i>By: {data["from_user"]}</i>\n'
        txt += "\n\n....."
        return txt


async def get_from_queue(chat_id):
    play_this = list(VC_QUEUE[int(chat_id)].keys())[0]
    info = VC_QUEUE[int(chat_id)][play_this]
    song = info.get("song")
    title = info["title"]
    link = info["link"]
    thumb = info["thumb"]
    from_user = info["from_user"]
    duration = info["duration"]
    if not song:
        song = await get_stream_link(link)
    return song, title, link, thumb, from_user, play_this, duration


# --------------------------------------------------


async def download(query):
    search = VideosSearch(query, limit=1).result()
    data = search["result"][0]
    link = data["link"]
    dl = await get_stream_link(link)
    title = data["title"]
    duration = data.get("duration") or "♾"
    thumb = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
    return dl, thumb, title, link, duration


async def get_stream_link(ytlink):
    """
    info = YoutubeDL({}).extract_info(url=ytlink, download=False)
    k = ""
    for x in info["formats"]:
        h, w = ([x["height"], x["width"]])
        if h and w:
            if h <= 720 and w <= 1280:
                k = x["url"]
    return k
    """
    stream = await bash(f'youtube-dl -g -f "best[height<=?720][width<=?1280]" {ytlink}')
    return stream[0]


async def vid_download(query):
    search = VideosSearch(query, limit=1).result()
    data = search["result"][0]
    link = data["link"]
    video = await get_stream_link(link)
    title = data["title"]
    thumb = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
    duration = data.get("duration") or "♾"
    return video, thumb, title, link, duration


async def dl_playlist(chat, from_user, link):
    # untill issue get fix
    # https://github.com/alexmercerind/youtube-search-python/issues/107
    """
    vids = Playlist.getVideos(link)
    try:
        vid1 = vids["videos"][0]
        duration = vid1["duration"] or "♾"
        title = vid1["title"]
        song = await get_stream_link(vid1['link'])
        thumb = f"https://i.ytimg.com/vi/{vid1['id']}/hqdefault.jpg"
        return song[0], thumb, title, vid1["link"], duration
    finally:
        vids = vids["videos"][1:]
        for z in vids:
            duration = z["duration"] or "♾"
            title = z["title"]
            thumb = f"https://i.ytimg.com/vi/{z['id']}/hqdefault.jpg"
            add_to_queue(chat, None, title, z["link"], thumb, from_user, duration)
    """
    links = await get_videos_link(link)
    try:
        search = VideosSearch(links[0], limit=1).result()
        vid1 = search["result"][0]
        duration = vid1.get("duration") or "♾"
        title = vid1["title"]
        song = await get_stream_link(vid1["link"])
        thumb = f"https://i.ytimg.com/vi/{vid1['id']}/hqdefault.jpg"
        return song, thumb, title, vid1["link"], duration
    finally:
        for z in links[1:]:
            search = VideosSearch(z, limit=1).result()
            vid = search["result"][0]
            duration = vid.get("duration") or "♾"
            title = vid["title"]
            thumb = f"https://i.ytimg.com/vi/{vid['id']}/hqdefault.jpg"
            add_to_queue(chat, None, title, vid["link"], thumb, from_user, duration)


async def file_download(event, reply, fast_download=True):
    thumb = "https://telegra.ph/file/22bb2349da20c7524e4db.mp4"
    title = reply.file.title or reply.file.name
    if fast_download:
        dl = await downloader(
            "vcbot/downloads/" + reply.file.name,
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
    return dl, thumb, title, reply.message_link, duration


# --------------------------------------------------
