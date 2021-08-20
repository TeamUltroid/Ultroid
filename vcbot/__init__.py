import asyncio
import os
import random
import subprocess
from asyncio import sleep
from datetime import datetime
from os import path
from random import randint
from signal import SIGINT

import ffmpeg
import wget
from pyrogram import emoji
from pyrogram.methods.messages.download_media import DEFAULT_DOWNLOAD_DIR
from pyUltroid import CallsClient, Var, asst, udB
from pyUltroid import ultroid_bot as ultroid
from pyUltroid import vcClient
from pyUltroid.misc import sudoers
from telethon import events
from youtube_dl import YoutubeDL

USERNAME = asst.me.username

FFMPEG_PROCESSES = {}
ADMIN_LIST = {}
CALL_STATUS = {}
GET_FILE = {}
EDIT_TITLE = udB.get("EDIT_TITLE") or "Ultroid Songs"
RADIO = {6}
LOG_GROUP = Var.LOG_CHANNEL
DURATION_LIMIT = 15
DELAY = 10
playlist = []
msg = {}
SHUFFLE = True
LIMIT = 350
STREAM_URL = (
    udB.get("STREAM_URL")
    or "https://bcovlive-a.akamaihd.net/19b535b7499a4719a5c19e043063f5d9/ap-southeast-1/6034685947001/playlist.m3u8?nocache=825347"
)
CPLAY = udB.get("CPLAY") or True

ydl_opts = {
    "format": "bestaudio[ext=m4a]",
    "geo-bypass": True,
    "nocheckcertificate": True,
    "outtmpl": "downloads/%(id)s.%(ext)s",
}
ydl = YoutubeDL(ydl_opts)

RADIO_TITLE = os.environ.get("RADIO_TITLE", " 🎸 Music 24/7 | Radio Mode")
if RADIO_TITLE == "NO":
    RADIO_TITLE = None


def VC_AUTHS():
    _vc_sudos = udB.get("VC_SUDOS").split() if udB.get("VC_SUDOS") else ""
    A_AUTH = [udB["OWNER_ID"], *sudoers(), *_vc_sudos]
    return [int(x) for x in A_AUTH]


def vc_asst(dec):
    def ult(func):
        pattern = "^/" + dec
        asst.add_event_handler(
            func,
            events.NewMessage(incoming=True, pattern=pattern, from_users=VC_AUTHS()),
        )
        asst.add_event_handler(
            events.NewMessage(
                incoming=True,
                pattern=pattern + "@" + asst.me.username,
                from_users=VC_AUTHS(),
            ),
        )

    return ult


# --------------------------------------------------


