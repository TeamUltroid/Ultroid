import os
import time

from core.remote import rm
from telethon.tl.types import Message

from . import eod, get_string, ultroid_cmd

with rm.get("onedrive", helper=True, dispose=True) as mod:
    onedrv = mod.OneDrive

@ultroid_cmd(pattern="1dauth( (.*)|$)")
async def onedrive_auth(event):
    """`{}1dauth <code>` - To authorise with OneDrive graphql api.
Args:
    `code` - Code which you get after visiting the oauth2 link provided by `{}1dauth`"""
    match = event.pattern_match.group(1)
    odrive = onedrv()
    if not (odrive.client_id and odrive.client_secret):
        return await event.eor("Please set OneDrive credentials before requesting authorisation.")
    if not match:
        return await event.eor(f"Please visit [this]({get_oauth2_url()}) to login and get authorisation code from onedrive.")
    creds = await odrive.get_access_token(code=match)
    msg = "Successfully authorised with onedrive API."
    if "error" in creds:
        msg = f"`{creds}`"
    await event.eor(msg)

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
                return await event.eor(mone, str(e), time=10)
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

    status = await onedrv().upload_file(mone, filename)
    if status.get("error"):
        return await mone.eor(status.get("error"))
    await mone.eor(f"Uploaded to OneDrive: <a href='{status.get('shareUrl')}'>{status.get('name')}</a>\nTemp Download url [1 hour]: <a href='{status.get('@content.downloadUrl')}'>{status.get('name')}</a>.", parse_mode="html")


@ultroid_cmd(pattern="1ddl( (.*)|$)")
async def onedrive_download(event):
    """`{}1ddl <link>` - Download file from OneDrive using link.`"""
    match = event.pattern_match.group(1).strip()
    if not match:
        return await event.eor("Give me a link to download")
    link = match.split(" | ")[0].strip()
    filename = match.split(" | ")[1].strip() if " | " in match else None
    event = await event.eor(get_string("com_1"))
    filename = await onedrv().download_file(event, "resources/downloads", link)
    await event.eor(f"Downloaded to `resources/downloads/{filename}`")
