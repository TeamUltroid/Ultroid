import contextlib
import os, json

from core import rm
from utilities.tools import generate_screenshot, is_url_ok

from .. import LOGS, bash, get_string, mediainfo, ultroid_cmd


@ultroid_cmd(pattern="mediainfo( (.*)|$)")
async def mediainfo_cmd(event):
    r = await event.get_reply_message()
    match = event.pattern_match.group(1).strip()
    extra = ""
    if r and r.media:
        xx = mediainfo(r)
        murl = json.dumps(json.loads(r.media.to_json()), indent=2)
        with rm.get("graph", helper=True, dispose=True) as mod:
            url = await mod.make_html_telegraph("Mediainfo", f"<pre>{murl}</pre>")
        extra = f"**[{xx}]({url})**\n\n"
        e = await event.eor(f"{extra}`Loading More...`", link_preview=False)

        if hasattr(r.media, "document"):
            dl = await event.client.fast_downloader(
                r.document,
                show_progress=True,
                event=event,
                message=f"{extra}`Loading More...`",
            )

            naam = dl[0].name
        else:
            naam = await r.download_media()
    elif match and (
        os.path.isfile(match)
        or (match.startswith("https://") and (await is_url_ok(match)))
    ):
        naam, xx = match, "file"
    else:
        return await event.eor(get_string("cvt_3"), time=5)
    out, er = await bash(f"mediainfo '{naam}'")
    makehtml = ""
    thumb = None
    if naam.endswith((".mkv", ".mp4", ".avi")):
        thumb = await generate_screenshot(naam)
    is_img = naam.endswith((".jpg", ".png"))
    if is_img:
        thumb = naam
    if thumb and os.path.exists(thumb):
        with rm.get("graph", helper=True, dispose=True) as mod:
            med = mod.upload_file(thumb)

        makehtml += f"<img src='{med}'><br>"
    elif is_img:
        makehtml += f"<img src='{match}'><br>"
    for line in out.split("\n"):
        line = line.strip()
        if not line:
            makehtml += "<br>"
        elif ":" not in line:
            makehtml += f"<h3>{line}</h3>"
        else:
            makehtml += f"<p>{line}</p>"
    try:
        with rm.get("graph", helper=True, dispose=True) as mod:
            urll = await mod.make_html_telegraph("Mediainfo", makehtml)
    except Exception:
        LOGS.exception(er)
        return
    await event.eor(f"{extra}[{get_string('mdi_1')}]({urll})", link_preview=False)
    if not match:
        os.remove(naam)
    if thumb and thumb != naam:
        with contextlib.suppress(FileNotFoundError):
            os.remove(thumb)
