# < Source - t.me/testingpluginnn >
# < https://github.com/TeamUltroid/Ultroid >

"""
✘ Unduh lagu, daftar putar, album dari Spotify!
• menggunakan -yt = hasil yang lebih baik
• Daftar putar akan diunggah di Grup Log!

✘ **CMD:**
>>  `{i}spotify <song name>`
>>  `{i}spotify -yt <song / playlist link>`
"""

import os
from uuid import uuid4

from telethon.tl.types import DocumentAttributeAudio
from pyUltroid.fns.tools import metadata

from . import *

try:
    import spotdl
except:
    # Can be added in requirements [Addons repo]
    os.system("pip install spotdl")

TEMP_DIR = "resources/spotify"
UL_TXT = "**Mengunggah {0}/{1}** \n»» `{2}!`"


def list_dir(folder):
    to_del = ".spotdl-cache"
    dir = os.listdir(folder)
    if to_del in dir:
        dir.remove(to_del)
    return [os.path.join(folder, i) for i in dir]


async def get_attrs(path):
    if os.path.getsize(path) > 10*1024*1024:
        minfo = await metadata(path)
        return [DocumentAttributeAudio(
            duration=minfo["duration"],
            title=minfo["title"],
            performer=minfo["performer"],
        )]
    return []


@ultroid_cmd(
    pattern="spot(?:dl|ify)(?: (-yt)?|$)(.*)"
)
async def spotify_dl(e):
    chk_yt = bool(e.pattern_match.group(1))
    args = e.pattern_match.group(2)
    reply = await e.get_reply_message()
    if not args:
        if reply and reply.text:
            args = reply.text
        else:
            return await e.eor("Beri nama Lagu juga;", time=5)

    dls = os.path.join(TEMP_DIR, str(uuid4().hex)[:8])
    if not os.path.isdir(dls):
        os.makedirs(dls)
    eris = await e.eor("`Cari di spotify! Harap tunggu`")
    cmd = f"""spotdl "{args}" -o "{dls}" --ignore-ffmpeg-version --dt 20 --st 20"""
    cmd += " --use-youtube" if chk_yt else ""
    await bash(cmd)
    await asyncio.sleep(2)
    files = list_dir(dls)
    if not files:
        return await eris.eor(f"**Tidak ada hasil untuk:**  `{args}`", time=30)
    # Less spammy, incase of Playlists
    chat_id = int(udB.get_key("LOG_CHANNEL")) if len(files) > 8 else e.chat_id
    for count, i in enumerate(files, start=1):
        fn = os.path.basename(i)
        await eris.edit(UL_TXT.format(count, len(files), fn))
        attr = await get_attrs(i)
        size = humanbytes(os.path.getsize(i))
        uls = await e.client.fast_uploader(i, show_progress=False, to_delete=True)
        if not uls:
            LOGS.error(f"Terjadi kesalahan saat mengunggah: {i}")
            continue
        await e.client.send_file(chat_id, uls[0],
            caption=f"`{fn}` – [ `{size}` ]", silent=True,
            attributes=attr, supports_streaming=True)
        await asyncio.sleep(5)
    await eris.eor(f"**Diunggah {len(files)} Lagu!**", time=20)
