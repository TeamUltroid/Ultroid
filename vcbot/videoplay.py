# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available

`{i}videoplay <song name/url/m3u8 links/reply to video>`
   Stream Videos in chat.
   you can use remotely too
   like `{i}videoplay @chat <input/reply>`

"""


import requests
from requests.exceptions import MissingSchema

from . import *


@vc_asst("videoplay")
async def video_c(event):
    xx = await eor(event, get_string("com_1"))
    chat = event.chat_id
    from_user = inline_mention(event.sender)
    reply, song = None, None
    if event.reply_to:
        reply = await event.get_reply_message()
    if len(event.text.split()) > 1:
        input = event.text.split(maxsplit=1)[1]
        tiny_input = input.split()[0]
        if tiny_input.startswith("@"):
            try:
                chat = int("-100" + str(await get_user_id(tiny_input, client=vcClient)))
                song = input.split(maxsplit=1)[1]
            except IndexError:
                pass
            except Exception as e:
                return await eor(event, str(e))
        elif tiny_input.startswith("-"):
            chat = int(
                "-100" + str(await get_user_id(int(tiny_input), client=vcClient))
            )
            try:
                song = input.split(maxsplit=1)[1]
            except BaseException:
                pass
        else:
            song = input
    if not (reply or song):
        return await eor(
            xx, "Please specify a song name or reply to a video file !", time=5
        )
    await eor(xx, "`Downloading and converting...`")
    if reply and reply.media and mediainfo(reply.media).startswith("video"):
        song, thumb, title, link, duration = await file_download(xx, reply)
    else:
        try:
            requests.get(song)
            is_link = True
        except MissingSchema:
            is_link = None
        except BaseException:
            is_link = False
        if not is_link:
            return await eor(xx, f"`{song}`\n\nNot a playable link.🥱")
        if is_link is None:
            song, thumb, title, link, duration = await vid_download(song)
        elif re.search("youtube", song) or re.search("youtu", song):
            song, thumb, title, link, duration = await vid_download(song)
        else:
            song, thumb, title, link, duration = (
                song,
                "https://telegra.ph/file/22bb2349da20c7524e4db.mp4",
                song,
                song,
                "♾",
            )
    ultSongs = Player(chat, xx, True)
    if not (await ultSongs.vc_joiner()):
        return
    await xx.reply(
        "🎸 **Now playing:** [{}]({})\n⏰ **Duration:** `{}`\n👥 **Chat:** `{}`\n🙋‍♂ **Requested by:** {}".format(
            title, link, duration, chat, from_user
        ),
        file=thumb,
        link_preview=False,
    )
    await asyncio.sleep(1)
    await ultSongs.group_call.start_video(song, with_audio=True)
    await xx.delete()
