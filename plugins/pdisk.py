# Ultroid - UserBot
# Copyright (C) 2021 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}pdisk <url> ; <name> ; <description>`
  Upload to pdisk.net from a URL.

• `{i}pdisk <name> ; <description> (reply to file)`
  Upload the replied file to pdisk.net. 
"""

import requests
from . import HNDLR, LOGS, downloader, eor, get_string, ultroid_cmd, udB


@ultroid_cmd(pattern="pdisk")
async def pdisk_uploader(event):
    if udB.get("PDISK_API") is None:
        return await eor(
            event, "Please add your pdisk.net api key via your assistant!", time=10
        )
    t = event.text.split(" ")
    try:
        args = t[1]
    except IndexError:
        return await eor(
            event, "Please check `{}help pdisk` about usage.".format(HNDLR), time=10
        )
    if event.reply_to_msg_id:
        reply = await event.get_replied_message()
        if reply.media or reply.video:
            args = args.split(";")
            try:
                name = args[0]
            except IndexError:
                name = reply.file.name
            try:
                desc = args[1]
            except IndexError:
                desc = "Uploaded using @TheUtroid!"
    else:
        args = args.split(";")
        try:
            url = args[0]
        except IndexError:
            return await eor(
                event, "Please check `{}help pdisk` about usage.".format(HNDLR), time=10
            )
        try:
            name = args[1]
        except IndexError:
            name = "TheUltroid"
        try:
            desc = args[2]
        except IndexError:
            desc = "Uploaded using @TheUtroid!"

    base_url = "http://linkapi.net/open/create_item?api_key={api}&content_src={url}&link_type=link&title={name}&description={desc}"

    if url:
        base_url = base_url.format(
            api=udB.get("PDISK_API"), url=url, name=name, desc=desc
        )
        r = requests.get(base_url).json()
        if not r["data"] and r["msg"] and r["msg"] == "api_key invalid":
            return await eor(event, "Invalid API key provided.", time=10)
        try:
            k = r["data"]["item_id"]
        except IndexError:
            return await eor(event, "Something went wrong!", time=10)
        end_url = "https://cofilink.com/share-video?videoid=" + k
        return await eor(
            event,
            "File from [URL]({url}) has been uploaded to pdisk.net, and can be found [here]({final})!\n`{final}`".format(
                url=url, final=end_url
            ),
            link_preview=False,
        )
    else:
        # download the fking thing, and do the rem stuff
        # TODO: do later
        return
