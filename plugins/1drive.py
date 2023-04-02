import os

from utilities.onedrive import OneDrive

from . import ultroid_cmd

onedrv = OneDrive()


@ultroid_cmd(pattern="1dul ((.*)|$)")
async def onedrive_upload(event):
    """`{}1dul <path to file/reply to document>` - Upload file from local/telegram to OneDrive`"""
    file = event.pattern_match.group(1)
    if not file:
        return await event.eor("Give me a file to upload")
    # check if file exists
    if not os.path.exists(file):
        return await event.eor("File not found")
    await event.eor("Uploading...")
    status = await onedrv.upload_file(file)
    if status.get("error"):
        return await event.eor(status.get("error"))
    await event.eor(f"Uploaded to OneDrive: [{status.get('name')}]({status.get('shareUrl')})\nTemp Download url [1 hour]: [{status.get('name')}]({status.get('@content.downloadUrl')}).")


@ultroid_cmd(pattern="1ddl ((.*)|$)")
async def onedrive_download(event):
    """`{}1ddl <link>` - Download file from OneDrive using link.`"""
    link = event.pattern_match.group(1)
    if not link:
        return await event.eor("Give me a link to download")
    await event.eor("Downloading...")
    filename = await onedrv.download_file(event, "resources/downloads", link)
    await event.eor(f"Downloaded to `resources/downloads/{filename}`")
