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

• `{i}storydl <username/reply user/story link>`
    Download and upload user stories or specific story from link!
"""

import os
import re
from contextlib import suppress
from . import ultroid_cmd, get_string, LOGS

from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import User, UserFull, InputPeerSelf, InputPrivacyValueAllowAll, Channel, InputUserSelf
from telethon.tl.functions.stories import SendStoryRequest, GetStoriesByIDRequest
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
    message = await event.eor(get_string("com_1"))
    
    try:
        text_input = event.text.split(maxsplit=1)[1]
        # Check if input is a Telegram story link
        story_link_pattern = r"https?://t\.me/([^/]+)/s/(\d+)"
        match = re.match(story_link_pattern, text_input)
        
        if match:
            # Extract username and story ID from link
            username = match.group(1)
            story_id = int(match.group(2))
            
            try:
                # Get the entity for the username
                entity = await event.client.get_entity(username)
                
                # Using GetStoriesByIDRequest to fetch the specific story
                stories_response = await event.client(
                    GetStoriesByIDRequest(
                        entity.id,
                        id=[story_id]
                    )
                )
                print(stories_response)
                
                if not stories_response.stories:
                    return await message.eor("ERROR: Story not found or expired!")

                # Download and upload the story
                for story in stories_response.stories:
                    client: TelegramClient = event.client
                    file = await client.download_media(story.media)
                    caption = story.caption if hasattr(story, 'caption') else ""
                    await message.reply(
                        caption,
                        file=file
                    )
                    os.remove(file)
                
                return await message.eor("**Uploaded Story!**", time=5)

            except Exception as er:
                await message.eor(f"ERROR while fetching story: __{er}__")
                LOGS.exception(er)
                return
        
        # If not a story link, proceed with the original functionality
        username = text_input
        
    except IndexError as er:
        LOGS.exception
        if replied and isinstance(replied.sender, User):
            username = replied.sender_id
        else:
            return await message.eor(
                "Please reply to a user, provide username or story link!"
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
        await message.eor(f"ERROR: __{er}__")
        return

    if not (stories and stories.stories):
        await message.eor("ERROR: Stories not found!")
        return
    for story in stories.stories[:5]:
        client: TelegramClient = event.client
        file = await client.download_media(story.media)
        caption = story.caption if hasattr(story, 'caption') else ""
        await message.reply(
            caption,
            file=file
        )
        os.remove(file)

    await message.eor("**Uploaded Stories!**", time=5)