import os
import time

from core.remote import rm
from telethon.tl.types import Message

from . import ultroid_cmd

with rm.get("onedrive", helper=True, dispose=True) as mod:
    onedrv = mod.OneDrive


@ultroid_cmd(pattern="1dul( (.*)|$)")
async def onedrive_upload(event):
    """`{}1dul <path to file/reply to document>` - Upload file from local/telegram to OneDrive`"""
    file = event.pattern_match.group(1).strip() or await event.get_reply_message()
    if not file:
        return await event.eor("Give me a file to upload")
    mone = await event.eor(get_string("com_1"))
    if isinstance(file, Message):
        location = "resources/downloads"
        if file.photo:
            filename = await file.download_media(location)
        else:
            filename = file.file.name
            if not filename:
                filename = str(round(time.time()))
            filename = f"{location}/{filename}"
            try:
                filename, downloaded_in = await event.client.fast_downloader(
                    file=file.media.document,
                    filename=filename,
                    show_progress=True,
                    event=mone,
                    message=get_string("com_5"),
                )
                filename = filename.name
            except BaseException:
                return await eor(mone, str(e), time=10)
        await mone.edit(
            f"`Downloaded to ``{filename}`.`",
        )
    else:
        filename = file.strip()
        if not os.path.exists(filename):
            return await eod(
                mone,
                "File Not found in local server. Give me a file path :((",
                time=5,
            )

    await event.eor("Uploading...")
    status = await onedrv().upload_file(file)
    if status.get("error"):
        return await event.eor(status.get("error"))
    await event.eor(f"Uploaded to OneDrive: [{status.get('name')}]({status.get('shareUrl')})\nTemp Download url [1 hour]: [{status.get('name')}]({status.get('@content.downloadUrl')}).")


@ultroid_cmd(pattern="1ddl( (.*)|$)")
async def onedrive_download(event):
    """`{}1ddl <link>` - Download file from OneDrive using link.`"""
    link = event.pattern_match.group(
        2) if event.pattern_match.group(1) else None
    if not link:
        return await event.eor("Give me a link to download")
    await event.eor("Downloading...")
    filename = await onedrv().download_file(event, "resources/downloads", link)
    await event.eor(f"Downloaded to `resources/downloads/{filename}`")
