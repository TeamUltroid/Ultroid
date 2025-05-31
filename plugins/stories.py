# Ultroid - UserBot
# Copyright (C) 2021-2023 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}setstory <reply media>`
    Set replied media as your story.

• `{i}storydl <username/reply user>`
    Download and upload user stories!
"""

import os
from contextlib import suppress
from . import ultroid_cmd, get_string, LOGS

from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import User, UserFull, InputPeerSelf, InputPrivacyValueAllowAll, Channel
from telethon.tl.functions.stories import SendStoryRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.events import NewMessage


@ultroid_cmd("setstory")
async def setStory(event: NewMessage.Event):
    reply = await event.get_reply_message()
    if not (reply and (reply.photo or reply.video)):
        await event.eor("Please reply to a photo or video!", time=5)
        return
    msg = await event.eor(get_string("com_1"))
    try:
        await event.client(
        SendStoryRequest(
            InputPeerSelf(),
            reply.media,
            privacy_rules=[
             InputPrivacyValueAllowAll()   
            ]
        )
    )
        await msg.eor("🔥 **Story is Live!**", time=5)
    except Exception as er:
        await msg.edit(f"__ERROR: {er}__")
        LOGS.exception(er)


@ultroid_cmd("storydl")
async def downloadUserStories(event: NewMessage.Event):
    replied = await event.get_reply_message()
    await event.eor(get_string("com_1"))
    try:
        username = event.text.split(maxsplit=1)[1]
    except IndexError:
        if replied and isinstance(replied.sender, User):
            username = replied.sender_id
        else:
            return await event.eor(
                "Please reply to a user or provide username!"
                # get_string("story_1")
            )
    with suppress(ValueError):
        username = int(username)
    stories = None
    try:
        entity = await event.client.get_entity(username)
        if isinstance(entity, Channel):
            full_user: UserFull = (
                await event.client(GetFullChannelRequest(entity.id))
            ).full_channel
            stories = full_user.stories
        else:
            full_user: UserFull = (
                await event.client(GetFullUserRequest(id=username))
            ).full_user 
            stories = full_user.stories
    except Exception as er:
        await event.eor(f"ERROR: __{er}__")
        return

    if not (stories and stories.stories):
        await event.eor("ERROR: Stories not found!")
        return
    for story in stories.stories:
        client: TelegramClient = event.client
        file = await client.download_media(story.media)
        await event.reply(
            story.caption,
            file=file
        )
        os.remove(file)
    await event.eor("**Uploaded Stories!**", time=5)