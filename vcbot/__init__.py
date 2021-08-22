from os import remove

from pyUltroid import LOGS, CallsClient, asst, udB
from pyUltroid.dB.core import ACTIVE_CALLS
from pyUltroid.functions.all import bash, dler, time_formatter
from pyUltroid.misc import sudoers
from pyUltroid.misc._wrappers import eod, eor
from telethon import events
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch

_yt_base_url = "https://www.youtube.com/watch?v="
asstUserName = asst.me.username


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
    ytdl_data = await dler(event, link)
    YoutubeDL(opts).download([link])
    dl = vid_id + ".mp3"
    title = ytdl_data["title"]
    duration = ytdl_data["duration"]
    thumb = f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg"
    await bash(f"ffmpeg -i {dl} -f s16le -ac 2 -ar 48000 -acodec pcm_s16le {song}")
    try:
        remove(dl)
    except BaseException:
        pass
    return song, thumb, title, duration


def vc_asst(dec):
    def ult(func):
        pattern = "^/" + dec
        asst.add_event_handler(
            func,
            events.NewMessage(incoming=True, pattern=pattern, from_users=VC_AUTHS()),
        )
        asst.add_event_handler(
            func,
            events.NewMessage(
                incoming=True,
                pattern=pattern + "@" + asstUserName,
                from_users=VC_AUTHS(),
            ),
        )

    return ult


# --------------------------------------------------


class Player(object):
    def __init__(self):
        self.group_call = CallsClient.get_file_group_call()

    async def startCall(self, chat):
        if chat not in ACTIVE_CALLS:
            try:
                await self.group_call.start(chat)
            except Exception as e:
                return False, e
        return True, None


ultSongs = Player()


async def vc_joiner(event, chat_id):
    chat = chat_id  # TODO - channel, remote joins
    done, err = await ultSongs.startCall(chat)
    if done:
        await eor(event, "Joined VC in {}".format(chat))
        return True
    else:
        await eor(event, "**ERROR:**\n{}".format(err))
        return False


@ultSongs.group_call.on_network_status_changed
async def on_network_changed(call, is_connected):
    chat = call.full_chat.id
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


@ultSongs.group_call.on_playout_ended
async def playout_ended_handler(call, __):
    try:
        remove(call._GroupCallFile__input_filename)
    except BaseException:
        pass
    # play the next song in queue
    # if queue is empty, then leave vc
    # TODO
    call.stop_playout()
