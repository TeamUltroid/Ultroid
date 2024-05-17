# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}webupload`
    Upload files on another server.
"""

import os, re


from .. import Button, asst, get_string, ultroid_cmd, callback, fetch, in_pattern

_webupload_cache = {}

@ultroid_cmd(
    pattern="webupload( (.*)|$)",
)
async def _(event):
    xx = await event.eor(get_string("com_1"))
    match = event.pattern_match.group(1).strip()
    if event.chat_id not in _webupload_cache:
        _webupload_cache.update({int(event.chat_id): {}})
    if match:
        if not os.path.exists(match):
            return await xx.eor("`File doesn't exist.`")
        _webupload_cache[event.chat_id][event.id] = match
    elif event.reply_to_msg_id:
        reply = await event.get_reply_message()
        if reply.photo:
            file = await reply.download_media("resources/downloads/")
            _webupload_cache[int(event.chat_id)][int(event.id)] = file
        else:
            file, _ = await event.client.fast_downloader(
                reply.document, show_progress=True, event=xx
            )
            _webupload_cache[int(event.chat_id)][int(event.id)] = file.name
    else:
        return await xx.eor("`Reply to file or give file path...`")
    if not event.client._bot:
        results = await event.client.inline_query(
            asst.me.username, f"fl2lnk {event.chat_id}:{event.id}"
        )
        await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
        await xx.delete()

    else:
        __cache = f"{event.chat_id}:{event.id}"
        buttons = [
            [
                Button.inline("anonfiles", data=f"flanonfiles//{__cache}"),
                Button.inline("transfer", data=f"fltransfer//{__cache}"),
            ],
            [
                Button.inline("bayfiles", data=f"flbayfiles//{__cache}"),
                Button.inline("x0.at", data=f"flx0.at//{__cache}"),
            ],
            [
                Button.inline("file.io", data=f"flfile.io//{__cache}"),
                Button.inline("siasky", data=f"flsiasky//{__cache}"),
            ],
        ]
        await xx.edit("**Choose Server to Upload File...**", buttons=buttons)


@callback(
    re.compile(
        "fl(.*)",
    ),
    owner=True,
)
async def _(e):
    t = (e.data).decode("UTF-8")
    data = t[2:]
    host = data.split("//")[0]
    chat_id, msg_id = data.split("//")[1].split(":")
    filename = _webupload_cache[int(chat_id)][int(msg_id)]
    if "/" in filename:
        filename = filename.split("/")[-1]
    await e.edit(f"Uploading `{filename}` on {host}")
    link = (await webuploader(chat_id, msg_id, host)).strip().replace("\n", "")
    await e.edit(f"Uploaded `{filename}` on {host}.", buttons=Button.url("View", link))


@in_pattern("fl2lnk ?(.*)", owner=True)
async def _(e):
    match = e.pattern_match.group(1)
    chat_id, msg_id = match.split(":")
    filename = _webupload_cache[int(chat_id)][int(msg_id)]
    if "/" in filename:
        filename = filename.split("/")[-1]
    __cache = f"{chat_id}:{msg_id}"
    buttons = [
        [
            Button.inline("anonfiles", data=f"flanonfiles//{__cache}"),
            Button.inline("transfer", data=f"fltransfer//{__cache}"),
        ],
        [
            Button.inline("bayfiles", data=f"flbayfiles//{__cache}"),
            Button.inline("x0.at", data=f"flx0.at//{__cache}"),
        ],
        [
            Button.inline("file.io", data=f"flfile.io//{__cache}"),
            Button.inline("siasky", data=f"flsiasky//{__cache}"),
        ],
    ]
    try:
        lnk = [
            await e.builder.article(
                title=f"Upload {filename}",
                text=f"**File:**\n{filename}",
                buttons=buttons,
            )
        ]
    except BaseException as er:
        LOGS.exception(er)
        lnk = [
            await e.builder.article(
                title="fl2lnk",
                text="File not found",
            )
        ]
    await e.answer(lnk, switch_pm="File to Link.", switch_pm_param="start")


async def webuploader(chat_id: int, msg_id: int, uploader: str):
    file = _webupload_cache[int(chat_id)][int(msg_id)] # nq
    sites = {
        "anonfiles": {"url": "https://api.anonfiles.com/upload", "json": True},
        "siasky": {"url": "https://siasky.net/skynet/skyfile", "json": True},
        "file.io": {"url": "https://file.io", "json": True},
        "bayfiles": {"url": "https://api.bayfiles.com/upload", "json": True},
        "x0.at": {"url": "https://x0.at/", "json": False},
        "transfer": {"url": "https://transfer.sh", "json": False},
    }
    if uploader and uploader in sites:
        url = sites[uploader]["url"]
        json = sites[uploader]["json"]
    with open(file, "rb") as data:
        # todo: add progress bar
        status = await fetch(
            url, data={"file": data.read()}, method="POST", re_json=json
        )
    if isinstance(status, dict):
        if "skylink" in status:
            return f"https://siasky.net/{status['skylink']}"
        if status["status"] == 200 or status["status"] is True:
            try:
                link = status["link"]
            except KeyError:
                link = status["data"]["file"]["url"]["short"]
            return link
    del _webupload_cache[chat_id][msg_id]
    return status

