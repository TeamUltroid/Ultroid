# Ultroid - UserBot
# Instagram Downloader Plugin
#
# This file is part of < https://github.com/TeamUltroid/Ultroid/ >
# Please read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}ig <instagram link>`
   Download reels/videos/photos/carousels from Instagram.

"""

import glob
import os
import time
import asyncio
from yt_dlp import YoutubeDL

from pyUltroid import LOGS
from pyUltroid.fns.helper import humanbytes, run_async, time_formatter
from pyUltroid.fns.tools import set_attributes
from . import ultroid_cmd


# ----------- Progress Handler -----------

async def ig_progress(data, start_time, event):
    if data["status"] == "error":
        return await event.edit("**[X] Error while downloading.**")

    if data["status"] == "downloading":
        txt = (
            "**Downloading from Instagram...**\n\n"
            f"**File:** `{data.get('filename','')}`\n"
            f"**Total:** `{humanbytes(data.get('total_bytes', 0))}`\n"
            f"**Done:** `{humanbytes(data.get('downloaded_bytes', 0))}`\n"
            f"**Speed:** `{humanbytes(data.get('speed', 0))}/s`\n"
            f"**ETA:** `{time_formatter(data.get('eta', 0) * 1000)}`"
        )

        # update every 10 seconds
        if round((time.time() - start_time) % 10) == 0:
            try:
                await event.edit(txt)
            except:
                pass


# ----------- Instagram Extraction -----------

@run_async
def _download_ig(url, opts):
    try:
        return YoutubeDL(opts).extract_info(url=url, download=True)
    except Exception as e:
        LOGS.error(f"IG Download Error: {e}")
        return None


# ----------- IG Handler -----------

async def insta_downloader(event, url):
    msg = await event.eor("`Fetching Instagram media...`")
    reply_to = event.reply_to_msg_id or event

    opts = {
        "quiet": True,
        "prefer_ffmpeg": True,
        "geo-bypass": True,
        "nocheckcertificate": True,
        "outtmpl": "%(id)s.%(ext)s",
        "progress_hooks": [lambda d: asyncio.create_task(ig_progress(d, time.time(), msg))],
    }

    info = await _download_ig(url, opts)
    if not info:
        return await msg.edit("**[X] Failed to fetch Instagram media.**")

    # Playlist = carousel
    if info.get("_type") == "playlist":
        entries = info.get("entries", [])
    else:
        entries = [info]

    await msg.edit(f"**Downloading {len(entries)} media...**")

    for idx, media in enumerate(entries, start=1):
        media_id = media.get("id")
        title = media.get("title") or "Instagram_Media"

        if len(title) > 30:
            title = title[:27] + "..."

        # Find downloaded file from yt-dlp
        media_path = None
        for f in glob.glob(f"{media_id}*"):
            if not f.endswith(".jpg"):
                media_path = f
                break

        if not media_path:
            continue

        # Rename file
        ext = "." + media_path.split(".")[-1]
        final_name = f"{title}{ext}"

        try:
            os.rename(media_path, final_name)
        except:
            final_name = media_path

        attributes = await set_attributes(final_name)

        uploaded, _ = await event.client.fast_uploader(
            final_name, show_progress=True, event=msg, to_delete=True
        )

        await event.client.send_file(
            event.chat_id,
            file=uploaded,
            caption=f"**Instagram Media**\n`[{idx}/{len(entries)}]`",
            attributes=attributes,
            supports_streaming=True,
            reply_to=reply_to,
        )

    await msg.edit("**Instagram Download Complete.**")


# ----------- Command Handler -----------

@ultroid_cmd(
    pattern="ig ?(.*)",
    category="Media"
)
async def _insta_cmd(event):
    url = event.pattern_match.group(1).strip()

    if not url:
        return await event.eor("**Usage:** `.ig <instagram link>`")

    if "instagram.com" not in url:
        return await event.eor("**[X] Invalid Instagram link.**")

    await insta_downloader(event, url)
