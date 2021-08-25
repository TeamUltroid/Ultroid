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
from pyUltroid import LOGS, asst, udB, vcClient
from pyUltroid.dB.core import ACTIVE_CALLS, VC_QUEUE
from pyUltroid.functions.all import bash, dler, get_user_id, time_formatter
from pyUltroid.misc import sudoers
from pyUltroid.misc._wrappers import eod, eor
from telethon import events
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch

_yt_base_url = "https://www.youtube.com/watch?v="
asstUserName = asst.me.username
CLIENTS = {}


def VC_AUTHS():
    _vc_sudos = udB.get("VC_SUDOS").split() if udB.get("VC_SUDOS") else ""
    A_AUTH = [udB["OWNER_ID"], *sudoers(), *_vc_sudos]
    return [int(x) for x in A_AUTH]


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
    try:
        ytdl_data = await dler(event, url=link, opts=opts, download=True)
    except Exception as e:
        return await eor(event, str(e))
    dl = vid_id + ".mp3"
    title = ytdl_data["title"]
    duration = ytdl_data["duration"]
    thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"
    await raw_converter(dl, song)
    return song, thumb, title, duration


async def file_download(event, chat, ts):
    song = f"VCSONG_{chat}_{ts}.raw"
    thumb = None
    dl = await event.download_media()
    title = event.file.title
    duration = event.file.duration
    if event.document.thumbs:
        thumb = await event.download_media(thumb=-1)
    await raw_converter(dl, song)
    remove(dl)
    return song, thumb, title, duration


async def raw_converter(dl, song):
    out, err = await bash(
        f'ffmpeg -y -i "{dl}" -f s16le -ac 2 -ar 48000 -acodec pcm_s16le "{song}"'
    )
    if err != "":
        LOGS.info(err)


def vc_asst(dec):
    def ult(func):
        pattern = "\\" + udB["VC_HNDLR"] if udB.get("VC_HNDLR") else "/"
        # pattern = f"^({pattern}|{pattern}@{asstUserName})"
        asst.add_event_handler(
            func,
            events.NewMessage(
                incoming=True, pattern=re.compile(pattern + dec), from_users=VC_AUTHS()
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


# credits to @subinps for the basic working idea
class Player(object):
    _client = None

    def __init__(self, chat):
        try:
            self._client = CLIENTS[chat]
            self.group_call = self._client.get_file_group_call()
        except KeyError:
            _client = GroupCallFactory(
                vcClient, GroupCallFactory.MTPROTO_CLIENT_TYPE.TELETHON
            )
            CLIENTS.update({chat: _client})
            self._client = _client
            self.group_call = self._client.get_file_group_call()
            self.group_call.on_network_status_changed(on_network_changed)
            self.group_call.on_playout_ended(playout_ended_handler)

    async def startCall(self, chat):
        if chat not in ACTIVE_CALLS:
            try:
                await self.group_call.start(chat)
            except Exception as e:
                return False, e
        return True, None


# ultSongs = Player()


async def vc_joiner(event, chat_id):
    done, err = await ultSongs.startCall(chat_id)
    if done:
        await eor(event, "Joined VC in {}".format(chat_id))
        return True
    else:
        await eor(event, "**ERROR:**\n{}".format(err))
        return False


async def play_from_queue(chat_id):
    chat_id = chat_id if str(chat_id).startswith("-100") else int("-100" + str(chat_id))
    try:
        song, title, thumb, from_user, pos, dur = get_from_queue(chat_id)
        ultSongs.group_call.input_filename = song
        xx = await asst.send_message(
            chat_id,
            "**Now playing #{}**: `{}`\n**Duration:** `{}`\n**Requested by:** `{}`".format(
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
        await asst.send_message(
            chat_id, "`Queue is empty. Leaving the voice chat now !`"
        )
        await ultSongs.group_call.stop()
    except Exception as e:
        LOGS.info(e)
        await asst.send_message(chat_id, "**ERROR:**\n{}".format(str(e)))


# @ultSongs.group_call.on_network_status_changed
async def on_network_changed(call, is_connected):
    chat = call.full_chat.id
    chat = chat if str(chat).startswith("-100") else int("-100" + str(chat))
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


# @ultSongs.group_call.on_playout_ended
async def playout_ended_handler(call, __):
    chat = call.full_chat.id
    chat = chat if str(chat).startswith("-100") else int("-100" + str(chat))
    try:
        remove(call._GroupCallFile__input_filename)
    except BaseException:
        pass
    await play_from_queue(chat)
