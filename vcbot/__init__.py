# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

import asyncio
import re
import subprocess
from os import remove
from time import time

from pytgcalls import GroupCallFactory
from pyUltroid import LOGS, asst, udB, vcClient
from pyUltroid.functions.all import (
    bash,
    dler,
    downloader,
    get_user_id,
    inline_mention,
    mediainfo,
    time_formatter,
)
from pyUltroid.misc import sudoers
from pyUltroid.misc._wrappers import eod, eor
from telethon import events
from youtubesearchpython import ResultMode, Video, VideosSearch

from strings import get_string

asstUserName = asst.me.username
LOG_CHANNEL = int(udB["LOG_CHANNEL"])
ACTIVE_CALLS, VC_QUEUE = [], {}
CLIENTS = {}


def VC_AUTHS():
    _vc_sudos = udB.get("VC_SUDOS").split() if udB.get("VC_SUDOS") else ""
    A_AUTH = [udB["OWNER_ID"], *sudoers(), *_vc_sudos]
    return [int(x) for x in A_AUTH]


async def download(query, chat, ts):
    song = f"VCSONG_{chat}_{ts}.raw"
    search = VideosSearch(query, limit=1).result()
    data = search["result"][0]
    link = data["link"]
    dl = await bash(f"youtube-dl -x -g {link}")
    title = data["title"]
    duration = data["duration"]
    thumb = data["thumbnails"][-1]["url"] + ".jpg"
    raw_converter(dl[0], song)
    return song, thumb, title, duration


async def live_dl(link, file):
    dl = await bash(f"youtube-dl -x -g {link}")
    raw_converter(dl[0], file)
    info = eval(Video.getInfo(link, mode=ResultMode.json))
    title = info["title"]
    thumb = info["thumbnails"][-1]["url"] + ".jpg"
    duration = "♾"
    return thumb, title, duration


async def file_download(event, reply, chat, ts):
    song = f"VCSONG_{chat}_{ts}.raw"
    thumb = None
    title = reply.file.title if reply.file.title else reply.file.name
    dl = await downloader(
        "resources/downloads/" + reply.file.name,
        reply.media.document,
        event,
        time(),
        "Downloading " + title + "...",
    )
    duration = reply.file.duration
    if reply.document.thumbs:
        thumb = await reply.download_media(thumb=-1)
    raw_converter(dl.name, song)
    return song, thumb, title, duration


def raw_converter(dl, song):
    subprocess.Popen(
        [
            "ffmpeg",
            "-y",
            "-i",
            dl,
            "-f",
            "s16le",
            "-ac",
            "2",
            "-ar",
            "48000",
            "-acodec",
            "pcm_s16le",
            song,
        ],
        stdin=None,
        stdout=None,
        stderr=None,
        cwd=None,
    )


def vc_asst(dec):
    def ult(func):
        pattern = "\\" + udB["VC_HNDLR"] if udB.get("VC_HNDLR") else "/"
        asst.add_event_handler(
            func,
            events.NewMessage(
                incoming=True,
                pattern=re.compile(pattern + dec),
                from_users=VC_AUTHS(),
                func=lambda e: not e.is_private and not e.via_bot_id,
            ),
        )
        vcClient.add_event_handler(
            func,
            events.NewMessage(
                outgoing=True,
                pattern=re.compile(pattern + dec),
                func=lambda e: not e.is_private and not e.via_bot_id,
            ),
        )

    return ult


def add_to_queue(chat_id, song, song_name, thumb, from_user, duration):
    try:
        n = sorted(list(VC_QUEUE[int(chat_id)].keys()))
        play_at = n[-1] + 1
    except BaseException:
        play_at = 1
    if VC_QUEUE.get(int(chat_id)):
        VC_QUEUE[int(chat_id)].update(
            {
                play_at: {
                    "song": song,
                    "title": song_name,
                    "thumb": thumb,
                    "from_user": from_user,
                    "duration": duration,
                }
            }
        )
    else:
        VC_QUEUE.update(
            {
                int(chat_id): {
                    play_at: {
                        "song": song,
                        "title": song_name,
                        "thumb": thumb,
                        "from_user": from_user,
                        "duration": duration,
                    }
                }
            }
        )
    return VC_QUEUE[int(chat_id)]


async def list_queue(chat):
    if VC_QUEUE.get(chat):
        txt, n = "", 0
        for x in list(VC_QUEUE[chat].keys()):
            n += 1
            data = VC_QUEUE[chat][x]
            user = await vcClient.get_entity(data["from_user"])
            txt += f'**{n}.{data["title"]}** : __By {inline_mention(user)}__\n'
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


class Player:
    def __init__(self, chat):
        self._chat = chat
        if CLIENTS.get(chat):
            self.group_call = CLIENTS[chat]
        else:
            _client = GroupCallFactory(
                vcClient, GroupCallFactory.MTPROTO_CLIENT_TYPE.TELETHON
            )
            self.group_call = _client.get_file_group_call()
            CLIENTS.update({chat: self.group_call})

    async def startCall(self):
        if self._chat not in ACTIVE_CALLS:
            try:
                self.group_call.on_network_status_changed(self.on_network_changed)
                self.group_call.on_playout_ended(self.playout_ended_handler)
                await self.group_call.start(self._chat)
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
            try:
                remove(call._GroupCallFile__input_filename)
            except BaseException:
                pass

    async def playout_ended_handler(self, call, __):
        try:
            remove(call._GroupCallFile__input_filename)
        except BaseException:
            pass
        await self.play_from_queue()

    async def play_from_queue(self):
        chat_id = self._chat
        try:
            song, title, thumb, from_user, pos, dur = get_from_queue(chat_id)
            self.group_call.input_filename = song
            xx = await asst.send_message(
                chat_id,
                "🎧 **Now playing #{}**: `{}`\n⏰ **Duration:** `{}`\n👤 **Requested by:** {}".format(
                    pos, title, time_formatter(dur * 1000), from_user
                ),
                file=thumb,
            )
            VC_QUEUE[chat_id].pop(pos)
            if not VC_QUEUE[chat_id]:
                VC_QUEUE.pop(chat_id)
            await asyncio.sleep(dur + 5)
            await xx.delete()

        except (IndexError, KeyError):
            await self.group_call.stop()
            del CLIENTS[self._chat]
            await asst.send_message(
                LOG_CHANNEL, f"• Successfully Left Vc : `{chat_id}` •"
            )
            try:
                await asst.send_message(
                    chat_id, "`Queue is empty. Left the voice chat now !`"
                )
            except BaseException:
                pass
        except Exception as e:
            LOGS.info(e)
            await asst.send_message(LOG_CHANNEL, f"**ERROR:** {e}")

    async def vc_joiner(self):
        done, err = await self.startCall()
        chat_id = self._chat
        if done:
            await asst.send_message(LOG_CHANNEL, "• Joined VC in {}".format(chat_id))
            return True
        await asst.send_message(
            LOG_CHANNEL, f"**ERROR while Joining Vc - `{chat_id}` :**\n{err}"
        )
        return False


# --------------------------------------------------
