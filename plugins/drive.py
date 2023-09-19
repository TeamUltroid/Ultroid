import os

from utilities.gdrive import GDrive
from utilities.helper import humanbytes

from . import ultroid_cmd

drive = GDrive()


@ultroid_cmd("gdul( (.*)|$)", fullsudo=True)
async def drive_upload_func(event):
    """`{}gdul <path to file/reply to file>` - Upload file from local/telegram to Google Drive."""
    match = event.pattern_match.group(2)
    if not drive.creds.get("access_token"):
        return await event.eor("Please authorise with Gdrive before uploading.")
    reply = await event.get_reply_message()
    xx = await event.eor("`Processing...`")
    if reply:
        if reply.photo:
            file = await event.client.download_media("resources/downloads/")
        else:
            file, _ = await event.client.fast_downloader(
                reply.document, event=xx, show_progress=True
            )
            file = file.name
    elif match:
        file = match
    else:
        return await xx.edit("`Give path to file or reply to a file.`")
    if not os.path.exists(file):
        return await xx.edit(
            f"`{file}` not found in local storage. Check your path again."
        )
    res = await drive.upload_file(xx, file)
    await xx.edit(
        f"`{res['name']}` uploaded to GDrive successfully: {res['webContentLink']}",
        link_preview=False,
    )


@ultroid_cmd("gddl( (.*)|$)", fullsudo=True)
async def drive_download_func(event):
    """`{}gddl <link>` - Download file from Google Drive using link."""
    ...


@ultroid_cmd("gdusg$")
async def drive_usage_func(event):
    """`{}gdusg` - Show total limit and usage of Google Drive storage."""
    if not drive.creds.get("access_token"):
        return await event.eor("Please authorise with Gdrive before using gdrive.")
    size = await drive.get_size_status()
    if "error" in size:
        return await event.eor(f"`{size}`")
    size = size["storageQuota"]
    await event.eor(
        f"`GDrive Usage\n"
        + f"「 Limit: {humanbytes(size['limit'])} 」\n"
        + f"「 Usage: {humanbytes(size['usage'])} 」\n"
        + f"「 Usage in drive: {humanbytes(size['usageInDrive'])} 」\n"
        + f"「 Usage in trash: {humanbytes(size['usageInDriveTrash'])} 」`"
    )


@ultroid_cmd("gdauth( (.*)|$)", fullsudo=True)
async def drive_auth_func(event):
    """`{}gdauth <code>` - To authorise with Google Drive API.
    Args:
        `code` - Code which you get after visiting the link provided by `{}gdauth`"""
    match = event.pattern_match.group(2)
    if not match:
        if not (drive.client_id or drive.client_secret):
            return await event.eor("Fill GDrive credentials before authorisation.")
        return await event.eor(
            f"Visit [this]({drive.get_oauth2_url()}) to get authorisation code."
        )
    creds = await drive.get_access_token(code=match)
    msg = "Authorisation successful."
    if "error" in creds:
        msg = f"`{creds}`"
    await event.eor(msg)


@ultroid_cmd("gdls$", fullsudo=True)
async def drive_list_func(event):
    """`{}gdls` - List all files of Google Drive."""
    x = await event.eor("`Processing...`")
    resp = await drive.list()
    if "error" in resp:
        return await x.edit(f"`{resp}`")
    text = f"Files found: {len(resp['files'])}\n\n"
    for file in resp["files"]:
        text += f"Name: {file['name']}\n"
        text += f"Link: {file['webContentLink']}\n"
        text += f"Size: {file['size']}\n\n"
    if len(text) > 4096:
        with open("drivefiles.txt", "w") as dfiles:
            dfiles.write(text)
        await event.reply(f"Files found: {len(resp['files'])}", file="drivefiles.txt")
        os.remove("drivefiles.txt")
        await x.delete()
    else:
        await x.edit(text, link_preview=False)


@ultroid_cmd("gdmv( (.*)|$)", fullsudo=True)
async def drive_move_func(event):
    """`{}gdmv <file_id> <folder_id>` - Move file to another directory in Google Drive.
    Args:
        `file_id` - File ID or File Link which you want to move.
        `folder_id` - Folder ID or Folder Link where you want to move."""
    ...


@ultroid_cmd("gdcp( (.*)|$)", fullsudo=True)
async def drive_copy_func(event):
    """`{}gdcp <file_id> <folder_id>` - Copy file to another directory in Google Drive.
    Args:
        `file_id` - File ID or File Link which you want to copy.
        `folder_id` - Folder ID or Folder Link where you want to copy."""
    ...


@ultroid_cmd("gdfd( (.*)|$)", fullsudo=True)
async def drive_search_func(event):
    """`{}gdfd <filename>` - Search for specific file in Google Drive.
    Args:
        `filename` - Name of file (case-sensitive)."""
    query = event.pattern_match.group(2)
    if not query:
        return await event.eor("`Give filename to search.`")
    x = await event.eor("`Processing...`")
    resp = await drive.list(query)
    if "error" in resp:
        return await x.edit(f"`{resp}`")
    text = f"Files found: {len(resp['files'])}\n\n"
    for file in resp["files"]:
        text += f"Name: {file['name']}\n"
        text += f"Link: {file['webContentLink']}\n"
        text += f"Size: {file['size']}\n\n"
    if len(text) > 4096:
        with open("drivesearchedfiles.txt", "w") as dfiles:
            dfiles.write(text)
        await event.reply(
            f"Files found: {len(resp['files'])}", file="drivesearchedfiles.txt"
        )
        os.remove("drivesearchedfiles.txt")
        await x.delete()
    else:
        await x.edit(text, link_preview=False)


@ultroid_cmd("gddel( (.*)|$)", fullsudo=True)
async def drive_delete_func(event):
    """`{}gddel <file_id>` - Delete file from Google Drive.
    Args:
        `file_id` - File ID or File Link which you want to move."""
    match = event.pattern_match.group(2)
    if not match:
        return await event.eor("Give FileId which you want to delete from gdrive.")
    res = await drive.delete(match)
    await event.eor(f"`{res}`")