class Player(object):
    def __init__(self):
        self.group_call = CallsClient.get_file_group_call()

    async def send_playlist(self):
        if not playlist:
            pl = f"{emoji.NO_ENTRY} Empty playlist"
        elif len(playlist) >= 25:
            tplaylist = playlist[:25]
            pl = f"Listing first 25 songs of total {len(playlist)} songs.\n"
            pl += f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join(
                f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}"
                for i, x in enumerate(tplaylist)
            )

        else:
            pl = f"{emoji.PLAY_BUTTON} **Playlist**:\n" + "\n".join(
                f"**{i}**. **🎸{x[1]}**\n   👤**Requested by:** {x[4]}\n"
                for i, x in enumerate(playlist)
            )

        if msg.get("playlist") is not None:
            await msg["playlist"].delete()
        msg["playlist"] = await self.send_text(pl)

    async def skip_current_playing(self):
        group_call = self.group_call
        if not playlist:
            return
        if len(playlist) == 1:
            await mp.start_radio()
            return
        client = group_call.client
        download_dir = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR)
        group_call.input_filename = os.path.join(download_dir, f"{playlist[1][5]}.raw")
        # remove old track from playlist
        old_track = playlist.pop(0)
        print(f"- START PLAYING: {playlist[0][1]}")
        if EDIT_TITLE:
            await self.edit_title()
        if LOG_GROUP:
            await self.send_playlist()
        os.remove(os.path.join(download_dir, f"{old_track[5]}.raw"))
        oldfile = GET_FILE.get(old_track[2])
        os.remove(oldfile)
        if len(playlist) == 1:
            return
        await self.download_audio(playlist[1])

    async def send_text(self, text):
        self.group_call
        chat_id = LOG_GROUP
        message = await asst.send_message(
            chat_id, text, disable_web_page_preview=True, disable_notification=True
        )
        return message

    async def download_audio(self, song):
        group_call = self.group_call
        client = group_call.client
        raw_file = os.path.join(client.workdir, DEFAULT_DOWNLOAD_DIR, f"{song[5]}.raw")
        # if os.path.exists(raw_file):
        # os.remove(raw_file)
        if not os.path.isfile(raw_file):
            # credits: https://t.me/c/1480232458/6825
            # os.mkfifo(raw_file)
            if song[3] == "telegram":
                original_file = await bot.download_media(f"{song[2]}")
            elif song[3] == "youtube":
                url = song[2]
                try:
                    info = ydl.extract_info(url, False)
                    ydl.download([url])
                    original_file = path.join(
                        "downloads", f"{info['id']}.{info['ext']}"
                    )
                except Exception as e:
                    playlist.pop(1)
                    print(f"Unable to download due to {e} and skipped.")
                    if len(playlist) == 1:
                        return
                    await self.download_audio(playlist[1])
                    return
            else:
                original_file = wget.download(song[2])
            ffmpeg.input(original_file).output(
                raw_file,
                format="s16le",
                acodec="pcm_s16le",
                ac=2,
                ar="48k",
                loglevel="error",
            ).overwrite_output().run()
            GET_FILE[song[2]] = original_file
            # os.remove(original_file)

    async def start_radio(self, chat_id):
        group_call = self.group_call
        if group_call.is_connected:
            playlist.clear()
        process = FFMPEG_PROCESSES.get(chat_id)
        if process:
            try:
                process.send_signal(SIGINT)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(e)
            FFMPEG_PROCESSES[chat_id] = ""
        station_stream_url = STREAM_URL
        try:
            RADIO.remove(0)
        except BaseException:
            pass
        try:
            RADIO.add(1)
        except BaseException:
            pass

        if CPLAY:
            await self.c_play(STREAM_URL)
            return
        try:
            RADIO.remove(3)
        except BaseException:
            pass
        if os.path.exists(f"radio-{chat_id}.raw"):
            os.remove(f"radio-{chat_id}.raw")
        if not CALL_STATUS.get(chat_id):
            await self.start_call(chat_id)
        ffmpeg_log = open("ffmpeg.log", "w+")
        command = [
            "ffmpeg",
            "-y",
            "-i",
            station_stream_url,
            "-f",
            "s16le",
            "-ac",
            "2",
            "-ar",
            "48000",
            "-acodec",
            "pcm_s16le",
            f"radio-{chat_id}.raw",
        ]

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=ffmpeg_log,
            stderr=asyncio.subprocess.STDOUT,
        )

        FFMPEG_PROCESSES[chat_id] = process
        if RADIO_TITLE:
            await self.edit_title()
        await sleep(2)
        while not os.path.isfile(f"radio-{chat_id}.raw"):
            await sleep(1)
        group_call.input_filename = f"radio-{chat_id}.raw"
        while True:
            if CALL_STATUS.get(chat_id):
                print("Succesfully Joined")
                break
            else:
                print("Connecting...")
                await self.start_call(chat_id)
                await sleep(1)
                continue

    async def stop_radio(self, chat_id):
        group_call = self.group_call
        if group_call:
            playlist.clear()
            group_call.input_filename = ""
            try:
                RADIO.remove(1)
            except BaseException:
                pass
            try:
                RADIO.add(0)
            except BaseException:
                pass
        process = FFMPEG_PROCESSES.get(chat_id)
        if process:
            try:
                process.send_signal(SIGINT)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(e)
            FFMPEG_PROCESSES[chat_id] = ""

    async def start_call(self, chat_id):
        group_call = self.group_call
        try:
            await group_call.start(chat_id)
        except RuntimeError:
            """
            await USER.send(
                CreateGroupCall(
                    peer=(await USER.resolve_peer(chat_id)),
                    random_id=randint(10000, 999999999),
                )
            )
            """
            # TODO
            await group_call.start(chat_id)
        except Exception as e:
            print(e)

    # TODO
    # async def edit_title(self):
    #     if not playlist:
    #         title = RADIO_TITLE
    #     else:
    #         pl = playlist[0]
    #         title = pl[1]
    #     call = InputGroupCall(
    #         id=self.group_call.group_call.id,
    #         access_hash=self.group_call.group_call.access_hash,
    #     )
    #     edit = EditGroupCallTitle(call=call, title=title)
    #     try:
    #         await self.group_call.client.send(edit)
    #     except Exception as e:
    #         print("Errors Occured while editing title", e)

    async def delete(self, event):
        await sleep(DELAY)
        try:
            await event.delete()
        except BaseException:
            pass

    async def get_admins(self, chat):
        admins = ADMIN_LIST.get(chat)
        if not admins:
            admins = VC_AUTHS()
            try:
                grpadmins = await vcClient.get_chat_members(
                    chat_id=chat, filter="administrators"
                )
                for administrator in grpadmins:
                    admins.append(administrator.user.id)
            except Exception as e:
                print(e)
            ADMIN_LIST[chat] = admins
        return admins

    async def shuffle_playlist(self):
        v = []
        [v.append(playlist[c]) for c in range(2, len(playlist))]
        random.shuffle(v)
        for c in range(2, len(playlist)):
            playlist.remove(playlist[c])
            playlist.insert(c, v[c - 2])

    async def c_play(self, channel):  # sourcery no-metrics
        if 1 in RADIO:
            await self.stop_radio(channel)
        channel = int(channel) if channel.startswith("-100") else channel
        try:
            chat = await asst.get_entity(channel)
            print("Starting Playlist from", chat.title)
            async for m in vcClient.iter_messages(
                chat_id=channel, filter="audio", limit=LIMIT
            ):
                m_audio = await asst.get_messages(channel, m.message_id)
                if round(m_audio.audio.duration / 60) > DURATION_LIMIT:
                    print(
                        f"Skiped {m_audio.audio.file_name} since duration is greater than maximum duration."
                    )
                else:
                    now = datetime.now()
                    nyav = now.strftime("%d-%m-%Y-%H:%M:%S")
                    data = {
                        1: m_audio.audio.title,
                        2: m_audio.audio.file_id,
                        3: "telegram",
                        4: f"[{chat.title}]({m_audio.link})",
                        5: f"{nyav}_{m.message_id}",
                    }
                    playlist.append(data)
                    if len(playlist) == 1:
                        print("Downloading..")
                        await self.download_audio(playlist[0])
                        if not self.group_call.is_connected:
                            await self.start_call(chat.id)
                        file = playlist[0][5]
                        client = self.group_call.client
                        self.group_call.input_filename = os.path.join(
                            client.workdir, DEFAULT_DOWNLOAD_DIR, f"{file}.raw"
                        )
                        print(f"- START PLAYING: {playlist[0][1]}")
                        if EDIT_TITLE:
                            await self.edit_title()
                    for track in playlist[:2]:
                        await self.download_audio(track)
            if not playlist:
                print("No songs Found From Channel, Starting Red FM")
                STREAM_URL = "https://bcovlive-a.akamaihd.net/19b535b7499a4719a5c19e043063f5d9/ap-southeast-1/6034685947001/playlist.m3u8?nocache=825347"
                await self.start_radio(channel)
                return
            else:
                if len(playlist) > 2 and SHUFFLE:
                    await self.shuffle_playlist()
                RADIO.add(3)
                if LOG_GROUP:
                    await self.send_playlist()
        except Exception as e:
            STREAM_URL = "https://bcovlive-a.akamaihd.net/19b535b7499a4719a5c19e043063f5d9/ap-southeast-1/6034685947001/playlist.m3u8?nocache=825347"
            await self.start_radio(channel)
            print("Errorrs Occured\n Starting Red FM", e)


mp = Player()

# pytgcalls handlers


@mp.group_call.on_network_status_changed
async def on_network_changed(call, is_connected):
    chat_id = call.full_chat.id
    CALL_STATUS[chat_id] = bool(is_connected)


@mp.group_call.on_playout_ended
async def playout_ended_handler(_, __):
    if not playlist:
        await mp.start_radio()
    else:
        await mp.skip_current_playing()
