# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available
"""

from . import *


def on_converter(link, song):
    subprocess.Popen(
        [
            "ffmpeg",
            "-i",
            link,
            "-vn",
            "-f",
            "s16le",
            "-ac",
            "2",
            "-ar",
            "48000",
            "-acodec",
            "pcm_s16le",
            "-filter:a",
            "atempo=1",
            song,
            "-y",
        ],
        stdin=None,
        stdout=None,
        stderr=None,
        cwd=None,
    )


@vc_asst("vidstream")
async def video_c(ult):
    try:
        match = ult.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await eor(ult, "`Give link to play...`")
    file = "vcbot/downloads/" + str(ult.chat_id) + ".raw"
    on_converter(match, file)
    await asyncio.sleep(3)
    if not os.path.exists(file):
        return await eor(ult, "Unplayable Link")
    ultSongs = Player(ult.chat_id, ult, True)
    if not (await ultSongs.vc_joiner()):
        return
    ultSongs.group_call.input_filename = file
    await ultSongs.group_call.set_video_capture(match)
    await eor(ult, f"Playing {match}")
